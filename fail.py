Analyse fehlgeschlagen: Fehlgeschlagen (Exit 1)

Details:
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/pipelines/analysis_pipeline.py", line 222, in _run_tuning
    tuned_params_by_model = tuner.tune_all(cfg.models.models_to_train, X=X, Y=Y, T=T)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 648, in tune_all
    best = self._tune_task(task, X=X, Y=Y, T=T, shared_params=tuned_by_task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 624, in _tune_task
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
  File "/mnt/rubin/rubin/tuning_optuna.py", line 610, in objective
    return self._objective_all_classification(params, X_mat=X_mat, target=target.astype(int))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 495, in _objective_all_classification
    for tr, va in _iter_stratified_or_kfold(target.astype(int), n_splits=self.cfg.tuning.cv_splits, seed=self.seed):
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/tuning_optuna.py", line 42, in _iter_stratified_or_kfold
    raise ValueError("Für die Aufteilung werden mindestens 2 Beobachtungen benötigt.")
ValueError: Für die Aufteilung werden mindestens 2 Beobachtungen benötigt.
