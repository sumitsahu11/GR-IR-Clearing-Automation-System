import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path

def check_po_match(po_gr: str, po_ir: str) -> float:

    if not po_gr or not po_ir:
        return 0.0
    po_gr = str(po_gr).strip()
    po_ir = str(po_ir).strip()
    if po_gr == po_ir:
        return 1.0
    if po_gr.startswith(po_ir[:6]) or po_ir.startswith(po_gr[:6]):
        return 0.7
    return 0.0

def check_amount_match(
    gr_amt: float, ir_amt: float,
    pct_tol: float = 0.2, abs_tol: float = 100.0
) -> float:

    if gr_amt is None or ir_amt is None:
        return 0.0
    if pd.isna(gr_amt) or pd.isna(ir_amt):
        return 0.0

    diff     = abs(float(gr_amt) - float(ir_amt))
    base     = max(abs(float(gr_amt)), 1.0)
    diff_pct = (diff / base) * 100

    if diff == 0:
        return 1.0                              # Exact match
    if diff <= abs_tol or diff_pct <= pct_tol:
        return 0.95                             # Within tolerance
    if diff_pct <= 2.0:
        return 0.75                             # Small diff TDS,GST 
    if diff_pct <= 5.0:
        return 0.50                             # Moderate diff
    if diff_pct <= 10.0:
        return 0.25                             # Large diff
    return 0.0                                  # Too different

def check_date_match(gr_date, ir_date, days_tol: int = 60) -> float:

    if pd.isna(gr_date) or gr_date is None:
        return 0.5   
    if pd.isna(ir_date) or ir_date is None:
        return 0.3   

    try:
        gap = abs((pd.Timestamp(gr_date) - pd.Timestamp(ir_date)).days)
    except:
        return 0.3

    if gap == 0:           return 1.0
    if gap <= 30:          return 0.9
    if gap <= days_tol:    return 0.7
    if gap <= 90:          return 0.4
    return 0.1

def check_currency_match(curr_gr: str, curr_ir: str) -> float:
    if not curr_gr or not curr_ir:
        return 0.5
    return 1.0 if str(curr_gr).strip() == str(curr_ir).strip() else 0.0

def compute_rule_score(row: pd.Series, config: dict) -> dict:

    w = config["rule_scoring"]

    po_score   = check_po_match(
        row.get("PO Number"), row.get("PO Number"))  # same row = same PO

    tfidf_score = float(row.get("tfidf_vendor_score", 0.0))

    amt_score  = check_amount_match(
        row.get("GR Amount"), row.get("IR Amount"),
        w["amount_tolerance_pct"], w["amount_tolerance_abs_inr"]
    )
    date_score = check_date_match(
        row.get("GR Posting Date"), row.get("IR Posting Date"),
        w["date_tolerance_days"]
    )
    curr_score = check_currency_match(
        row.get("Currency"), row.get("Currency"))

    total = (
        po_score    * w["po_number_match_weight"]   +
        tfidf_score * w["vendor_similarity_weight"] +
        amt_score   * w["amount_tolerance_weight"]  +
        date_score  * w["date_tolerance_weight"]    +
        curr_score  * w["currency_match_weight"]
    )

    flag = str(row.get("Discrepancy Flag", ""))
    if flag == "EXACT MATCH":
        total = max(total, 95.0)        # Exact match always high
    elif flag == "MISSING INVOICE":
        total = min(total, 40.0)        # Missing invoice always hold
    elif flag == "DUPLICATE IR RISK":
        total = min(total, 30.0)        # Duplicate always escalate

    return {
        "confidence_score": round(total, 1),
        "score_po":         round(po_score * w["po_number_match_weight"], 1),
        "score_vendor":     round(tfidf_score * w["vendor_similarity_weight"], 1),
        "score_amount":     round(amt_score * w["amount_tolerance_weight"], 1),
        "score_date":       round(date_score * w["date_tolerance_weight"], 1),
        "score_currency":   round(curr_score * w["currency_match_weight"], 1),
    }

def apply_rule_scoring(df: pd.DataFrame, config: dict) -> pd.DataFrame:

    logger.info("Applying weighted rule-based scoring...")

    score_data = df.apply(
        lambda row: compute_rule_score(row, config), axis=1
    )
    score_df = pd.DataFrame(list(score_data))

    df = pd.concat([df.reset_index(drop=True),
                    score_df.reset_index(drop=True)], axis=1)

    t_auto   = config["rule_scoring"]["auto_clear_score"]
    t_review = config["rule_scoring"]["review_score"]

    def get_decision(row):
        score = row["confidence_score"]
        flag  = str(row.get("Discrepancy Flag", ""))
        if flag in ("MISSING INVOICE", "DUPLICATE IR RISK"):
            return "ESCALATE"
        if score >= t_auto:   return "AUTO-CLEAR"
        if score >= t_review: return "REVIEW"
        return "HOLD"

    df["decision"] = df.apply(get_decision, axis=1)

    counts = df["decision"].value_counts().to_dict()
    logger.success(
        f"Scoring complete | "
        f"AUTO-CLEAR: {counts.get('AUTO-CLEAR',0)} | "
        f"REVIEW: {counts.get('REVIEW',0)} | "
        f"HOLD: {counts.get('HOLD',0)} | "
        f"ESCALATE: {counts.get('ESCALATE',0)}"
    )
    return df

def split_buckets(df: pd.DataFrame) -> dict:
    return {
        "auto_clear": df[df["decision"] == "AUTO-CLEAR"].copy(),
        "review":     df[df["decision"] == "REVIEW"].copy(),
        "hold":       df[df["decision"] == "HOLD"].copy(),
        "escalate":   df[df["decision"] == "ESCALATE"].copy(),
    }

def save_reports(buckets: dict, config: dict):
    
    out_dir = Path("data/output")
    out_dir.mkdir(parents=True, exist_ok=True)

    for bucket_name, df_bucket in buckets.items():
        filename = f"{bucket_name.lower().replace(' ', '_')}.csv"
        filepath = out_dir / filename
        
        df_bucket.to_csv(filepath, index=False)
        logger.info(f"Saved {len(df_bucket)} items → {filepath}")
    
    logger.success("All reports saved successfully!")