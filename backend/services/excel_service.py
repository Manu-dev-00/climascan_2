import pandas as pd
from pathlib import Path

def save_to_excel_and_csv(df: pd.DataFrame, job_dir: Path, job_id: str, station: str):
    excel_path = job_dir / f"{station}_{job_id}.xlsx"
    csv_path = job_dir / f"{station}_{job_id}.csv"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Releves", index=False)

    df.to_csv(csv_path, index=False, encoding='utf-8-sig', sep=';')

    return excel_path, csv_path