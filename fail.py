Datenvorbereitung fehlgeschlagen: Fehlgeschlagen (Exit 1) Details: Traceback (most recent call last): File "/mnt/rubin/run_dataprep.py", line 27, in <module> main() File "/mnt/rubin/run_dataprep.py", line 22, in main pipeline = DataPrepPipeline.from_config_path(args.config) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 65, in from_config_path return cls(cfg, cfg.data_prep) ^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 51, in __init__ raise ValueError("data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.") ValueError: data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.




[rubin] 2026-03-20 20:24:30 INFO 127.0.0.1 - - [20/Mar/2026 20:24:30] "GET /api/health HTTP/1.1" 200 -
[rubin] 2026-03-20 20:24:40 INFO Analyse-Konfiguration geschrieben: /mnt/rubin/config_ui.yml
[rubin] 2026-03-20 20:24:40 INFO Task gestartet: run_analysis (timeout=3600s)
[rubin] 2026-03-20 20:24:40 INFO 127.0.0.1 - - [20/Mar/2026 20:24:40] "POST /api/run-analysis HTTP/1.1" 200 -
[rubin] 2026-03-20 20:24:41 INFO 127.0.0.1 - - [20/Mar/2026 20:24:41] "GET /api/progress HTTP/1.1" 200 -
