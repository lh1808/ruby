from __future__ import annotations

"""Feature-Selektion für kausale Modellierung.

Unterstützte Methoden
---------------------
- ``lgbm_importance``: LightGBM-Regressor auf Outcome (Y), Gain-Importance.
  Schnell, erfasst prädiktive Relevanz für das Outcome.
- ``lgbm_permutation``: LightGBM-Regressor auf Outcome (Y), Permutation-Importance.
  Robuster als Gain (kein Split-Bias), aber rechenintensiver.
- ``causal_forest``: EconML GRF CausalForest Feature-Importances.
  Erfasst kausale Relevanz (Heterogenität des Treatment-Effekts).
  Nutzt die direkte GRF-Implementierung ohne separates Nuisance-Fitting.

Bei mehreren Methoden werden die Top-X% aus jeder Methode berechnet und
per Union zusammengeführt. Dadurch werden Features behalten, die entweder
prädiktiv wichtig (Outcome) oder kausal relevant (CATE-Heterogenität) sind.
"""

from typing import Dict, Iterable, List, Optional, Tuple
import logging

import numpy as np
import pandas as pd


_logger = logging.getLogger("rubin.feature_selection")


# ---------------------------------------------------------------------------
# Korrelationsfilter
# ---------------------------------------------------------------------------

