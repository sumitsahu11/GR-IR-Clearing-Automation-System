import pandas as pd
import yaml
from loguru import logger
from pathlib import Path
from src.utils import validate_columns, clean_amount


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _find_header_row(file: str, sheet: str | int) -> int:
    raw = pd.read_excel(file, sheet_name=sheet, header=None, dtype=str)
    keywords = {"po", "vendor", "amount", "document", "plant", "currency", "posting"}
    best_row = 0
    best_score = -1

    for i in range(min(len(raw), 20)):
        row = raw.iloc[i].astype(str).str.lower().tolist()
        score = 0
        for v in row:
            if any(k in v for k in keywords):
                score += 1
        if score > best_score:
            best_score = score
            best_row = i

    return best_row


def load_sap_data(config: dict) -> pd.DataFrame:
    file = config["sap"]["input_file"]
    sheet = config["sap"].get("sheet_name", 0)
    logger.info(f"Loading SAP data: {file} | Sheet: {sheet}")

    header_row = _find_header_row(file, sheet)
    logger.info(f"Detected header row: {header_row}")

    df = pd.read_excel(
        file,
        sheet_name=sheet,
        header=header_row,
        dtype=str
    )

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )
    logger.info(f"Loaded columns: {df.columns.tolist()}")

    for col in ["GR Posting Date", "IR Posting Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["GR Amount", "IR Amount", "Difference (IR-GR)", "TDS Amount", "GST Diff Amount"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_amount)

    str_cols = [
        "GR Vendor Name (SAP)", "IR Vendor Name (Invoice)",
        "Vendor Code", "PO Number", "Discrepancy Flag",
        "Currency", "Plant", "Cost Center"
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "PO Number" in df.columns:
        df = df[df["PO Number"].notna()].copy()
        df = df[df["PO Number"].astype(str).str.lower() != "nan"].copy()
        df = df[df["PO Number"].astype(str).str.strip() != ""].copy()
    else:
        raise KeyError(f"'PO Number' not found. Columns: {df.columns.tolist()}")

    validate_columns(df)
    logger.success(f"Loaded {len(df)} GR/IR open items successfully")

    out = Path("data/processed/cleaned_grir.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    logger.info(f"Processed data saved to {out}")

    return df