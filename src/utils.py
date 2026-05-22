import pandas as pd
from datetime import datetime
from loguru import logger

def format_inr(amount: float) -> str:
    if amount is None or pd.isna(amount):
        return "N/A"
    return f"Rs.{amount:,.2f}"

def age_bucket(days: int) -> str:
    if days <= 30:   return "0-30 Days"
    if days <= 60:   return "31-60 Days"
    if days <= 90:   return "61-90 Days"
    return ">90 Days (Critical)"

def run_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_columns(df: pd.DataFrame) -> bool:
    required = [
        "PO Number", "GR Document No", "GR Amount",
        "GR Vendor Name (SAP)", "Discrepancy Flag", "Currency"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    logger.success(f"Column validation passed. Shape: {df.shape}")
    return True

def clean_amount(val) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return float(str(val).replace(",", "").replace("Rs.", "").strip())
    except:
        return None