Analyse fehlgeschlagen: Fehlgeschlagen (Exit 1)

Details:
Traceback (most recent call last):
  File "/mnt/rubin/run_analysis.py", line 43, in <module>
    main()
  File "/mnt/rubin/run_analysis.py", line 37, in main
    cfg = load_config(args.config)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/rubin/settings.py", line 500, in load_config
    return AnalysisConfig.model_validate(raw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/rubin/.pixi/envs/app/lib/python3.12/site-packages/pydantic/main.py", line 716, in model_validate
    return cls.__pydantic_validator__.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for AnalysisConfig
learner_data_usage
  Input should be a valid dictionary or instance of LearnerDataUsageConfig [type=model_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.12/v/model_type
