import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

def normalize_vendor_name(name: str) -> str:
    if not name or name in ("nan", "-", "NOT RECEIVED"):
        return ""

    name = name.lower().strip()

    suffixes = [
        r"\bprivate limited\b", r"\bpvt ltd\b", r"\bpvt\b",
        r"\blimited\b", r"\bltd\b", r"\bcorp\b",
        r"\bcorporation\b", r"\bincorporated\b", r"\binc\b",
        r"\bllp\b", r"\blp\b"
    ]
    for s in suffixes:
        name = re.sub(s, "", name)

    abbreviations = {
        "tcs":   "tata consultancy services",
        "hcl":   "hcl technologies",
        "l&t":   "larsen toubro",
        "bel":   "bharat electronics",
        "ril":   "reliance industries",
        "infy":  "infosys",
    }
    for abbr, full in abbreviations.items():
        if name.strip() == abbr:
            name = full

    name = re.sub(r"[^a-z0-9\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name


def build_tfidf_matrix(vendor_names: list) -> tuple:
  
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",    
        ngram_range=(2, 4),    
        min_df=1,
        lowercase=True
    )

    normalized = [normalize_vendor_name(n) for n in vendor_names]
    normalized = [n if n else "unknown_vendor" for n in normalized]

    matrix = vectorizer.fit_transform(normalized)
    logger.info(f"TF-IDF matrix built: {matrix.shape[0]} vendors, "
                f"{matrix.shape[1]} features")
    return vectorizer, matrix, normalized


def compute_vendor_similarity(
    gr_vendor_name: str,
    ir_vendor_name: str,
    vectorizer: TfidfVectorizer,
) -> float:

    if not gr_vendor_name or not ir_vendor_name:
        return 0.0
    if ir_vendor_name in ("NOT RECEIVED", "-", "nan"):
        return 0.0

    gr_norm = normalize_vendor_name(gr_vendor_name)
    ir_norm = normalize_vendor_name(ir_vendor_name)

    if not gr_norm or not ir_norm:
        return 0.0

    if gr_norm == ir_norm:
        return 1.0

    try:
        gr_vec = vectorizer.transform([gr_norm])
        ir_vec = vectorizer.transform([ir_norm])
        score  = cosine_similarity(gr_vec, ir_vec)[0][0]
        return float(round(score, 4))
    except Exception as e:
        logger.warning(f"TF-IDF similarity error: {e}")
        return 0.0


def apply_tfidf_matching(df: pd.DataFrame, config: dict) -> pd.DataFrame:
   
    threshold = config["tfidf_matching"]["vendor_similarity_threshold"]

    logger.info("Building TF-IDF model on all vendor names...")

    all_names = list(set(
        df["GR Vendor Name (SAP)"].dropna().tolist() +
        df["IR Vendor Name (Invoice)"].dropna().tolist()
    ))

    vectorizer, _, _ = build_tfidf_matrix(all_names)

    logger.info("Computing TF-IDF vendor similarity for all pairs...")

    scores = []
    for _, row in df.iterrows():
        gr_vend = str(row.get("GR Vendor Name (SAP)", ""))
        ir_vend = str(row.get("IR Vendor Name (Invoice)", ""))
        score   = compute_vendor_similarity(gr_vend, ir_vend, vectorizer)
        scores.append(score)

    df = df.copy()
    df["tfidf_vendor_score"]   = scores
    df["vendor_match_quality"] = df["tfidf_vendor_score"].apply(
        lambda s: "HIGH" if s >= threshold    #90
             else "MEDIUM" if s >= threshold * 0.7  #63
             else "LOW"         #63
    )

    high   = sum(1 for s in scores if s >= threshold)
    medium = sum(1 for s in scores if threshold * 0.7 <= s < threshold)
    low    = sum(1 for s in scores if s < threshold * 0.7)

    logger.success(
        f"TF-IDF matching done | "
        f"High: {high} | Medium: {medium} | Low: {low}"
    )
    return df