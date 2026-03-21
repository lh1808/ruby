from __future__ import annotations

"""Registry für kausale Learner und Base Learner.
Die Registry kapselt,
- welche kausalen Modelle trainiert werden können,
- wie ein Modell instanziiert wird,
- wie Base Learner (LightGBM/CatBoost) konsistent gebaut werden.
Die Konfiguration bleibt damit schlank; die Factory kümmert sich um die
konkrete Modellinstanziierung."""


from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any

from econml.dml import CausalForestDML, NonParamDML, LinearDML
from econml.dr import DRLearner
from econml.metalearners import SLearner, TLearner, XLearner

from rubin.tuning_optuna import build_base_learner


@dataclass
class ModelContext:
    seed: int = 42
    base_learner_type: str = "lgbm"  # "lgbm" | "catboost"
    # Fixe Standardparameter für Base Learner aus der globalen Konfiguration.
    # Diese werden immer gesetzt und können durch getunte Parameter ergänzt/überschrieben werden.
    base_fixed_params: Dict[str, Any] = field(default_factory=dict)

    # Getunte (oder modell-/rollen-spezifisch gesetzte) Parameter.
    # Struktur: role -> {param: value}
    tuned_params: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def params_for(self, role: str) -> Dict[str, Any]:
        # Zuerst rollen-spezifisch, sonst 'default', sonst leer.
        return dict(self.tuned_params.get(role) or self.tuned_params.get("default") or {})


Factory = Callable[[ModelContext], Any]


class ModelRegistry:
    def __init__(self) -> None:
        self._factories: Dict[str, Factory] = {}

    def register(self, name: str, factory: Factory) -> None:
        self._factories[name] = factory

    def create(self, name: str, ctx: ModelContext) -> Any:
        if name not in self._factories:
            raise KeyError(f"Unbekanntes Modell '{name}'. Registriert: {sorted(self._factories)}")
        return self._factories[name](ctx)

    def list(self) -> List[str]:
        return sorted(self._factories.keys())


def default_registry() -> ModelRegistry:
    """Standard-Registry der verfügbaren kausalen Learner.
Alle Base Learner werden konsistent über `ctx.base_learner_type` und `ctx.tuned_params`
erzeugt."""
    reg = ModelRegistry()

    def _base(ctx: ModelContext, role: str):
        # Wichtig: fixe Defaults aus der Konfiguration immer berücksichtigen.
        # Getunte Werte (rollen-spezifisch) überschreiben bei Schlüsselkonflikten.
        params = dict(ctx.base_fixed_params or {})
        params.update(ctx.params_for(role))

        # Rollen unterscheiden sich in der Zielgröße:
        # - Outcome/Propensity: binär -> Klassifikator
        # - CATE/Final-Modelle: kontinuierlicher Effekt -> Regressor
        task = "regressor" if role in {"model_final", "cate_models"} else "classifier"
        return build_base_learner(ctx.base_learner_type, params, seed=ctx.seed, task=task)

    # DML family
    reg.register(
        "NonParamDML",
        lambda ctx: NonParamDML(
            model_y=_base(ctx, "model_y"),
            model_t=_base(ctx, "model_t"),
            # Das Final-Modell ist frei wählbar und wird optional über R-Loss/R-Score getunt.
            model_final=_base(ctx, "model_final"),
            discrete_treatment=True,
            discrete_outcome=True,
            random_state=ctx.seed,
        ),
    )
    # ParamDML nutzt EconMLs LinearDML, d. h. das Final-Modell nimmt eine lineare
    # CATE-Struktur an. Für nichtlineare parametrische CATE-Schätzung eignet sich
    # NonParamDML besser.
    reg.register(
        "ParamDML",
        lambda ctx: LinearDML(
            model_y=_base(ctx, "model_y"),
            model_t=_base(ctx, "model_t"),
            discrete_treatment=True,
            discrete_outcome=True,
            random_state=ctx.seed,
        ),
    )

    # CausalForestDML kombiniert DML-Residualisierung (mit Nuisance-Modellen für Outcome und
    # Treatment) mit einem Causal Forest als letzter Stufe. Daher werden auch hier Base Learner
    # (model_y, model_t) verwendet. Zusätzlich können Wald-Parameter (z. B. n_estimators,
    # max_depth, honest, subsample_fr) gesetzt werden.
    reg.register(
        "CausalForestDML",
        lambda ctx: CausalForestDML(
            model_y=_base(ctx, "model_y"),
            model_t=_base(ctx, "model_t"),
            discrete_treatment=True,
            discrete_outcome=True,
            random_state=ctx.seed,
            **ctx.params_for("forest"),
        ),
    )

    # DRLearner
    reg.register(
        "DRLearner",
        lambda ctx: DRLearner(
            model_propensity=_base(ctx, "model_propensity"),
            model_regression=_base(ctx, "model_regression"),
            # Final-Modell für die CATE-Schätzung (Regression der DR-Pseudo-Outcomes auf X).
            # Kann optional über R-Loss/R-Score getunt werden.
            model_final=_base(ctx, "model_final"),
            cv=5,
            random_state=ctx.seed,
        ),
    )

    # Meta-learners
    reg.register(
        "XLearner",
        lambda ctx: XLearner(
            models=_base(ctx, "models"),
            cate_models=_base(ctx, "cate_models"),
            propensity_model=_base(ctx, "propensity_model"),
        ),
    )
    reg.register("TLearner", lambda ctx: TLearner(models=_base(ctx, "models")))
    reg.register("SLearner", lambda ctx: SLearner(overall_model=_base(ctx, "overall_model")))

    return reg
