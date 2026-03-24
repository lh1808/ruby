13:54:25 INFO [rubin.analysis] DRTester Nuisance einmalig gefittet (BT, cv=3, n_est≤100). Wird für alle Modelle wiederverwendet.
13:54:25 INFO [rubin.analysis] Evaluation Predictions_SLearner: n=435995, min=-0.00771064, median=0.00171136, max=0.0432514, std=0.000422582, non-zero=435995/435995, unique=999
13:54:25 INFO [rubin.analysis] Evaluation Predictions_DRLearner: n=435995, min=-1.2593, median=0.00188598, max=1.87697, std=0.0291962, non-zero=435995/435995, unique=999
13:54:26 INFO [rubin.analysis] Evaluation Predictions_NonParamDML: n=435995, min=-0.891883, median=0.00193504, max=1.93905, std=0.0239251, non-zero=435995/435995, unique=999
13:54:27 INFO [rubin.analysis] Evaluation Predictions_CausalForestDML: n=435995, min=0.000416909, median=0.00219878, max=0.00829028, std=0.00137461, non-zero=435995/435995, unique=999
13:54:27 INFO [rubin.analysis] Metriken für 4 Modelle berechnet. Vorläufiger Champion: CausalForestDML. Diagnostik-Plots: nur Champion
13:54:47 WARNING [rubin.evaluation.drtester_plots] sklift Uplift-by-Percentile fehlgeschlagen: plot_uplift_by_percentile() got an unexpected keyword argument 'ax'
13:54:47 WARNING [rubin.evaluation.drtester_plots] sklift Treatment-Balance fehlgeschlagen: plot_treatment_balance_curve() got an unexpected keyword argument 'ax'
13:54:47 WARNING [rubin.analysis] DRTester/SkLift-Plots für CausalForestDML fehlgeschlagen.
Traceback (most recent call last):
  File "/mnt/rubin/rubin/pipelines/analysis_pipeline.py", line 985, in _evaluate_bt
    plt.close(fig)
    ^^^
NameError: name 'plt' is not defined
13:54:48 WARNING [rubin.evaluation.drtester_plots] sklift Uplift-by-Percentile fehlgeschlagen: plot_uplift_by_percentile() got an unexpected keyword argument 'ax'
13:54:48 WARNING [rubin.evaluation.drtester_plots] sklift Treatment-Balance fehlgeschlagen: plot_treatment_balance_curve() got an unexpected keyword argument 'ax'
13:54:49 WARNING [rubin.evaluation.drtester_plots] sklift Uplift-by-Percentile fehlgeschlagen: plot_uplift_by_percentile() got an unexpected keyword argument 'ax'
13:54:49 WARNING [rubin.evaluation.drtester_plots] sklift Treatment-Balance fehlgeschlagen: plot_treatment_balance_curve() got an unexpected keyword argument 'ax'
13:54:49 WARNING [rubin.evaluation.drtester_plots] sklift Uplift-by-Percentile fehlgeschlagen: plot_uplift_by_percentile() got an unexpected keyword argument 'ax'
13:54:49 WARNING [rubin.evaluation.drtester_plots] sklift Treatment-Balance fehlgeschlagen: plot_treatment_balance_curve() got an unexpected keyword argument 'ax'
13:54:50 WARNING [rubin.evaluation.drtester_plots] sklift Uplift-by-Percentile fehlgeschlagen: plot_uplift_by_percentile() got an unexpected keyword argument 'ax'
13:54:50 WARNING [rubin.evaluation.drtester_plots] sklift Treatment-Balance fehlgeschlagen: plot_treatment_balance_curve() got an unexpected keyword argument 'ax'
13:54:51 INFO [rubin.analysis] [rubin] Step 6/8: Surrogate-Tree
13:54:52 INFO [rubin.analysis] Surrogate-Evaluation: {'qini': 0.0005628525441926595, 'auuc': 0.0019619121766867604, 'uplift_at_10pct': 0.0007434081271287739, 'uplift_at_20pct': 0.0012734208089308825, 'uplift_at_50pct': 0.0021948207822510783, 'policy_value_treat_positive': 0.002798119265002922}
13:54:53 WARNING [rubin.evaluation.drtester_plots] sklift Uplift-by-Percentile fehlgeschlagen: plot_uplift_by_percentile() got an unexpected keyword argument 'ax'
13:54:53 WARNING [rubin.evaluation.drtester_plots] sklift Treatment-Balance fehlgeschlagen: plot_treatment_balance_curve() got an unexpected keyword argument 'ax'
13:54:53 INFO [rubin.analysis] RAM-Optimierung: gc.collect() nach Surrogate.
13:54:53 INFO [rubin.analysis] [rubin] Step 7/8: Bundle-Export
13:59:03 INFO [rubin.analysis] Surrogate-Einzelbaum exportiert (Typ=catboost, Tiefe=6, Blätter=64, trainiert auf 435995 Zeilen).
13:59:03 INFO [rubin.analysis] RAM-Optimierung: Modelle, Predictions und X_full freigegeben.
13:59:03 INFO [rubin.analysis] [rubin] Step 8/8: HTML-Report
13:59:03 INFO [rubin.reporting] HTML-Report geschrieben: ./analysis_report.html
