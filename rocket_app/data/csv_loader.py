import base64
import io

import pandas as pd


def load_dataframe_from_upload(contents, filename):
    if not contents or not filename:
        return None, None

    _, data = contents.split(",", 1)
    decoded = base64.b64decode(data)

    if filename.lower().endswith(".csv"):
        try:
            text = decoded.decode("utf-8")
        except UnicodeDecodeError:
            text = decoded.decode("latin-1")
        df = pd.read_csv(io.StringIO(text))
    elif filename.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(io.BytesIO(decoded))
    else:
        raise ValueError("Unsupported file format.")

    return df, f"{filename} loaded ({df.shape[0]} rows x {df.shape[1]} columns)"