def remove_highly_correlated_features(
    X: pd.DataFrame,
    correlation_threshold: float = 0.9,
    correlation_methods: Iterable[str] | None = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """Entfernt stark korrelierte numerische Features.

    Für jede Methode (Standard: Pearson + Spearman) wird eine Korrelationsmatrix
    berechnet. Sobald ein Feature in *einer* Methode oberhalb des Schwellwerts
    liegt, wird es als redundant markiert."""
    methods = list(correlation_methods or ["pearson", "spearman"])
    threshold = float(correlation_threshold)

    numeric_cols = X.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    if len(numeric_cols) < 2:
        return X.copy(), []

    to_drop: List[str] = []
    for method in methods:
        corr_matrix = X[numeric_cols].corr(method=method).abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop.extend([column for column in upper.columns if any(upper[column] > threshold)])

    to_drop = sorted(set(to_drop))
    return X.drop(columns=to_drop, errors="ignore"), to_drop


# ---------------------------------------------------------------------------
# Importance-Methoden
# ---------------------------------------------------------------------------

def _lgbm_gain_importance(
    X: pd.DataFrame, Y: np.ndarray, seed: int, n_jobs: int = -1,
) -> pd.Series:
    """LightGBM-Regressor auf Outcome trainieren, Gain-Importance extrahieren."""
    import lightgbm as lgb

    model = lgb.LGBMRegressor(
        n_estimators=200, max_depth=6, num_leaves=31,
        learning_rate=0.1, subsample=0.8, colsample_bytree=0.8,
        min_child_samples=20, random_state=seed, n_jobs=n_jobs, verbose=-1,
    )
    model.fit(X, Y)
    imp = model.feature_importances_
    return pd.Series(imp, index=X.columns, name="lgbm_gain").sort_values(ascending=False)


def _lgbm_permutation_importance(
    X: pd.DataFrame, Y: np.ndarray, seed: int,
    n_repeats: int = 5, n_jobs: int = -1,
) -> pd.Series:
    """LightGBM-Regressor auf Outcome trainieren, Permutation-Importance berechnen."""
    import lightgbm as lgb
    from sklearn.inspection import permutation_importance

    model = lgb.LGBMRegressor(
        n_estimators=200, max_depth=6, num_leaves=31,
        learning_rate=0.1, subsample=0.8, colsample_bytree=0.8,
        min_child_samples=20, random_state=seed, n_jobs=n_jobs, verbose=-1,
    )
    model.fit(X, Y)
    result = permutation_importance(
        model, X, Y, n_repeats=n_repeats, random_state=seed, n_jobs=n_jobs,
    )
    imp = result.importances_mean
    return pd.Series(imp, index=X.columns, name="lgbm_permutation").sort_values(ascending=False)


def _causal_forest_importance(
    X: pd.DataFrame, T: np.ndarray, Y: np.ndarray, seed: int, n_jobs: int = -1,
) -> pd.Series:
    """GRF CausalForest trainieren und Feature-Importances extrahieren.

    Nutzt die einfache GRF-Implementierung aus EconML (``econml.grf.CausalForest``),
    nicht das DML-Wrapper-Modell. Vorteil: kein separates Nuisance-Fitting,
    direkte Schätzung der Treatment-Effekt-Heterogenität über Honest Splitting.

    Wichtig
    -------
    GRF kann keine fehlenden Werte verarbeiten. ``compute_importances()`` prüft
    dies vor dem Aufruf und überspringt diese Methode bei fehlenden Werten
    automatisch. Falls diese Funktion direkt aufgerufen wird, muss der Aufrufer
    sicherstellen, dass X keine NaN enthält.

    X wird intern zu numpy float64 konvertiert, da GRF keine pandas
    category-Dtypes verarbeiten kann (anders als LightGBM)."""
    from econml.grf import CausalForest

    # GRF braucht sauberes numpy float64 — keine DataFrames mit category-Dtypes.
    feature_names = list(X.columns)
    X_np = np.asarray(X, dtype=np.float64)
    T_np = np.asarray(T).ravel()
    Y_np = np.asarray(Y, dtype=np.float64).ravel()

    cf = CausalForest(
        n_estimators=200,
        min_samples_leaf=20,
        random_state=seed,
        n_jobs=n_jobs,
    )
    cf.fit(X_np, T_np, Y_np)

    if hasattr(cf, "feature_importances_"):
        imp = np.asarray(cf.feature_importances_).ravel()
    elif hasattr(cf, "feature_importances"):
        imp_fn = cf.feature_importances
        imp = np.asarray(imp_fn() if callable(imp_fn) else imp_fn).ravel()
    else:
        _logger.warning("GRF CausalForest hat keine feature_importances. Fallback auf Nullen.")
        imp = np.zeros(len(feature_names))

    return pd.Series(imp, index=feature_names, name="causal_forest").sort_values(ascending=False)


# ---------------------------------------------------------------------------
# Top-Prozent + Union
# ---------------------------------------------------------------------------

def _top_pct_features(importance: pd.Series, top_pct: float, n_total: int) -> List[str]:
    """Gibt die Top-X% Features zurück (mindestens 1)."""
    n_keep = max(1, int(np.ceil(top_pct / 100.0 * n_total)))
    return list(importance.sort_values(ascending=False).head(n_keep).index)


def compute_importances(
    methods: List[str],
    X: pd.DataFrame,
    T: np.ndarray,
    Y: np.ndarray,
    seed: int,
    n_jobs: int = -1,
    parallel_methods: bool = False,
) -> Dict[str, pd.Series]:
    """Berechnet Feature-Importances für die angegebenen Methoden.

    Returns
    -------
    Dict mit Methodennamen als Keys und Importance-Serien als Values.

    Parameters
    ----------
    parallel_methods : bool
        Bei True werden unabhängige Methoden parallel ausgeführt (Level 3/4).
        Jede Methode bekommt dann n_jobs=1 für ihren internen Fit, da die
        Parallelisierung auf Methoden-Ebene stattfindet.

    Hinweis
    -------
    Die Methode ``causal_forest`` (GRF) kann keine fehlenden Werte verarbeiten.
    Wenn X fehlende Werte enthält, wird diese Methode automatisch übersprungen
    und eine Warnung ausgegeben. LightGBM-basierte Methoden sind davon nicht
    betroffen, da LightGBM fehlende Werte nativ unterstützt.
    """
    results: Dict[str, pd.Series] = {}
    has_missing = X.isnull().any().any()

    effective_methods = []
    for method in methods:
        if method == "none":
            continue
        if method == "causal_forest" and has_missing:
            n_missing_cols = int(X.isnull().any().sum())
            _logger.warning(
                "Feature-Selektion: Methode 'causal_forest' (GRF) übersprungen – "
                "Daten enthalten fehlende Werte (%d Spalten betroffen). "
                "GRF kann keine fehlenden Werte verarbeiten. "
                "Die übrigen Methoden werden weiterhin berechnet.",
                n_missing_cols,
            )
            continue
        effective_methods.append(method)

    if not effective_methods:
        return results

    def _run_method(method: str, method_n_jobs: int) -> Tuple[str, Optional[pd.Series]]:
        try:
            if method == "lgbm_importance":
                return method, _lgbm_gain_importance(X, Y, seed, n_jobs=method_n_jobs)
            elif method == "lgbm_permutation":
                return method, _lgbm_permutation_importance(X, Y, seed, n_jobs=method_n_jobs)
            elif method == "causal_forest":
                return method, _causal_forest_importance(X, T, Y, seed, n_jobs=method_n_jobs)
            else:
                _logger.warning("Unbekannte Feature-Selection-Methode: '%s', überspringe.", method)
                return method, None
        except Exception:
            _logger.warning("Feature-Importance '%s' fehlgeschlagen.", method, exc_info=True)
            return method, None

    if parallel_methods and len(effective_methods) >= 2:
        # Methoden parallel: jede Methode bekommt weniger Kerne
        import os
        n_cpus = os.cpu_count() or 1
        per_method_jobs = max(1, n_cpus // len(effective_methods))
        _logger.info(
            "Feature-Selektion: %d Methoden parallel (%d Kerne/Methode).",
            len(effective_methods), per_method_jobs,
        )

        # KRITISCH: Alle Module VOR dem Thread-Start importieren.
        # Python's Import-Lock + C-Extension-Loading in parallelen Threads
        # kann zu Deadlocks führen. Pre-Import verhindert das.
        for m in effective_methods:
            try:
                if m in ("lgbm_importance", "lgbm_permutation"):
                    import lightgbm  # noqa: F401
                elif m == "causal_forest":
                    from econml.grf import CausalForest  # noqa: F401
            except ImportError:
                pass  # Fehler wird in _run_method abgefangen

        try:
            from joblib import Parallel, delayed
            method_results = Parallel(n_jobs=len(effective_methods), prefer="threads")(
                delayed(_run_method)(m, per_method_jobs) for m in effective_methods
            )
            for method, imp in method_results:
                if imp is not None:
                    results[method] = imp
            return results
        except Exception:
            _logger.warning("Parallele Feature-Selektion fehlgeschlagen, Fallback sequentiell.", exc_info=True)

    # Sequentiell (Level 1/2 oder Fallback)
    for method in effective_methods:
        _, imp = _run_method(method, n_jobs)
        if imp is not None:
            results[method] = imp

    return results


def select_features_by_importance(
    X: pd.DataFrame,
    importances: Dict[str, pd.Series],
    top_pct: float,
    max_features: Optional[int] = None,
) -> Tuple[pd.DataFrame, List[str], Dict[str, List[str]]]:
    """Wählt Features per Top-Prozent-Union aus allen Importance-Methoden.

    Parameters
    ----------
    X : Feature-DataFrame
    importances : Dict von Methodenname -> Importance-Serie
    top_pct : Prozent der Features, die pro Methode behalten werden
    max_features : Absolute Obergrenze nach Union

    Returns
    -------
    X_filtered : Gefilterter DataFrame
    removed : Liste der entfernten Spaltennamen
    top_per_method : Dict mit den Top-Features pro Methode (für Logging)
    """
    if not importances:
        return X.copy(), [], {}

    n_total = X.shape[1]
    all_keep: set = set()
    top_per_method: Dict[str, List[str]] = {}

    for method_name, imp in importances.items():
        # Nur Features berücksichtigen, die in X vorhanden sind
        imp = imp.reindex(X.columns).dropna()
        if imp.empty:
            continue
        top_features = _top_pct_features(imp, top_pct, n_total)
        top_per_method[method_name] = top_features
        all_keep.update(top_features)
        _logger.info(
            "Feature-Selection '%s': Top-%.0f%% = %d / %d Features.",
            method_name, top_pct, len(top_features), n_total,
        )

    if not all_keep:
        return X.copy(), [], top_per_method

    # Absolute Obergrenze anwenden (nach kombinierter Importance sortieren)
    if max_features is not None and len(all_keep) > int(max_features):
        # Bei Union mehrerer Methoden: mittlere Rank-Position als Tiebreaker
        rank_sum = pd.Series(0.0, index=X.columns)
        for imp in importances.values():
            imp_reindexed = imp.reindex(X.columns).fillna(0.0)
            rank_sum += imp_reindexed.rank(ascending=False)
        ranked = rank_sum.loc[list(all_keep)].sort_values()
        all_keep = set(ranked.head(int(max_features)).index)

    keep_ordered = [c for c in X.columns if c in all_keep]
    removed = [c for c in X.columns if c not in all_keep]

    _logger.info(
        "Feature-Selection Union: %d / %d Features behalten, %d entfernt.",
        len(keep_ordered), n_total, len(removed),
    )

    return X[keep_ordered].copy(), removed, top_per_method


# ---------------------------------------------------------------------------
# Legacy-kompatible Hilfsfunktionen
# ---------------------------------------------------------------------------

def calculate_feature_importance(model, X: pd.DataFrame, T, Y) -> pd.Series:
    """Berechnet Feature-Importance über ein kausales Modell (Legacy-Schnittstelle)."""
    try:
        model.fit(Y, T, X=X)
    except TypeError:
        model.fit(Y, T, X)
    if hasattr(model, "feature_importances_"):
        imps = getattr(model, "feature_importances_")
        return pd.Series(imps, index=X.columns).sort_values(ascending=False)
    if hasattr(model, "model_final_") and hasattr(model.model_final_, "feature_importances_"):
        imps = model.model_final_.feature_importances_
        return pd.Series(imps, index=X.columns).sort_values(ascending=False)
    return pd.Series(dtype=float)


def remove_low_importance_features(
    X: pd.DataFrame,
    importance: pd.Series,
    importance_threshold_pct_of_max: float = 2.0,
    max_features: int | None = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """Entfernt Features unter einem Schwellwert (Legacy-Schnittstelle)."""
    if importance.empty:
        return X, []
    max_imp = float(importance.max())
    keep = importance[importance >= (importance_threshold_pct_of_max / 100.0) * max_imp].index.tolist()
    if max_features is not None and len(keep) > int(max_features):
        keep = importance.loc[keep].sort_values(ascending=False).head(int(max_features)).index.tolist()
    removed = [c for c in X.columns if c not in keep]
    return X[keep].copy(), removed
