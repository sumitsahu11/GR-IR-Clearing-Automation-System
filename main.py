from loguru import logger
import sys

from src.extractor      import load_config, load_sap_data
from src.tfidf_matcher  import apply_tfidf_matching
from src.rule_scorer    import apply_rule_scoring, split_buckets, save_reports
from src.poster         import run_auto_posting

def run_pipeline():
    logger.remove()
    logger.add(sys.stdout, level="INFO",
               format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    logger.add("logs/pipeline.log", rotation="1 week", level="DEBUG")

    logger.info("=" * 65)
    logger.info("   GR/IR CLEARING AUTOMATION — TF-IDF + RULE-BASED ENGINE")
    logger.info("=" * 65)

    # Step 1: Load Config 
    config = load_config("config/config.yaml")
    logger.info("Config loaded successfully")

    # Step 2: Extract & Clean SAP Data 
    df = load_sap_data(config)
    logger.info(f"Total open items loaded: {len(df)}")

    # Step 3: TF-IDF Vendor Name Matching 
    df = apply_tfidf_matching(df, config)

    # Step 4: Rule-Based Weighted Scoring 
    df = apply_rule_scoring(df, config)

    # Step 5: Split into Decision Buckets 
    buckets = split_buckets(df)

    # Step 6: Summary Report 
    total = len(df)
    ac    = len(buckets["auto_clear"])
    rv    = len(buckets["review"])
    hd    = len(buckets["hold"])
    esc   = len(buckets["escalate"])

    cash_locked = buckets["auto_clear"]["GR Amount"].sum()

    logger.info("")
    logger.info("─" * 50)
    logger.info(f"  PIPELINE RESULTS SUMMARY")
    logger.info("─" * 50)
    logger.info(f"  Total Items     : {total}")
    logger.info(f"  AUTO-CLEAR      : {ac}  ({round(ac/total*100,1)}%)")
    logger.info(f"  REVIEW          : {rv}  ({round(rv/total*100,1)}%)")
    logger.info(f"  HOLD            : {hd}  ({round(hd/total*100,1)}%)")
    logger.info(f"  ESCALATE        : {esc} ({round(esc/total*100,1)}%)")
    logger.info(f"  Cash to Unlock  : Rs.{cash_locked:,.2f}")
    logger.info("─" * 50)

    # Step 7: Save Excel Reports 
    save_reports(buckets, config)

    # Step 8: Auto-Post HIGH confidence items 
    posting_log = run_auto_posting(buckets["auto_clear"], config)

    cleared_count = len(posting_log[posting_log["status"]=="CLEARED"])
    logger.success(
        f"Pipeline complete! {cleared_count} items cleared in SAP. "
        f"Check data/output/ for reports."
    )

if __name__ == "__main__":
    run_pipeline()