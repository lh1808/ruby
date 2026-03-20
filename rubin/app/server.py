#!/usr/bin/env python3
"""rubin – Backend-Server (Flask)

Architektur:
  GET  /                    → React-App (frontend/index.html)
  GET  /api/health          → Health-Check (Monitoring, Load-Balancer)
  POST /api/upload          → Datei-Upload (multipart)
  POST /api/detect-columns  → Spalten aus Datei erkennen
  POST /api/save-config     → YAML auf Disk speichern
  POST /api/import-config   → YAML importieren (Client-Sync)
  POST /api/run-analysis    → Analyse starten (Background)
  POST /api/run-dataprep    → Datenvorbereitung starten (Background)
  GET  /api/progress        → Fortschritts-Status (Polling)
  POST /api/reset           → State zurücksetzen + Prozess beenden
  GET  /api/results         → Liste der Ergebnis-Dateien
  GET  /api/download/<path> → Datei herunterladen (als Attachment)
  GET  /api/view/<path>     → Datei inline anzeigen (iframe-Einbettung)
  GET  /api/report          → HTML-Report + Metriken laden
  404                       → SPA-Routing (index.html)
"""

from __future__ import annotations

import json
import logging
import os
import re
import signal
import subprocess
import sys
import threading
import traceback
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory, abort
from werkzeug.utils import secure_filename

# ── Version ──
__version__ = "1.0.0"

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="[rubin] %(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("rubin")

# ── Pfade ──
APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
FRONTEND = APP_DIR / "frontend"
UPLOAD_DIR = ROOT / "data" / "uploads"
PROGRESS_FILE = ROOT / ".rubin_progress.json"

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")

# ── Production-Konfiguration ──
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB Upload-Limit
app.config["JSON_SORT_KEYS"] = False

# ── Server-State ──
_state = {
    "status": "idle",           # idle | running | done | error
    "task": None,               # run_analysis | run_dataprep
    "generation": 0,            # Incremented on each start, prevents old threads from overwriting
    "message": "",
    "step": "",
    "step_index": 0,
    "total_steps": 0,
    "percent": 0,
    "stdout_tail": "",
    "stderr_tail": "",
    "result_files": [],
    "pid": None,
}
_state_lock = threading.Lock()


def _set_state(**kw):
    with _state_lock:
        _state.update(kw)
        # Also write to disk so subprocess could read it
        try:
            PROGRESS_FILE.write_text(json.dumps(_state, default=str), encoding="utf-8")
        except Exception:
            pass


def _get_state():
    with _state_lock:
        return dict(_state)


# ══════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════

@app.route("/api/health")
def health():
    """Health-Check für Monitoring und Load-Balancer."""
    is_domino = bool(os.environ.get("DOMINO_PROJECT_NAME"))
    return jsonify({
        "status": "ok",
        "version": __version__,
        "environment": "domino" if is_domino else "standalone",
    })


# ══════════════════════════════════════════════════════
# STATIC / FRONTEND
# ══════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory(str(FRONTEND), "index.html")


@app.errorhandler(404)
def not_found(e):
    """SPA-Routing: Unbekannte Pfade liefern index.html (React-Router)."""
    # API-Requests bekommen echte 404
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Endpoint nicht gefunden."}), 404
    # Alle anderen Pfade → React-App (SPA)
    return send_from_directory(str(FRONTEND), "index.html")


