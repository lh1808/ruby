from __future__ import annotations

"""Kleine I/O-Helfer für tabellarische Dateien."""

import pandas as pd


def read_table(path: str, *, use_index: bool = True) -> pd.DataFrame:
    """Liest CSV oder Parquet anhand der Dateiendung."""
    p = str(path)
    if p.lower().endswith((".parquet", ".pq")):
        try:
            df = pd.read_parquet(p)
        except ImportError as e:
            raise ImportError(
                "Für Parquet-Dateien wird 'pyarrow' oder 'fastparquet' benötigt. "
                "Bitte die Abhängigkeiten aus requirements.txt installieren."
            ) from e
        return df if use_index else df.reset_index(drop=True)

    if use_index:
        return pd.read_csv(p, index_col=0, low_memory=False)
    return pd.read_csv(p, low_memory=False)
