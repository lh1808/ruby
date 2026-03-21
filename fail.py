Datenvorbereitung fehlgeschlagen: Fehlgeschlagen (Exit 1) Details: Traceback (most recent call last): File "/mnt/rubin/run_dataprep.py", line 27, in <module> main() File "/mnt/rubin/run_dataprep.py", line 22, in main pipeline = DataPrepPipeline.from_config_path(args.config) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 65, in from_config_path return cls(cfg, cfg.data_prep) ^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 51, in __init__ raise ValueError("data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.") ValueError: data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.




Details:
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:1408: DataConversionWarning: A column-vector y was passed when a 1d array was expected. Please change the shape of y to (n_samples, ), for example using ravel().
  y = column_or_1d(y, warn=True)
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names
  warnings.warn(
Traceback (most recent call last):
  File "/mnt/rubin/run_analysis.py", line 43, in <module>
    main()
  File "/mnt/rubin/run_analysis.py", line 39, in main
    pipe.run(export_bundle=args.export_bundle, bundle_dir=args.bundle_dir, bundle_id=args.bundle_id)
  File "/mnt/rubin/rubin/pipelines/analysis_pipeline.py", line 1229, in run
    models, preds = self._run_training(cfg, X, T, Y, tuned_params_by_model, holdout_data, mlflow)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/pipelines/analysis_pipeline.py", line 399, in _run_training
    df_pred = train_and_crosspredict_bt_bo(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/training.py", line 137, in train_and_crosspredict_bt_bo
    preds[va_idx] = fold_pred
    ~~~~~^^^^^^^^
ValueError: shape mismatch: value array of shape (8720,1,1) could not be broadcast to indexing result of shape (8720,)



(generic) ubuntu@192.168.0.138 ~ $ curl http://localhost:8501/api/progress
{"generation":1,"message":"Fehlgeschlagen (Exit 1)","percent":66,"pid":35292,"result_files":[],"status":"error","stderr_tail":"  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:1408: DataConversionWarning: A column-vector y was passed when a 1d array was expected. Please change the shape of y to (n_samples, ), for example using ravel().\n  y = column_or_1d(y, warn=True)\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names\n  warnings.warn(\n/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/validation.py:2739: UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names\n  warnings.warn(\nTraceback (most recent call last):\n  File \"/mnt/rubin/run_analysis.py\", line 43, in <module>\n    main()\n  File \"/mnt/rubin/run_analysis.py\", line 39, in main\n    pipe.run(export_bundle=args.export_bundle, bundle_dir=args.bundle_dir, bundle_id=args.bundle_id)\n  File \"/mnt/rubin/rubin/pipelines/analysis_pipeline.py\", line 1229, in run\n    models, preds = self._run_training(cfg, X, T, Y, tuned_params_by_model, holdout_data, mlflow)\n                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/mnt/rubin/rubin/pipelines/analysis_pipeline.py\", line 399, in _run_training\n    df_pred = train_and_crosspredict_bt_bo(\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/mnt/rubin/rubin/training.py\", line 137, in train_and_crosspredict_bt_bo\n    preds[va_idx] = fold_pred\n    ~~~~~^^^^^^^^\nValueError: shape mismatch: value array of shape (8720,1,1) could not be broadcast to indexing result of shape (8720,)","stdout_tail":"[rubin] Step 1/6: Daten laden & Preprocessing\n[rubin] Step 2/6: Feature-Selektion\n[rubin] Step 3/6: Base-Learner-Tuning","step":"Training & Cross-Predictions","step_index":4,"task":"run_analysis","total_steps":6}
