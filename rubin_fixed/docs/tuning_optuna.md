# Optuna-Tuning der Base Learner

## Ziel
Optimiert werden ausschließlich die **Base Learner** (LightGBM/CatBoost), die innerhalb der kausalen Verfahren verwendet werden.
Das hat zwei Vorteile:

1. Du bekommst konsistente Base Modelle über verschiedene kausale Verfahren hinweg.
2. Das Tuning bleibt vergleichbar und modular, weil die kausalen Wrapper selbst nicht "aufgerissen" werden müssen.

## Wie wird getunt?
- Optuna schlägt Hyperparameter vor.
- Es wird eine CV (Cross Validation) mit `cv_splits` durchgeführt. **Empfehlung:** `cv_splits` sollte dem Wert in `data_processing.cross_validation_splits` entsprechen, damit die Trainingsset-Größen zwischen Tuning und finaler Evaluation konsistent bleiben.
- Als Metrik wird für **Classifier-Tasks** (Nuisance: `model_y`, `model_t`, Propensity) z.B. `roc_auc` verwendet. Für **Regressor-Tasks** (Meta-Learner Outcome: `overall_model`, `models`, `model_regression`) wird automatisch **neg. MSE** als Metrik genutzt.
- Bei **Multi-Treatment** wird für die Propensity-Modelle automatisch `roc_auc_ovr` (One-vs-Rest, gewichtet) statt der binären AUC verwendet, da das Propensity-Modell dann eine Multiclass-Klassifikation durchführt (K Treatment-Gruppen). LightGBM und CatBoost erkennen Multiclass automatisch aus den Trainingsdaten.

### Single-Fold-Tuning
Mit `single_fold: true` wird jeder Trial nur auf **einem** zufälligen Fold evaluiert statt auf allen K. Das ist besonders nützlich bei:

- Großen Datensätzen (lange CV-Läufe)
- Explorativen Analysen (schnelle Iteration wichtiger als maximale Stabilität)
- Hohen Trial-Zahlen (Optuna/TPE gleicht verrauschtere Metriken durch mehr Samples aus)

Der Speedup ist linear: Bei 5 Folds ist Single-Fold 5× schneller.

## Learner-spezifische Trainingsmengen
Viele kausale Learner trainieren nicht auf der vollen Datenmenge:

- **S-Learner**: ein Modell auf allen Daten (Features + Treatment als Feature)
- **T-Learner**: zwei Modelle – eins auf Control, eins auf Treatment
- **X-Learner**: mehrere Modelle (Outcome- und CATE-Modelle) teils gruppenweise

Im Tuning wird daher vor dem CV-Lauf eine **Sampling-Strategie** angewendet:
- Für T-/X-Learner wird balanciert nach `T` gezogen (Control/Treatment), damit die Datenmenge pro Modell realistisch ist.
- Die Skalierung erfolgt über die `learner_data_usage`-Felder.

## Separate Hyperparameter-Sets
Je nach Konfiguration werden getrennte Parameter gesucht:

- `per_learner = false`: identische Tuning-Aufgaben werden über mehrere kausale Verfahren hinweg geteilt
- `per_learner = true`: getrennte Parameter-Sets je kausalem Verfahren
- `per_role = false`: identische Rollen werden zusammengefasst, wenn die Task-Signatur gleich ist
- `per_role = true`: getrennte Parameter-Sets je Rolle innerhalb eines Verfahrens

Das Ergebnis wird in einem JSON-Artefakt gespeichert und beim Modellbau angewendet.

---

## Final-Model-Tuning (R-Loss / R-Score)

Einige Verfahren besitzen zusätzlich ein **Final-Modell**, das die heterogenen Effekte lernt
(z. B. `NonParamDML`, `DRLearner`). Dieses Final-Modell ist typischerweise ein Regressor
(LightGBM/CatBoost). Die DML-Nuisance-Modelle (`model_y`, `model_t`, `model_propensity`) sind
Klassifikatoren, während die Meta-Learner Outcome-Modelle (`overall_model`, `models`,
`model_regression`) ebenfalls Regressoren sind.

Damit das Final-Modell nicht mit den Nuisance-Modellen vermischt wird, gibt es eine separate
Konfigsektion:

```yml
final_model_tuning:
  enabled: true
  n_trials: 30
  cv_splits: 5
  models: [NonParamDML]
  single_fold: false
  max_tuning_rows: 200000
  method: "rscorer"
  fixed_params: {}
```