# ══════════════════════════════════════════════════════
# FILE UPLOAD
# ══════════════════════════════════════════════════════

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Multipart file upload. Speichert in data/uploads/ oder target_dir."""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Keine Datei im Request."}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"status": "error", "message": "Kein Dateiname."}), 400

    # Filename sanitieren (entfernt ../, absolute Pfade etc.)
    safe_name = secure_filename(f.filename)
    if not safe_name:
        return jsonify({"status": "error", "message": "Ungueltiger Dateiname."}), 400

    target_dir = request.form.get("target_dir", "data/uploads")
    target = (ROOT / target_dir).resolve()

    # Path-Traversal-Schutz fuer target_dir
    if not str(target).startswith(str(ROOT.resolve())):
        log.warning("Path-Traversal-Versuch blockiert (upload target_dir): %s", target_dir)
        abort(403)

    target.mkdir(parents=True, exist_ok=True)

    filepath = target / safe_name
    f.save(str(filepath))
    log.info("Datei hochgeladen: %s (%d bytes)", filepath.relative_to(ROOT), filepath.stat().st_size)

    return jsonify({
        "status": "done",
        "message": f"Gespeichert: {filepath.relative_to(ROOT)}",
        "path": str(filepath.relative_to(ROOT)),
        "filename": safe_name,
    })


# ══════════════════════════════════════════════════════
# COLUMN DETECTION
# ══════════════════════════════════════════════════════

@app.route("/api/detect-columns", methods=["POST"])
def detect_columns():
    """Liest eine Datei und gibt Spalten, Typen, NaN-Spalten zurueck."""
    data = request.get_json(silent=True) or {}
    filepath = data.get("path", "")

    if not filepath:
        return jsonify({"status": "error", "message": "Kein Pfad angegeben."}), 400

    # Absolute Pfade (z.B. PVC: /mnt/data/...) direkt verwenden,
    # relative Pfade werden relativ zu ROOT aufgelöst + Traversal-Check
    if os.path.isabs(filepath):
        full = Path(filepath).resolve()
    else:
        full = (ROOT / filepath).resolve()
        if not str(full).startswith(str(ROOT.resolve())):
            log.warning("Path-Traversal-Versuch blockiert (detect-columns): %s", filepath)
            return jsonify({"status": "error", "message": "Ungueltiger Pfad."}), 403
    if not full.exists():
        return jsonify({"status": "error", "message": f"Nicht gefunden: {filepath}"}), 404

    try:
        import pandas as pd  # lazy import – nur bei Spalten-Erkennung nötig

        ext = full.suffix.lower()
        if ext == ".parquet":
            # Nur erste Zeilen lesen um OOM bei großen Dateien zu vermeiden
            try:
                import pyarrow.parquet as pq
                pf = pq.ParquetFile(full)
                batch = next(pf.iter_batches(batch_size=5000))
                df = batch.to_pandas()
            except Exception:
                # Fallback: ganzes File lesen (kleine Dateien)
                df = pd.read_parquet(full, engine="pyarrow")
        elif ext == ".csv":
            delim = data.get("delimiter", ",")
            df = pd.read_csv(full, nrows=5000, sep=delim)
        elif ext in (".sas7bdat",):
            try:
                reader = pd.read_sas(full, encoding=data.get("encoding", "utf-8"),
                                     chunksize=5000)
                df = next(reader)
                reader.close()
            except (TypeError, StopIteration):
                # Fallback: manche SAS-Dateien unterstützen kein chunksize
                df = pd.read_sas(full, encoding=data.get("encoding", "utf-8"))
        else:
            df = pd.read_csv(full, nrows=5000)

        columns = list(df.columns)
        dtypes = {}
        nan_cols = []
        for col in columns:
            dtypes[col] = "cat" if df[col].dtype.kind in ("O", "b") else "num"
            if df[col].isnull().any():
                nan_cols.append(col)

        # Sample values for treatment/target detection
        sample_values = {}
        for col in columns[:50]:
            try:
                uniq = df[col].dropna().unique()[:20]
                sample_values[col] = [_safe_str(v) for v in uniq]
            except Exception:
                pass

        # Target values (for binary detection)
        target_col = data.get("target_column")
        target_values = []
        if target_col and target_col in df.columns:
            target_values = [_safe_str(v) for v in sorted(df[target_col].dropna().unique()[:50])]

        # Treatment values
        treat_col = data.get("treatment_column")
        treat_values = []
        if treat_col and treat_col in df.columns:
            treat_values = [_safe_str(v) for v in sorted(df[treat_col].dropna().unique()[:20])]

        return jsonify({
            "status": "done",
            "columns": columns,
            "dtypes": dtypes,
            "nan_cols": nan_cols,
            "n_rows": int(len(df)),
            "n_cols": len(columns),
            "sample_values": sample_values,
            "target_values": target_values,
            "treat_values": treat_values,
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def _safe_str(v):
    try:
        if hasattr(v, "item"):
            return v.item()
        return str(v) if not isinstance(v, (int, float, bool)) else v
    except Exception:
        return str(v)


# ══════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════

@app.route("/api/save-config", methods=["POST"])
def save_config():
    data = request.get_json(silent=True) or {}
    yaml_text = data.get("yaml", "")
    if not yaml_text or not yaml_text.strip():
        return jsonify({"status": "error", "message": "Keine Konfiguration gesendet."}), 400
    filename = data.get("filename", "config.yml")
    # Nur .yml/.yaml erlauben, Filename sanitieren
    safe = secure_filename(filename)
    if not safe or not safe.endswith((".yml", ".yaml")):
        safe = "config.yml"
    out = ROOT / safe
    # Path-Traversal-Schutz
    if not str(out.resolve()).startswith(str(ROOT.resolve())):
        log.warning("Path-Traversal-Versuch blockiert: %s", filename)
        abort(403)
    out.write_text(yaml_text, encoding="utf-8")
    log.info("Konfiguration gespeichert: %s", safe)
    return jsonify({"status": "done", "message": f"Gespeichert: {safe}", "path": str(out)})


@app.route("/api/import-config", methods=["POST"])
def import_config():
    data = request.get_json(silent=True) or {}
    yaml_text = data.get("yaml_text", "")
    if not yaml_text or not yaml_text.strip():
        return jsonify({"status": "error", "message": "Kein YAML-Text gesendet."}), 400
    out = ROOT / "config_imported.yml"
    out.write_text(yaml_text, encoding="utf-8")
    log.info("Konfiguration importiert: %s", out.name)
    return jsonify({"status": "done", "message": f"Importiert: {out.name}"})


# ══════════════════════════════════════════════════════
# ANALYSIS / DATAPREP (Background Tasks)
# ══════════════════════════════════════════════════════

def _run_in_background(task_name: str, cmd: list[str], timeout: int = 3600):
    """Startet einen Subprocess im Background-Thread mit Fortschritts-Tracking."""
    log.info("Task gestartet: %s (timeout=%ds)", task_name, timeout)
    with _state_lock:
        _state["generation"] += 1
        gen = _state["generation"]
    _set_state(
        status="running", task=task_name, message=f"{task_name} gestartet...",
        step="", step_index=0, total_steps=0, percent=0,
        stdout_tail="", stderr_tail="", result_files=[], pid=None,
    )

    def _guarded_set(**kw):
        """Setzt State nur wenn diese Task-Generation noch aktuell ist."""
        with _state_lock:
            if _state["generation"] != gen:
                return  # Abgebrochen oder neuer Task gestartet
            _state.update(kw)
            try:
                PROGRESS_FILE.write_text(json.dumps(_state, default=str), encoding="utf-8")
            except Exception:
                pass

    def _worker():
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1,
                cwd=str(ROOT),
                env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONUNBUFFERED": "1"},
            )
            _guarded_set(pid=proc.pid)

            stdout_lines = []
            stderr_lines = []

            # Stderr in separatem Thread lesen um Deadlock zu vermeiden:
            # Pipeline schreibt viel in stderr (logging, MLflow, Optuna).
            # Wenn der 64KB-Buffer voll ist und niemand liest, blockiert
            # der Prozess → stdout stoppt → Server wartet ewig → Deadlock.
            def _drain_stderr():
                try:
                    for line in iter(proc.stderr.readline, ""):
                        stderr_lines.append(line.rstrip())
                except Exception:
                    pass

            stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
            stderr_thread.start()

            # Read stdout line by line for progress tracking
            for line in iter(proc.stdout.readline, ""):
                stdout_lines.append(line.rstrip())
                _parse_progress(line, stdout_lines, _guarded_set)
                _guarded_set(stdout_tail="\n".join(stdout_lines[-30:]))

            proc.stdout.close()
            stderr_thread.join(timeout=10)  # Warte kurz auf stderr-Thread
            proc.wait(timeout=timeout)

            if proc.returncode == 0:
                files = _scan_result_files()
                log.info("Task %s erfolgreich abgeschlossen (%d Ergebnis-Dateien).", task_name, len(files))
                _guarded_set(
                    status="done", message="Erfolgreich abgeschlossen.",
                    percent=100, result_files=files,
                    stderr_tail="\n".join(stderr_lines[-50:]),
                )
            else:
                log.error("Task %s fehlgeschlagen (Exit %d).", task_name, proc.returncode)
                _guarded_set(
                    status="error",
                    message=f"Fehlgeschlagen (Exit {proc.returncode})",
                    stderr_tail="\n".join(stderr_lines[-50:]),
                )
        except subprocess.TimeoutExpired:
            proc.kill()
            log.error("Task %s: Timeout nach %ds.", task_name, timeout)
            _guarded_set(status="error", message=f"Timeout nach {timeout}s.")
        except Exception as e:
            log.error("Task %s: Unerwarteter Fehler: %s", task_name, e)
            _guarded_set(status="error", message=str(e), stderr_tail=traceback.format_exc())

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


def _parse_progress(line: str, all_lines: list[str], state_setter=None):
    """Parst Pipeline-Fortschritt aus stdout-Zeilen."""
    _update = state_setter or _set_state
    line_lower = line.lower().strip()

    # rubin pipeline prints step markers like:
    # [rubin] Step 3/8: Training & Cross-Predictions
    # [rubin] Progress: 45%
    if "[rubin]" in line and "step" in line_lower:
        parts = line.split("Step")[-1].strip() if "Step" in line else ""
        if "/" in parts:
            try:
                current_total = parts.split(":")[0].strip()
                idx, total = current_total.split("/")
                step_name = parts.split(":", 1)[-1].strip() if ":" in parts else ""
                _update(
                    step=step_name, step_index=int(idx), total_steps=int(total),
                    percent=int(100 * int(idx) / int(total)),
                    message=f"Schritt {idx}/{total}: {step_name}",
                )
            except Exception:
                pass
    elif "progress:" in line_lower or "%" in line:
        try:
            m = re.search(r"(\d+)%", line)
            if m:
                _update(percent=int(m.group(1)))
        except Exception:
            pass
    # Generic step detection
    elif any(kw in line_lower for kw in ["loading", "training", "tuning", "evaluation", "shap", "surrogate", "bundle", "report"]):
        _update(message=line.strip()[:120])


@app.route("/api/run-analysis", methods=["POST"])
def run_analysis():
    if _get_state()["status"] == "running":
        log.warning("Analyse abgelehnt: bereits ein Task aktiv.")
        return jsonify({"status": "error", "message": "Bereits eine Analyse aktiv."}), 409

    data = request.get_json(silent=True) or {}
    yaml_text = data.get("yaml", "")
    if not yaml_text or not yaml_text.strip():
        return jsonify({"status": "error", "message": "Keine Konfiguration gesendet."}), 400
    config_path = ROOT / "config_ui.yml"
    config_path.write_text(yaml_text, encoding="utf-8")
    log.info("Analyse-Konfiguration geschrieben: %s", config_path)

    cmd = [sys.executable, str(ROOT / "run_analysis.py"), "--config", str(config_path)]
    _run_in_background("run_analysis", cmd)

    return jsonify({"status": "started", "message": "Analyse gestartet."})


@app.route("/api/run-dataprep", methods=["POST"])
def run_dataprep():
    if _get_state()["status"] == "running":
        log.warning("Datenvorbereitung abgelehnt: bereits ein Task aktiv.")
        return jsonify({"status": "error", "message": "Bereits ein Task aktiv."}), 409

    data = request.get_json(silent=True) or {}
    yaml_text = data.get("yaml", "")
    if not yaml_text or not yaml_text.strip():
        return jsonify({"status": "error", "message": "Keine Konfiguration gesendet."}), 400
    config_path = ROOT / "config_dataprep_ui.yml"
    config_path.write_text(yaml_text, encoding="utf-8")
    log.info("DataPrep-Konfiguration geschrieben: %s", config_path)

    cmd = [sys.executable, str(ROOT / "run_dataprep.py"), "--config", str(config_path)]
    _run_in_background("run_dataprep", cmd, timeout=1800)

    return jsonify({"status": "started", "message": "Datenvorbereitung gestartet."})


# ══════════════════════════════════════════════════════
# PROGRESS (Polling)
# ══════════════════════════════════════════════════════

@app.route("/api/progress")
def get_progress():
    return jsonify(_get_state())


@app.route("/api/reset", methods=["POST"])
def reset_state():
    # Laufenden Prozess beenden
    pid = _get_state().get("pid")
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            log.info("Laufenden Prozess beendet (PID %d).", pid)
        except (OSError, ProcessLookupError):
            pass
    _set_state(status="idle", task=None, message="", step="", step_index=0,
               total_steps=0, percent=0, stdout_tail="", stderr_tail="",
               result_files=[], pid=None)
    return jsonify({"status": "idle"})


# ══════════════════════════════════════════════════════
# RESULTS / DOWNLOADS
# ══════════════════════════════════════════════════════

def _scan_result_files() -> list[dict]:
    """Scannt Ergebnis-Dateien in output/ und bundles/."""
    files = []
    seen = set()

    def _add(f: Path, desc: str):
        key = str(f)
        if key not in seen and f.is_file():
            seen.add(key)
            try:
                files.append({
                    "name": f.name,
                    "path": str(f.relative_to(ROOT)),
                    "desc": desc,
                    "size": f.stat().st_size,
                })
            except Exception:
                pass

    # Bekannte Ergebnis-Dateien (nur in output/ und ROOT suchen)
    search_dirs = [ROOT / "output", ROOT]
    known = [
        ("analysis_report.html", "HTML-Report"),
        ("uplift_eval_summary.json", "Evaluationsmetriken"),
        ("model_registry.json", "Champion & Challenger"),
    ]
    for name, desc in known:
        for d in search_dirs:
            match = d / name
            if match.exists():
                _add(match, desc)
                break
            # Maximal 1 Ebene tief suchen
            for f in d.glob(f"*/{name}"):
                _add(f, desc)
                break

    # Config
    cfg_file = ROOT / "config_ui.yml"
    if cfg_file.exists():
        _add(cfg_file, "Verwendete Konfiguration")

    # Modelle, CSVs, Parquets in output/
    output_dir = ROOT / "output"
    if output_dir.exists():
        for ext, desc in [("*.pkl", "Modell"), ("*.csv", "CSV"), ("*.parquet", "Parquet")]:
            for f in output_dir.rglob(ext):
                _add(f, desc)

    # Bundles
    bundle_dir = ROOT / "bundles"
    if bundle_dir.exists():
        for f in bundle_dir.glob("*.zip"):
            _add(f, "Bundle-Archiv")
    for f in (ROOT / "output").glob("bundle*.zip") if output_dir.exists() else []:
        _add(f, "Bundle-Archiv")

    # Nach Typ sortieren: Reports zuerst, dann Modelle, dann Daten
    type_order = {"HTML-Report": 0, "Evaluationsmetriken": 1, "Verwendete Konfiguration": 2,
                  "Champion & Challenger": 3, "Modell": 4, "Bundle-Archiv": 5, "CSV": 6, "Parquet": 7}
    files.sort(key=lambda f: (type_order.get(f["desc"], 99), f["name"]))
    return files


@app.route("/api/results")
def list_results():
    return jsonify({"files": _scan_result_files()})


@app.route("/api/download/<path:filepath>")
def download_file(filepath):
    full = (ROOT / filepath).resolve()
    # Path-Traversal-Schutz ZUERST (vor exists-Check, verhindert Info-Leak)
    if not str(full).startswith(str(ROOT.resolve())):
        log.warning("Path-Traversal-Versuch blockiert: %s", filepath)
        abort(403)
    if not full.exists() or not full.is_file():
        log.warning("Download angefragt, nicht gefunden: %s", filepath)
        abort(404)
    log.info("Download: %s", filepath)
    return send_file(str(full), as_attachment=True, download_name=full.name)


@app.route("/api/view/<path:filepath>")
def view_file(filepath):
    """Liefert eine Datei inline (fuer iframe-Einbettung, kein Download)."""
    full = (ROOT / filepath).resolve()
    if not str(full).startswith(str(ROOT.resolve())):
        log.warning("Path-Traversal-Versuch blockiert (view): %s", filepath)
        abort(403)
    if not full.exists() or not full.is_file():
        abort(404)
    # Mimetype basierend auf Endung
    mimetype = "text/html" if full.suffix.lower() == ".html" else None
    return send_file(str(full), as_attachment=False, mimetype=mimetype)


@app.route("/api/report")
def get_report():
    """Laed den neuesten HTML-Report und die Metriken."""
    report_path = None
    metrics = None

    # Gezielt in output/ und output/*/ suchen (nicht das ganze Repo)
    search_dirs = [ROOT / "output", ROOT]
    for d in search_dirs:
        if not d.exists():
            continue
        candidates = list(d.glob("analysis_report.html")) + list(d.glob("*/analysis_report.html"))
        if candidates:
            report_path = max(candidates, key=lambda p: p.stat().st_mtime)
            break

    for d in search_dirs:
        if not d.exists():
            continue
        for f in list(d.glob("uplift_eval_summary.json")) + list(d.glob("*/uplift_eval_summary.json")):
            try:
                metrics = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                pass
            break
        if metrics:
            break

    result = {"status": "done" if report_path else "not_found"}
    if report_path:
        result["report_url"] = f"./api/view/{report_path.relative_to(ROOT)}"
    if metrics:
        result["metrics"] = metrics

    return jsonify(result)


# ══════════════════════════════════════════════════════
# START
# ══════════════════════════════════════════════════════

def main():
    port = int(os.environ.get("DOMINO_APP_PORT", os.environ.get("PORT", 8501)))
    host = os.environ.get("RUBIN_HOST", "0.0.0.0")
    is_domino = bool(os.environ.get("DOMINO_PROJECT_NAME"))

    log.info("Server v%s starten auf %s:%d", __version__, host, port)
    log.info("Frontend: %s", FRONTEND)
    log.info("Projekt:  %s", ROOT)
    if is_domino:
        log.info("Umgebung: Domino (%s)", os.environ.get("DOMINO_PROJECT_NAME"))
    else:
        log.info("Umgebung: Standalone")

    # Sicherstellen, dass Upload-Verzeichnis existiert
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Production-Hinweis: Fuer Hochlast-Szenarien wird ein
    # WSGI-Server wie gunicorn empfohlen:
    #   gunicorn -w 4 -b 0.0.0.0:8501 app.server:app
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()

