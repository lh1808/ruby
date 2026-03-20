Datenvorbereitung fehlgeschlagen: Fehlgeschlagen (Exit 1) Details: Traceback (most recent call last): File "/mnt/rubin/run_dataprep.py", line 27, in <module> main() File "/mnt/rubin/run_dataprep.py", line 22, in main pipeline = DataPrepPipeline.from_config_path(args.config) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 65, in from_config_path return cls(cfg, cfg.data_prep) ^^^^^^^^^^^^^^^^^^^^^^^ File "/mnt/rubin/rubin/pipelines/data_prep_pipeline.py", line 51, in __init__ raise ValueError("data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.") ValueError: data_prep.feature_path ist nicht gesetzt. Bitte Feature-Dictionary konfigurieren.




(generic) ubuntu@192.168.52.214 ~/rubin $ dmesg | grep -i "killed\|oom" | tail -5
[1234724.058674]  oom_kill_process.cold.33+0xb/0x10
[1234724.343154] [  pid  ]   uid  tgid total_vm      rss pgtables_bytes swapents oom_score_adj name
[1234724.814012] oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=cri-containerd-e5aa2a624639ed64b174607f484c7129e62095f268155e68d500a3566f7a31ad.scope,mems_allowed=0-1,oom_memcg=/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod3ec0052f_2587_45ac_958c_b9f801448d6c.slice/cri-containerd-e5aa2a624639ed64b174607f484c7129e62095f268155e68d500a3566f7a31ad.scope,task_memcg=/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod3ec0052f_2587_45ac_958c_b9f801448d6c.slice/cri-containerd-e5aa2a624639ed64b174607f484c7129e62095f268155e68d500a3566f7a31ad.scope,task=python,pid=134243,uid=12574
[1234724.869945] Memory cgroup out of memory: Killed process 134243 (python) total-vm:220109624kB, anon-rss:162942916kB, file-rss:0kB, shmem-rss:0kB, UID:12574 pgtables:346912kB oom_score_adj:672
[1234727.578299] oom_reaper: reaped process 134243 (python), now anon-rss:0kB, file-rss:0kB, shmem-rss:0kB
