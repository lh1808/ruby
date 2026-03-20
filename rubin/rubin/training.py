from __future__ import annotations

"""Training- und Cross-Prediction-Hilfsfunktionen.
Die Analyse-Pipeline benötigt eine einheitliche Routine, um:
- Modelle zu trainieren und
- aus dem Training heraus Cross-Predictions zu erzeugen.
Warum Cross-Predictions?
Bei Uplift-/Causal-Modellen ist eine robuste Evaluation wichtig. Wenn man die
Effekte auf denselben Daten bewertet, auf denen ein Modell trainiert wurde,
werden Kennzahlen (z. B. Qini/AUUC) oft zu optimistisch.
Die hier implementierte Methode nutzt eine K-fache Aufteilung und erzeugt für
jede Beobachtung eine Vorhersage, die aus einem Modell stammt, das diese
Beobachtung nicht gesehen hat.
Hinweis zur Modell-API:
EconML-Modelle bieten typischerweise .effect(X) oder .const_marginal_effect(X).
Für eine möglichst breite Kompatibilität wird beides unterstützt."""

from typing import Any
import copy

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold


def _predict_effect(model: Any, X: pd.DataFrame | np.ndarray) -> np.ndarray:
    """Berechnet Effekte/CATE-Vorhersagen für ein Modell.
Unterstützte Varianten (in Prioritätsreihenfolge):
- model.const_marginal_effect(X)  -- bevorzugt (DML-Familie)
- model.effect(X)                 -- Fallback (Meta-Learner)
Rückgabe:
- Binary Treatment:  1D-Array (n,)
- Multi Treatment:   2D-Array (n, K-1)"""
    if hasattr(model, "const_marginal_effect"):
        pred = model.const_marginal_effect(X)
    elif hasattr(model, "effect"):
        pred = model.effect(X)
    else:
        raise AttributeError(
            "Das Modell unterstützt weder 'const_marginal_effect' noch 'effect'. "
            "Bitte eine kompatible EconML-Implementierung verwenden oder die Funktion erweitern."
        )

    pred = np.asarray(pred)
    # BT: (n,1) -> (n,); MT: (n, K-1) bleibt erhalten.
    if pred.ndim == 2 and pred.shape[1] == 1:
        pred = pred[:, 0]
    return pred.astype(float)


def _n_treatment_arms(T: np.ndarray) -> int:
    """Anzahl der Treatment-Arme (inkl. Control)."""
    return len(np.unique(T))


def is_multi_treatment(T: np.ndarray) -> bool:
    """Prüft, ob mehr als 2 Treatment-Gruppen vorliegen."""
    return _n_treatment_arms(T) > 2


