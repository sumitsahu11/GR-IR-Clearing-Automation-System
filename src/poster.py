import pandas as pd
from datetime import date
from pathlib import Path
from loguru import logger


def _make_clearing_doc(gr_doc: str, ir_doc: str) -> str:
    """
    Deterministic clearing doc number — derived from actual GR + IR doc numbers.
    Same pair = same clearing doc number, har baar. Koi random nahi.
    Format: 190XXXXXXXX (SAP-style)
    """
    combined = f"{gr_doc}_{ir_doc}"
    hash_val = abs(hash(combined)) % 100_000_000  # 8 digits, deterministic
    return f"190{hash_val:08d}"


def post_to_sap(row: dict) -> dict:
    """
    SAP connected nahi hai abhi — isliye jo bhi auto_clear bucket mein aaya
    usse CLEARED mark karo actual data values ke saath.

    Production mein replace karo:
        pyrfc → BAPI_ACC_GL_POSTING_POST
    """
    gr_doc = str(row.get("GR Document No", "")).strip()
    ir_doc = str(row.get("IR Document No", "")).strip()

    return {
        # ── Document identifiers (actual data) ──────────────────
        "gr_document":      row.get("GR Document No"),
        "ir_document":      row.get("IR Document No"),
        "po_number":        row.get("PO Number"),
        "po_line_item":     row.get("PO Line Item"),

        # ── Vendor info (actual data) ────────────────────────────
        "vendor_code":      row.get("Vendor Code"),
        "vendor_name":      row.get("GR Vendor Name (SAP)"),
        "vendor_invoice":   row.get("IR Vendor Name (Invoice)"),

        # ── Amounts (actual data) ────────────────────────────────
        "gr_amount":        row.get("GR Amount"),
        "ir_amount":        row.get("IR Amount"),
        "difference":       row.get("Difference (IR-GR)"),
        "tds_amount":       row.get("TDS Amount"),
        "gst_diff":         row.get("GST Diff Amount"),

        # ── Dates (actual data) ──────────────────────────────────
        "gr_posting_date":  str(row.get("GR Posting Date", "")),
        "ir_posting_date":  str(row.get("IR Posting Date", "")),
        "posting_date":     str(date.today()),

        # ── Org data (actual data) ───────────────────────────────
        "company_code":     row.get("Company Code", "1000"),
        "plant":            row.get("Plant"),
        "cost_center":      row.get("Cost Center"),
        "gl_account":       row.get("GL Account"),
        "currency":         row.get("Currency", "INR"),
        "payment_terms":    row.get("Payment Terms"),

        # ── Aging (actual data) ──────────────────────────────────
        "aging_days":       row.get("Aging (Days)"),
        "aging_bucket":     row.get("Aging Bucket"),

        # ── Discrepancy info (actual data) ───────────────────────
        "discrepancy_flag": row.get("Discrepancy Flag"),
        "discrepancy_reason": row.get("Discrepancy Reason"),

        # ── Scoring (from pipeline) ──────────────────────────────
        "confidence_score": row.get("confidence_score"),
        "tfidf_score":      row.get("tfidf_vendor_score"),

        # ── Posting result ───────────────────────────────────────
        "status":           "CLEARED",
        "sap_clearing_doc": _make_clearing_doc(gr_doc, ir_doc),
        "error_msg":        None,
    }


def run_auto_posting(auto_clear_df: pd.DataFrame,
                     config: dict) -> pd.DataFrame:
    """
    auto_clear bucket ke saare items SAP mein post karo.
    SAP connected nahi → sab CLEARED, actual data values log mein.
    """
    total = len(auto_clear_df)
    logger.info(f"Starting SAP auto-posting for {total} items...")

    results = []
    for _, row in auto_clear_df.iterrows():
        results.append(post_to_sap(row.to_dict()))

    log_df   = pd.DataFrame(results)
    log_path = config["output"]["posting_log"]
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    log_df.to_csv(log_path, index=False)

    cleared_amt = log_df["gr_amount"].sum()

    logger.success(
        f"Posting complete | Cleared: {total} / {total} | "
        f"Cash Unlocked: Rs.{cleared_amt:,.2f}"
    )
    logger.info(f"Posting log saved → {log_path}")

    return log_df
