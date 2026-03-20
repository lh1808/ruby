Datenvorbereitung fehlgeschlagen: Fehlgeschlagen (Exit 1) Details: Traceback (most recent call last): File "/mnt/rubin/run_dataprep.py", line 27, in <module> main() File "/mnt/rubin/run_dataprep.py", line 22, in main pipeline = DataPrepPipeline.from_config_path(args.config) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 65, in from_config_path return cls(cfg, cfg.data_prep) ^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 51, in __init__ raise ValueError("data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.") ValueError: data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.




Analyse fehlgeschlagen: Fehlgeschlagen (Exit 1)

Details:
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/optuna/study/_optimize.py", line 206, in _run_trial
    value_or_values = func(trial)
                      ^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 632, in objective
    return self._objective_all_classification(params, X_mat=X_mat, target=target.astype(int))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 507, in _objective_all_classification
    for tr, va in _iter_stratified_or_kfold(target.astype(int), n_splits=self.cfg.tuning.cv_splits, seed=self.seed):
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 54, in _iter_stratified_or_kfold
    raise ValueError("Für die Aufteilung werden mindestens 2 Beobachtungen benötigt.")
ValueError: Für die Aufteilung werden mindestens 2 Beobachtungen benötigt.
[W 2026-03-20 19:48:34,529] Trial 0 failed with value None.
Traceback (most recent call last):
  File "/mnt/rubin/run_analysis.py", line 43, in <module>
    main()
  File "/mnt/rubin/run_analysis.py", line 39, in main
    pipe.run(export_bundle=args.export_bundle, bundle_dir=args.bundle_dir, bundle_id=args.bundle_id)
  File "/mnt/rubin/rubin/pipelines/analysis_pipeline.py", line 1216, in run
    tuned_params_by_model = self._run_tuning(cfg, X, T, Y, mlflow)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/pipelines/analysis_pipeline.py", line 231, in _run_tuning
    tuned_params_by_model = tuner.tune_all(cfg.models.models_to_train, X=X, Y=Y, T=T)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 680, in tune_all
    best = self._tune_task(task, X=X, Y=Y, T=T, shared_params=tuned_by_task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 646, in _tune_task
    study.optimize(objective, n_trials=int(self.cfg.tuning.n_trials), timeout=self.cfg.tuning.timeout_seconds)
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/optuna/study/study.py", line 490, in optimize
    _optimize(
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/optuna/study/_optimize.py", line 68, in _optimize
    _optimize_sequential(
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/optuna/study/_optimize.py", line 165, in _optimize_sequential
    frozen_trial_id = _run_trial(study, func, catch)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/optuna/study/_optimize.py", line 263, in _run_trial
    raise func_err
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/optuna/study/_optimize.py", line 206, in _run_trial
    value_or_values = func(trial)
                      ^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 632, in objective
    return self._objective_all_classification(params, X_mat=X_mat, target=target.astype(int))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 507, in _objective_all_classification
    for tr, va in _iter_stratified_or_kfold(target.astype(int), n_splits=self.cfg.tuning.cv_splits, seed=self.seed):
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 54, in _iter_stratified_or_kfold
    raise ValueError("Für die Aufteilung werden mindestens 2 Beobachtungen benötigt.")
ValueError: Für die Aufteilung werden mindestens 2 Beobachtungen benötigt.