def train_and_crosspredict_bt_bo(
    model: Any,
    X: pd.DataFrame,
    Y: np.ndarray,
    T: np.ndarray,
    n_splits: int,
    model_name: str,
    random_state: int,
    return_train_predictions: bool = True,
) -> pd.DataFrame:
    """Trainiert ein Modell und erzeugt Cross-Predictions für BT/BO und MT/BO.

BT/BO = Binary Treatment / Binary Outcome.
MT/BO = Multi Treatment / Binary Outcome.

Vorgehen:
- StratifiedKFold auf der Kombination aus Treatment und Outcome, damit die
  Grundgruppen (T x Y) pro Fold möglichst stabil bleiben.
- In jedem Fold wird das Modell auf dem Trainingsfold gefittet und für den
  Validierungsfold der CATE geschätzt.

Ergebnis (BT):
  DataFrame mit Spalten: Y, T, Predictions_<model_name>, optional Train_<model_name>
Ergebnis (MT, K Treatment-Arme):
  DataFrame mit Spalten: Y, T, Predictions_<model_name>_T1, ..., Predictions_<model_name>_T{K-1},
  OptimalTreatment_<model_name>, optional Train_<model_name>_T1, ..."""
    if n_splits < 2:
        raise ValueError("n_splits muss >= 2 sein.")

    t_int = np.asarray(T).astype(int)
    y_int = np.asarray(Y).astype(int)
    strata = (pd.Series(t_int).astype(str) + "_" + pd.Series(y_int).astype(str)).to_numpy()
    strata_counts = pd.Series(strata).value_counts(dropna=False)

    effective_splits = int(n_splits)
    if not strata_counts.empty:
        effective_splits = min(effective_splits, int(strata_counts.min()))

    if effective_splits >= 2:
        cv = StratifiedKFold(n_splits=effective_splits, shuffle=True, random_state=random_state)
        split_iter = cv.split(np.zeros(len(X)), strata)
    else:
        fallback_splits = min(int(n_splits), len(X))
        if fallback_splits < 2:
            raise ValueError("Für Cross-Predictions werden mindestens 2 Zeilen benötigt.")
        cv = KFold(n_splits=fallback_splits, shuffle=True, random_state=random_state)
        split_iter = cv.split(np.zeros(len(X)))

    K = _n_treatment_arms(T)
    is_mt = K > 2
    n_effects = K - 1

    if is_mt:
        preds = np.full(shape=(len(X), n_effects), fill_value=np.nan, dtype=float)
    else:
        preds = np.full(shape=(len(X),), fill_value=np.nan, dtype=float)

    for tr_idx, va_idx in split_iter:
        try:
            m = copy.deepcopy(model)
        except Exception as e:
            raise RuntimeError(
                "Das Modell konnte nicht kopiert werden. "
                "Bitte sicherstellen, dass das Modell deepcopy-fähig ist, oder die Trainingsroutine "
                "so erweitern, dass pro Fold eine neue Instanz erzeugt wird."
            ) from e

        X_tr = X.iloc[tr_idx]
        X_va = X.iloc[va_idx]

        m.fit(Y[tr_idx], T[tr_idx], X=X_tr)

        fold_pred = _predict_effect(m, X_va)
        if is_mt:
            preds[va_idx, :] = fold_pred
        else:
            preds[va_idx] = fold_pred

    # Ergebnis-DataFrame bauen
    out = pd.DataFrame({"Y": Y, "T": T})

    if is_mt:
        for k in range(n_effects):
            out[f"Predictions_{model_name}_T{k+1}"] = preds[:, k]
        # Optimale Treatment-Zuweisung: argmax über die K-1 Effekte,
        # aber nur wenn der beste Effekt > 0 ist. Sonst Control (0).
        best_effect = np.nanmax(preds, axis=1)
        best_arm = np.nanargmax(preds, axis=1) + 1  # 1-basiert
        out[f"OptimalTreatment_{model_name}"] = np.where(best_effect > 0, best_arm, 0)
    else:
        out[f"Predictions_{model_name}"] = preds

    if return_train_predictions:
        try:
            m_full = copy.deepcopy(model)
            m_full.fit(Y, T, X=X)
            train_pred = _predict_effect(m_full, X)
            if is_mt:
                for k in range(n_effects):
                    out[f"Train_{model_name}_T{k+1}"] = train_pred[:, k]
            else:
                out[f"Train_{model_name}"] = train_pred
        except Exception:
            if is_mt:
                for k in range(n_effects):
                    out[f"Train_{model_name}_T{k+1}"] = np.nan
            else:
                out[f"Train_{model_name}"] = np.nan
    return out


# ---------------------------------------------------------------------------
# Surrogate-Einzelbaum
# ---------------------------------------------------------------------------

SURROGATE_MODEL_NAME = "SurrogateTree"


class SurrogateTreeWrapper:
    """Wrapper um einen Einzelbaum-Regressor für CATE-kompatible Schnittstelle.

    Der Surrogate-Einzelbaum lernt die CATE-Vorhersagen des Champion-Modells
    nach (Teacher-Learner-Prinzip). Intern wird ein einzelner Baum des
    konfigurierten Base-Learners (LightGBM/CatBoost mit n_estimators=1)
    verwendet. Damit er in der Production-Pipeline wie ein normales
    CATE-Modell gescoret werden kann, stellt dieser Wrapper die
    Methoden ``const_marginal_effect`` und ``effect`` bereit.

    Bei Binary Treatment wird ein einzelner Baum gespeichert (``tree``).
    Bei Multi-Treatment wird pro Treatment-Arm ein eigener Baum trainiert
    (``trees``-Dict), da LightGBM/CatBoost nur 1D-Targets unterstützen.
    """

    _is_surrogate = True

    def __init__(self, tree=None, trees: dict | None = None, champion_name: str = ""):
        self.tree = tree
        self.trees = trees or {}
        self.champion_name = champion_name

    def const_marginal_effect(self, X):
        if self.trees:
            # MT: pro Arm predicten und zu (n, K-1)-Matrix zusammensetzen
            arm_keys = sorted(self.trees.keys())
            preds = np.column_stack([self.trees[k].predict(X) for k in arm_keys])
            return preds
        return self.tree.predict(X)

    def effect(self, X):
        return self.const_marginal_effect(X)