Wesentliche Punkte:

- Es wird ausschließlich das Final-Modell getunt (Rolle `model_final`).
- Bewertet wird über eine Residuen-basierte Zielfunktion (R-Loss/R-Score).
- Das Tuning läuft **nur einmal pro Run** auf der Trainingsmenge des ersten Cross-Prediction-Folds;
  die Parameter werden anschließend für alle weiteren Folds wiederverwendet ("Locking").

### Modellauswahl (`models`)

Statt alle FMT-fähigen Modelle zu tunen, kann mit `models` gezielt festgelegt werden, welche Modelle optimiert werden:

- `models: null` → alle FMT-fähigen Modelle (NonParamDML, DRLearner) werden getuned
- `models: [NonParamDML]` → nur NonParamDML wird getuned, DRLearner nutzt `fixed_params`
- `models: [NonParamDML, DRLearner]` → beide werden getuned

Das ist nützlich, weil die Kosten pro Trial zwischen den Modellen stark unterschiedlich sind:

- **NonParamDML** verwendet RScorer: 1 Fit pro Trial (Residuen werden vorab berechnet)
- **DRLearner** verwendet score() + CV: K Fits pro Trial (kein RScorer verfügbar)

Man kann z.B. nur NonParamDML tunen und DRLearner mit bewährten festen Parametern laufen lassen.

### Single-Fold für DRLearner (`single_fold`)

Analog zum Base-Learner-Tuning kann mit `single_fold: true` der DRLearner auf nur 1 Fold pro Trial evaluiert werden statt K. Das reduziert die Fits von K×Trials auf 1×Trials. NonParamDML profitiert nicht, da RScorer ohnehin nur 1 Fit benötigt.

### Feste Parameter (`fixed_params`)

Wenn FMT deaktiviert ist oder ein Modell nicht in `models` steht, werden die `fixed_params` direkt als Hyperparameter für `model_final` verwendet. Das ermöglicht eine bewusste Kombination: Tuning für ein Modell, feste Parameter für ein anderes.

## Search Space in der Config

Die Tuning-Ranges können direkt in der YAML definiert werden. Dafür gibt es getrennte Bereiche für

- `tuning.search_space` für die Base Learner der Nuisance-Modelle
- `final_model_tuning.search_space` für das Final-Modell (`model_final`)

Innerhalb jedes Bereichs werden LightGBM und CatBoost getrennt gepflegt:

```yml
tuning:
  enabled: true
  n_trials: 50
  search_space:
    lgbm:
      n_estimators: {type: "int", low: 50, high: 600}
      learning_rate: {type: "float", low: 0.01, high: 0.2, log: true}
      num_leaves: {type: "int", low: 7, high: 40}
      max_depth: {type: "int", low: 3, high: 6}
      min_child_samples: {type: "int", low: 10, high: 150}
      min_child_weight: {type: "float", low: 0.001, high: 10.0, log: true}
      subsample: {type: "float", low: 0.6, high: 1.0}
      subsample_freq: {type: "int", low: 1, high: 7}
      colsample_bytree: {type: "float", low: 0.6, high: 1.0}
      min_split_gain: {type: "float", low: 0.0, high: 1.0}
      reg_alpha: {type: "float", low: 0.00000001, high: 10.0, log: true}
      reg_lambda: {type: "float", low: 0.00000001, high: 10.0, log: true}
    catboost:
      iterations: {type: "int", low: 50, high: 600}
      learning_rate: {type: "float", low: 0.01, high: 0.3, log: true}
      depth: {type: "int", low: 3, high: 6}
      l2_leaf_reg: {type: "float", low: 1.0, high: 20.0, log: true}
      random_strength: {type: "float", low: 0.00000001, high: 10.0, log: true}
      bootstrap_type: {type: "categorical", choices: ["Bayesian", "Bernoulli"]}
      bagging_temperature: {type: "float", low: 0.0, high: 5.0}
      subsample: {type: "float", low: 0.5, high: 1.0}
      rsm: {type: "float", low: 0.5, high: 1.0}
      min_data_in_leaf: {type: "int", low: 1, high: 128}
      leaf_estimation_iterations: {type: "int", low: 1, high: 10}
      border_count: {type: "int", low: 32, high: 255}

final_model_tuning:
  enabled: true
  n_trials: 20
  search_space:
    lgbm:
      n_estimators: {type: "int", low: 50, high: 400}
      learning_rate: {type: "float", low: 0.01, high: 0.15, log: true}
```

