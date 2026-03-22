Datenvorbereitung fehlgeschlagen: Fehlgeschlagen (Exit 1) Details: Traceback (most recent call last): File "/mnt/rubin/run_dataprep.py", line 27, in <module> main() File "/mnt/rubin/run_dataprep.py", line 22, in main pipeline = DataPrepPipeline.from_config_path(args.config) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 65, in from_config_path return cls(cfg, cfg.data_prep) ^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 51, in __init__ raise ValueError("data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.") ValueError: data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.




Analyse fehlgeschlagen: Fehlgeschlagen (Exit -15)

Details:
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
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/numpy/_core/fromnumeric.py:3824: RuntimeWarning: Mean of empty slice
  return _methods._mean(a, axis=axis, dtype=dtype,
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/numpy/_core/_methods.py:142: RuntimeWarning: invalid value encountered in scalar divide
  ret = ret.dtype.type(ret / rcount)
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/numpy/_core/_methods.py:219: RuntimeWarning: Degrees of freedom <= 0 for slice
  ret = _var(a, axis=axis, dtype=dtype, out=out, ddof=ddof,
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/numpy/_core/_methods.py:178: RuntimeWarning: invalid value encountered in divide
  arrmean = um.true_divide(arrmean, div, out=arrmean,
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/numpy/_core/_methods.py:211: RuntimeWarning: invalid value encountered in scalar divide
  ret = ret.dtype.type(ret / rcount)
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/econml/validate/utils.py:106: RuntimeWarning: invalid value encountered in divide
  mboot = (toc_psi / toc_std.reshape(-1, 1)) @ w / n
/mnt/rubin/.pixi/envs/default/lib/python3.12/site-packages/econml/validate/utils.py:99: RuntimeWarning: invalid value encountered in divide
  toc_psi[it, :] = np.squeeze((dr_val - ate) * (inds / group_prob - 1) - toc[it])
