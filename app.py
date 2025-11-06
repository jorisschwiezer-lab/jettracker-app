from pathlib import Path
import pandas as pd
import glob

# === Einstellungen ===
# Ordner mit deinen CSVs (anpassen, z.B. auf ein Git-Repo-Verzeichnis)
DATA_DIR = Path(".")  # z.B. Path("/path/zum/repo/data")

# Muster für CSV-Dateien. Option A: alle CSVs im Ordner
CSV_PATTERN = str(DATA_DIR / "*.csv")
# Falls du nur Dateien mit '2024' im Namen willst, nimm:
# CSV_PATTERN = str(DATA_DIR / "*2024*.csv")

# Ausgabedatei
OUT_CSV = DATA_DIR / "flights_2024.csv"


def parse_mixed_date(series):
    """
    Robuste Datumserkennung:
    1) Versuch mit dayfirst=True (für 17.02.2025)
    2) Fallback ohne dayfirst (für 03/17/2025)
    3) ISO (2024-09-25) wird automatisch erkannt
    """
    dt = pd.to_datetime(series, errors="coerce", dayfirst=True)
    missing = dt.isna()
    if missing.any():
        dt2 = pd.to_datetime(series[missing], errors="coerce", dayfirst=False)
        dt.loc[missing] = dt2
    return dt


def load_and_filter(csv_paths):
    dfs = []
    for p in csv_paths:
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"Überspringe {p} wegen Lesefehler: {e}")
            continue

        if "Datum" not in df.columns:
            print(f"Überspringe {p}: Spalte 'Datum' fehlt.")
            continue

        # Datum normalisieren
        dt = parse_mixed_date(df["Datum"])
        df = df.assign(_date=dt)

        # Nur valide Datumszeilen behalten
        df = df[df["_date"].notna()].copy()

        # Auf Jahr 2024 filtern
        df_2024 = df[df["_date"].dt.year == 2024].copy()

        # Optional: sortieren und Hilfsspalte entfernen
        df_2024 = df_2024.sort_values("_date").drop(columns=["_date"])

        # Spaltenreihenfolge wie zuvor (falls vorhanden)
        desired_cols = [
            "Datum",
            "Abflugort",
            "Zielort",
            "Distanz (Meilen)",
            "Flugdauer",
            "Treibstoff (Gallonen)",
            "Emissionen (t)",
        ]
        cols = [c for c in desired_cols if c in df_2024.columns]
        other = [c for c in df_2024.columns if c not in cols]
        df_2024 = df_2024[cols + other]

        if not df_2024.empty:
            dfs.append(df_2024)

    if not dfs:
        return pd.DataFrame(columns=[
            "Datum","Abflugort","Zielort","Distanz (Meilen)",
            "Flugdauer","Treibstoff (Gallonen)","Emissionen (t)"
        ])
    return pd.concat(dfs, ignore_index=True)


def main():
    csv_paths = glob.glob(CSV_PATTERN)
    if not csv_paths:
        print(f"Keine CSVs gefunden mit Muster: {CSV_PATTERN}")
        return

    df_2024 = load_and_filter(csv_paths)

    # Speichern
    df_2024.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"Fertig. {len(df_2024)} Zeilen gespeichert unter: {OUT_CSV}")


if __name__ == "__main__":
    main()