Unterstützte Parametertypen:

- `type: "int"`
- `type: "float"`
- `type: "categorical"`

Optionale Felder:

- `log: true` für logarithmische Suche
- `step` für lineare Raster bei numerischen Parametern
- `choices` für kategoriale Parameter

Wenn `search_space` leer bleibt, verwendet rubin weiterhin die internen Standard-Ranges.

Die YAML ist bereits generisch aufgebaut: Du kannst auch weitere gültige LightGBM- oder CatBoost-Parameter ergänzen, solange sie von der jeweiligen sklearn-API akzeptiert werden. Die oben gezeigten Parameter sind nur die vordefinierten Standardräume.

## Task-basiertes Sharing
Die Tuning-Logik arbeitet nicht modellweise, sondern task-basiert.
Dafür wird aus `models_to_train` zunächst ein interner Trainingsplan abgeleitet.
Eine Task wird über folgende Merkmale beschrieben:

- Base-Learner-Familie
- Objective-Familie (`outcome`, `outcome_regression`, `grouped_outcome`, `grouped_outcome_regression`, `propensity`, `pseudo_effect`)
- Estimator-Task (`classifier` oder `regressor`)
- Sample-Scope (`all`, `group_specific_shared_params`, ...)
- Nutzung des Treatment-Features
- Zieltyp (`Y`, `T`, `D`)

Nur wenn diese Signatur identisch ist, wird ein Tuning-Ergebnis geteilt.
Dadurch werden gleiche Aufgaben nur einmal gerechnet, ohne unterschiedliche Lernprobleme künstlich zusammenzuwerfen.

Typische geteilte Aufgaben im Repo:

- `model_y` / `model_t` innerhalb der DML-Familie
- gruppenspezifische Outcome-Modelle von `TLearner` und `XLearner`
- Propensity-Modelle auf allen Daten
- separate Regressions-Tasks für CATE-/Final-Modelle

`per_learner=true` oder `per_role=true` können dieses Sharing gezielt feiner auflösen.

---

## Sonderfall: `CausalForestDML`

`CausalForestDML` besteht aus zwei Teilen:

1) **DML‑Residualisierung** mit Nuisance‑Modellen (`model_y`, `model_t`)  
2) **Causal Forest** als letzte Stufe

Optuna‑Tuning in rubin bezieht sich weiterhin auf die **Base Learner** der Nuisance‑Modelle.
Das heißt: Wenn `tuning.enabled=true`, werden (optional pro Rolle) Hyperparameter für
`model_y` und `model_t` optimiert.

Für die Wald‑Parameter der letzten Stufe nutzt rubin optional die eingebaute EconML‑Methode
`CausalForestDML.tune(...)`. Diese wählt zentrale Wald‑Parameter anhand eines Out‑of‑Sample‑R‑Scores
und setzt sie am Estimator. Danach folgt ein reguläres `fit(...)`.

Die Steuerung erfolgt über `causal_forest.use_econml_tune` und die zugehörigen Parameter
(`forest_fixed_params`, `econml_tune_params`, `tune_max_rows`).


## Persistente Optuna-Studies (SQLite)

### Konfiguration
Du kannst Optuna so konfigurieren, dass eine Study in einer SQLite-Datei gespeichert wird:

```yml
tuning:
  enabled: true
  n_trials: 50
  storage_path: "runs/optuna_studies/baselearner_tuning.db"
  study_name_prefix: "baselearner"
  reuse_study_if_exists: true
  optuna_seed: 42
```

### Warum ist das sinnvoll?
- **Fortsetzen** eines Tunings (z. B. wenn ein Lauf abbricht oder du später mehr Trials hinzufügen willst).
- **Transparenz**: Trial-Historie und beste Parameter lassen sich nachträglich analysieren.
- **Vergleichbarkeit** zwischen Runs.

### Study-Namen
Der Study-Name wird aus Prefix + Kontext zusammengesetzt, z. B.:

`baselearner__lgbm__outcome_regression__regressor__all__with_t__y`

Weitere typische Study-Namen:
- `baselearner__lgbm__outcome__classifier__all__no_t__y` (DML model_y)
- `baselearner__lgbm__propensity__classifier__all__no_t__t` (Propensity, geteilt)
- `baselearner__lgbm__grouped_outcome_regression__regressor__group_specific_shared_params__no_t__y` (TLearner/XLearner)
