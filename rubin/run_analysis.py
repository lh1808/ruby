from __future__ import annotations

"""Einstiegspunkt für die Analyse-Pipeline."""

import argparse
from rubin.settings import load_config
from rubin.pipelines.analysis_pipeline import AnalysisPipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yml")
    ap.add_argument(
        "--export-bundle",
        action="store_true",
        default=None,
        help="Überschreibt bundle.enabled aus der Konfiguration und exportiert am Ende ein Bundle.",
    )
    ap.add_argument(
        "--no-export-bundle",
        dest="export_bundle",
        action="store_false",
        help="Überschreibt bundle.enabled aus der Konfiguration und deaktiviert den Bundle-Export.",
    )
    ap.add_argument(
        "--bundle-dir",
        default=None,
        help="Überschreibt bundle.base_dir aus der Konfiguration.",
    )
    ap.add_argument(
        "--bundle-id",
        default=None,
        help="Überschreibt bundle.bundle_id aus der Konfiguration.",
    )
    args = ap.parse_args()

    cfg = load_config(args.config)
    pipe = AnalysisPipeline(cfg)
    pipe.run(export_bundle=args.export_bundle, bundle_dir=args.bundle_dir, bundle_id=args.bundle_id)


if __name__ == "__main__":
    main()
