11:13:03 INFO [rubin.analysis] [rubin] Step 4/8: Training & Cross-Predictions
11:13:03 INFO [rubin.analysis] DRLearner model_final effektive Params: {'iterations': 102, 'depth': 5, 'min_data_in_leaf': 52} (explicit_tuned=ja, default_fallback=BLOCKED)
11:13:03 INFO [rubin.training] DRLearner: 5 Folds parallel (n_jobs=5, threads) auf 64 Kernen.
11:15:45 INFO [rubin.analysis] Predictions_DRLearner: CATE min=-1.08014, median=0.00223135, max=1.72051, std=0.0146339, unique=435751/435995, non-zero=435995/435995
11:15:45 INFO [rubin.analysis] NonParamDML model_final effektive Params: {'iterations': 586, 'depth': 4, 'min_data_in_leaf': 13} (explicit_tuned=ja, default_fallback=BLOCKED)
11:15:46 INFO [rubin.training] NonParamDML: 5 Folds parallel (n_jobs=5, threads) auf 64 Kernen.
11:18:04 INFO [rubin.analysis] Predictions_NonParamDML: CATE min=-1.41199, median=0.00202579, max=2.15843, std=0.0294672, unique=435755/435995, non-zero=435995/435995
11:18:05 INFO [rubin.training] SLearner: 5 Folds parallel (n_jobs=5, threads) auf 64 Kernen.
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/sklearn/utils/deprecation.py:151: FutureWarning: 'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8.
  warnings.warn(
11:18:31 INFO [rubin.analysis] Predictions_SLearner: CATE min=-0.00521651, median=0.0021894, max=0.0256584, std=0.000360643, unique=433664/435995, non-zero=435995/435995
11:22:37 INFO [rubin.training] CausalForestDML: 5 Folds parallel (n_jobs=5, threads) auf 64 Kernen.
