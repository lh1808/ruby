"""Runner für die DataPrepPipeline.
Die Datenaufbereitung wird über die zentrale Projekt-Konfiguration gesteuert.
Voraussetzung ist eine Sektion `data_prep` in der verwendeten YAML-Datei.
Beispiel:
python run_dataprep.py --config configs/config_full_example.yml
Der Lauf erzeugt die Artefakte (X/T/Y + Preprocessing) in `data_prep.output_path`.
Diese Pfade werden anschließend in `data_files` der gleichen Konfiguration referenziert
und von der Analyse-Pipeline genutzt."""

from __future__ import annotations

import argparse

from rubin.pipelines.data_prep_pipeline import DataPrepPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="DataPrep für rubin ausführen")
    parser.add_argument("--config", required=True, help="Pfad zur zentralen Konfiguration (YAML)")
    args = parser.parse_args()

    pipeline = DataPrepPipeline.from_config_path(args.config)
    pipeline.run()


if __name__ == "__main__":
    main()
