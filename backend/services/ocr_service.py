from img2table.ocr import PaddleOCR
from img2table.document import Image as Img2TableImage
import pandas as pd

def process_images_to_dataframe(image_paths: list):
    paddle_ocr = PaddleOCR(use_angle_cls=True, lang="fr", show_log=False)
    all_dfs = []

    for path in image_paths:
        try:
            doc = Img2TableImage(src=path)
            tables = doc.extract_tables(ocr=paddle_ocr, implicit_rows=True, implicit_columns=True)

            for table in tables:
                if not table.df.empty:
                    all_dfs.append(table.df)
        except Exception as e:
            print(f"Erreur OCR sur {path}: {e}")

    if not all_dfs:
        raise Exception("Aucun tableau détecté dans les images fournies.")

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.columns = [str(col).strip() for col in final_df.columns]
    return final_df