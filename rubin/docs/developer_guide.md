# Entwicklerhandbuch – rubin

Dieses Dokument richtet sich an Entwicklerinnen und Entwickler, die **rubin** erweitern oder bestehende Teile umbauen.
Der Fokus liegt auf einer konsistenten Struktur, klaren Zuständigkeiten und stabilen Produktionsartefakten.

## Entwicklungsumgebung einrichten

[Pixi](https://pixi.sh) ist das empfohlene Tool für das Environment-Management.
Es verwaltet Python, conda-forge- und PyPI-Pakete einheitlich und erzeugt ein
reproduzierbares Lockfile (`pixi.lock`).

```bash
# Pixi installieren (einmalig)
curl -fsSL https://pixi.sh/install.sh | bash

# Dev-Environment aufbauen (Tests + Linting)
cd rubin_repo
pixi install -e dev

# Tests ausführen
pixi run test

# Tests mit Coverage
pixi run test-cov

# Linting (Ruff)
pixi run lint

# Auto-Fix für Lint-Fehler
pixi run lint-fix

# Alle verfügbaren Tasks anzeigen
pixi task list
```

**Alternativ (ohne pixi):** `pip install -e ".[dev,shap]"` in einer virtuellen Umgebung.

### Environments

| Environment | Inhalt | Typischer Einsatz |
|---|---|---|
| `default` | Core-Pipeline + SHAP | Training, Evaluation, Reporting |
| `app` | default + Flask | Web-UI starten (`pixi run app`) |
| `dev` | default + pytest + ruff | Entwicklung und CI |

## Grundprinzipien

1. **Analyse ≠ Produktion**  
   Analyse darf experimentieren; Produktion muss stabil sein.

2. **Bundles sind der Vertrag**  
   Produktion arbeitet ausschließlich mit exportierten Artefakten (Bundle-Verzeichnis).

3. **Registries statt verstreuter Sonderlogik**  
   Neue Learner und Modellvarianten werden über `ModelRegistry` angebunden, nicht über zusätzliche `if/else`-Blöcke in den Runnern.

## Projektstruktur

```text
rubin/
  pipelines/
    analysis_pipeline.py
    production_pipeline.py
    data_prep_pipeline.py
  evaluation/
    drtester_plots.py
  explainability/
    shap_uplift.py
    permutation_uplift.py
    segment_analysis.py
    reporting.py
  reporting/
    html_report.py            ← HTML-Report-Generator (analysis_report.html)
  model_registry.py
  model_management.py
  tuning_optuna.py
  training.py
  preprocessing.py
  feature_selection.py
  artifacts.py
  settings.py
  utils/
    data_utils.py
    io_utils.py
    schema_utils.py
    uplift_metrics.py
configs/
docs/
run_analysis.py
run_production.py
run_dataprep.py
run_explain.py
run_promote.py
```

## 1) Neuen kausalen Learner ergänzen

### Ort
`rubin/model_registry.py`

### Vorgehen
1. Implementiere eine Factory-Funktion, die eine Modellinstanz erzeugt.
2. Nutze `ModelContext`, um Base-Learner-Typ, Fixparameter und getunte Rollenparameter zu beziehen.
3. Registriere das Modell im `ModelRegistry`.
4. Ergänze in `rubin/settings.py` den Modellnamen in `SUPPORTED_MODEL_NAMES`, damit Konfigurationen strikt validiert bleiben.
5. Prüfe, ob für das Modell task-basiertes Tuning benötigt wird. Falls ja, ergänze die Rollensignaturen in `rubin/tuning_optuna.py`.
6. **Multi-Treatment-Kompatibilität:** Falls das neue Modell Multi-Treatment nicht unterstützt, ergänze den Modellnamen in `_BT_ONLY_MODELS` in `rubin/settings.py`. `_predict_effect()` erwartet, dass kompatible Modelle bei MT ein 2D-Array (n, K-1) zurückgeben. Bei BT genügt (n,) oder (n, 1).

Beispiel-Skizze:

```python
from rubin.model_registry import ModelRegistry, ModelContext
from rubin.tuning_optuna import build_base_learner

def make_my_learner(ctx: ModelContext):
    base = build_base_learner(
        ctx.base_learner_type,
        {**ctx.base_fixed_params, **ctx.params_for("overall_model")},
        seed=ctx.seed,
        task="classifier",
    )
    return MyLearner(model=base)

registry = ModelRegistry()
registry.register("MyLearner", make_my_learner)
```

Zusätzlich in der YAML:

```yaml
models:
  models_to_train:
    - MyLearner
```

## 2) Neuen Base-Learner ergänzen

### Orte
- `rubin/tuning_optuna.py`
- `rubin/model_registry.py` nutzt denselben Builder indirekt über `build_base_learner(...)`

### Schritte
- Builder-Zweig für Klassifikation und Regression ergänzen
- sinnvolle Default-Search-Spaces hinterlegen
- Search-Space-Dokumentation in `docs/tuning_optuna.md` anpassen
- Beispiel-Konfigurationen aktualisieren

## 3) Neue Metriken ergänzen

Metriken liegen in `rubin/utils/uplift_metrics.py`.

Konventionen:
- Funktionen sind möglichst side-effect-frei
- Inputs und Rückgaben bleiben numerisch und einfach serialisierbar
- neue Metriken sollten in der Analyse-Pipeline sowohl nach MLflow als auch in die JSON-Zusammenfassung geschrieben werden

## 4) Production Pipeline erweitern

Erweiterungen wie zusätzliche Ausgabeformate, Batching oder parallele Verarbeitung gehören nach
`rubin/pipelines/production_pipeline.py` und bei Bedarf in `run_production.py`.

Wichtig:
- keine Trainingslogik in Production
- keine Feature-Selektion in Production
- keine impliziten Schemaänderungen zur Laufzeit

## 5) Task-basiertes Optuna-Tuning

Das Base-Learner-Tuning arbeitet task-basiert. Das bedeutet:

1. aus `models_to_train` wird ein interner Trainingsplan erzeugt
2. identische Base-Learner-Aufgaben werden dedupliziert
3. die besten Parameter werden anschließend allen passenden Rollen zugeordnet

Eine Tuning-Task wird über folgende Merkmale beschrieben:
- Base-Learner-Familie
- Objective-Familie
- Estimator-Task (`classifier` oder `regressor`)
- Sample-Scope
- Nutzung des Treatment-Features
- Zieltyp

Beispiele für gemeinsam nutzbare Aufgaben:
- `TLearner / models` und `XLearner / models`
- DML-Familie für `model_y` und `model_t`
- Propensity-Modelle auf allen Daten

Nicht zusammengelegt werden Aufgaben, die auf anderer Datengrundlage oder mit anderem Zieltyp trainiert werden.

## 6) Final-Modelle und R-Score-Tuning

Einige Learner besitzen ein Final-Modell, das den CATE aus Residuen oder Pseudo-Outcomes lernt.
In **rubin** läuft dieses Tuning getrennt vom Base-Learner-Tuning über `final_model_tuning`.

Praktische Konsequenzen:
- `model_final` ist typischerweise ein Regressor
- Parameter für `model_final` werden getrennt von `model_y`, `model_t` oder `model_propensity` behandelt
- das Tuning wird bewusst nur einmal auf dem ersten Cross-Prediction-Train-Fold durchgeführt und danach wiederverwendet

## 7) Modell-Management (Champion/Challenger)

Siehe `rubin/model_management.py`:
- beim Analyselauf entsteht ein Registry-Manifest
- ein Champion wird automatisch oder manuell gewählt
- optional wird der Champion vor dem Bundle-Export auf allen im Run verfügbaren Daten refittet
- `run_promote.py` kann den Champion im Manifest nachträglich umstellen

## 8) Explainability erweitern

Explainability ist bewusst als separater Batch-Workflow umgesetzt. Einstiegspunkt ist `run_explain.py`, der auf einem Bundle arbeitet.

Kernmodule unter `rubin/explainability/`:
- `shap_uplift.py`
- `permutation_uplift.py`
- `segment_analysis.py`
- `reporting.py`

Neue Explainability-Bausteine sollten:
1. eine klar testbare Funktion liefern
2. keine Trainingslogik benötigen
3. Artefakte als CSV/PNG oder andere einfache Dateiformate erzeugen

## Best Practices

- Konfiguration ist die Quelle der Wahrheit
- neue Felder immer in `settings.py` modellieren und validieren
- Runner schlank halten; Geschäftslogik gehört in Module unter `rubin/`
- Bundles rückwärtskompatibel erweitern statt implizit umzubauen
- bei neuen Modellrollen immer prüfen, ob sie in `tuning_optuna.py` und in der Dokumentation ergänzt werden müssen
