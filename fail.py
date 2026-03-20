Datenvorbereitung fehlgeschlagen: Fehlgeschlagen (Exit 1) Details: Traceback (most recent call last): File "/mnt/rubin/run_dataprep.py", line 27, in <module> main() File "/mnt/rubin/run_dataprep.py", line 22, in main pipeline = DataPrepPipeline.from_config_path(args.config) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 65, in from_config_path return cls(cfg, cfg.data_prep) ^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 51, in __init__ raise ValueError("data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.") ValueError: data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.




(generic) ubuntu@192.168.0.138 ~ $ curl http://localhost:8501/api/progress
{"generation":1,"message":"Schritt 4/6: Training & Cross-Predictions","percent":66,"pid":16483,"result_files":[],"status":"running","stderr_tail":"","stdout_tail":"[rubin] Step 1/6: Daten laden & Preprocessing\n[rubin] Step 2/6: Feature-Selektion\n[rubin] Step 3/6: Base-Learner-Tuning\n[rubin] Step 4/6: Training & Cross-Predictions","step":"Training & Cross-Predictions","step_index":4,"task":"run_analysis","total_steps":6}
(generic) ubuntu@192.168.0.138 ~ $ dmesg | grep -i "killed\|oom" | tail -5
[499086.566573]  oom_kill_process.cold.33+0xb/0x10
[499086.821324] [  pid  ]   uid  tgid total_vm      rss pgtables_bytes swapents oom_score_adj name
[499086.916478] oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=cri-containerd-10521a761011051aec6ea9056ea310da06806d1c9719a59bf1790e0ca93d9d84.scope,mems_allowed=0-1,oom_memcg=/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podce01147c_c24e_4d06_94d1_4742572744b5.slice/cri-containerd-10521a761011051aec6ea9056ea310da06806d1c9719a59bf1790e0ca93d9d84.scope,task_memcg=/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podce01147c_c24e_4d06_94d1_4742572744b5.slice/cri-containerd-10521a761011051aec6ea9056ea310da06806d1c9719a59bf1790e0ca93d9d84.scope,task=python,pid=2868804,uid=12574
[499086.971877] Memory cgroup out of memory: Killed process 2868804 (python) total-vm:163885464kB, anon-rss:82514312kB, file-rss:0kB, shmem-rss:0kB, UID:12574 pgtables:246052kB oom_score_adj:788
[499089.224333] oom_reaper: reaped process 2868804 (python), now anon-rss:0kB, file-rss:0kB, shmem-rss:0kB
