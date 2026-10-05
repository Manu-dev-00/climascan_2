import pandas as pd
import re

def clean_meteo_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    def clean_cell(value):
        if pd.isna(value) or str(value).strip() == "":
            return -999

        text = str(value).strip().lower()

        if any(k in text for k in ["calme", "x", "xx", "xxx", ".", "-", "_", "scam", "néant"]):
            return 0

        # Nettoyage caractères
        cleaned = re.sub(r'[^0-9.,-]', '', text)
        cleaned = cleaned.replace(',', '.')

        try:
            return float(cleaned)
        except:
            return 0

    # Colonnes à nettoyer (sauf métadonnées)
    meta_cols = ['Station_Name', 'Station_Code', 'Observation_Month']
    for col in df.columns:
        if col not in meta_cols:
            df[col] = df[col].apply(clean_cell)

    return df