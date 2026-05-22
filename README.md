# 🤖 GR/IR Clearing Automation Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SAP](https://img.shields.io/badge/SAP-Integration-0FAAFF?style=for-the-badge&logo=sap&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-TF--IDF-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production%20Ready-34D399?style=for-the-badge)

<br/>

> **Intelligent TF-IDF + Rule-Based pipeline that automatically reconciles GR/IR discrepancies in SAP — reducing manual effort by up to 80%.**

<br/>

```
SAP Export → Extract → TF-IDF Match → Rule Score → Bucket → Auto-Post to SAP
```

</div>

---

## 📌 Problem Statement

In SAP, the **GR/IR (Goods Receipt / Invoice Receipt)** clearing account accumulates thousands of unmatched debit/credit line items. Manual reconciliation by AP teams is:

- 🕒 **Time-consuming** — analysts spend hours matching POs, GRs, and invoices
- ❌ **Error-prone** — vendor name mismatches, amount tolerances, date gaps cause misclears
- 💸 **Cash-locking** — uncleared items block working capital

This engine **automates the entire workflow** using NLP matching + configurable rule scoring.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **TF-IDF Vendor Matching** | Cosine similarity on vendor name vectors to find best GR↔IR pair |
| 🔤 **Fuzzy Matching** | RapidFuzz handles abbreviations, typos, and short forms |
| ⚖️ **Weighted Rule Scoring** | Configurable weights: amount delta, date gap, PO ref, currency |
| 🪣 **4-Tier Decision Buckets** | AUTO-CLEAR / REVIEW / HOLD / ESCALATE |
| 🤖 **SAP Auto-Posting** | Calls `BAPI_ACC_GL_POSTING_POST` via RFC for high-confidence matches |
| 📊 **Live Dashboard** | Streamlit + Plotly dashboard for monitoring and manual review |
| 📁 **Excel Reports** | Per-bucket Excel exports in `data/output/` |
| 🪵 **Structured Logging** | Loguru rotating logs with colored console output |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GR/IR AUTOMATION PIPELINE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SAP Export/RFC                                                  │
│       │                                                          │
│       ▼                                                          │
│  [src/extractor.py]  ──  Load & Clean GR/IR line items          │
│       │                                                          │
│       ▼                                                          │
│  [src/tfidf_matcher.py]  ──  TF-IDF + RapidFuzz vendor match    │
│       │                                                          │
│       ▼                                                          │
│  [src/rule_scorer.py]  ──  Weighted composite scoring           │
│       │                                                          │
│       ▼                                                          │
│  ┌────────────────────────────────────┐                         │
│  │         DECISION BUCKETS           │                         │
│  │  🟢 AUTO-CLEAR  🟡 REVIEW          │                         │
│  │  🟠 HOLD        🔴 ESCALATE        │                         │
│  └────────────────────────────────────┘                         │
│       │                                                          │
│       ▼                                                          │
│  [src/poster.py]  ──  RFC Auto-Post HIGH confidence → SAP       │
│                                                                  │
│  ─────────────────────────────────────                          │
│  📊 dashboard/app.py  ──  Streamlit live monitoring             │
│  📁 data/output/      ──  Excel reports per bucket              │
│  🪵 logs/pipeline.log ──  Rotating structured logs              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Pipeline Steps

```
Step 01 ─ ⚙️  Load config.yaml          (thresholds, weights, SAP params)
Step 02 ─ 📥  Extract SAP Data           (clean vendor names, amounts, dates)
Step 03 ─ 🧠  TF-IDF Matching            (cosine similarity + RapidFuzz)
Step 04 ─ 📐  Rule-Based Scoring         (weighted multi-criteria engine)
Step 05 ─ 🪣  Split into Buckets         (AUTO-CLEAR / REVIEW / HOLD / ESCALATE)
Step 06 ─ 📋  Summary Report             (counts, %, cash-to-unlock in ₹)
Step 07 ─ 📁  Save Excel Reports         (data/output/ per bucket)
Step 08 ─ 🚀  Auto-Post to SAP           (BAPI RFC call for HIGH confidence)
```

---

## 🪣 Decision Buckets

| Bucket | Confidence | Action |
|---|---|---|
| 🟢 **AUTO-CLEAR** | High | Posted directly to SAP via RFC. Zero human touch. |
| 🟡 **REVIEW** | Moderate | Analyst reviews & approves in dashboard. |
| 🟠 **HOLD** | Low | Senior review. May need vendor/PO master data fix. |
| 🔴 **ESCALATE** | Very Low | AP team handles dispute resolution. |

---

## 📊 Sample Pipeline Output

```
──────────────────────────────────────────────
  PIPELINE RESULTS SUMMARY
──────────────────────────────────────────────
  Total Items     : 1,240
  AUTO-CLEAR      : 743   (59.9%)
  REVIEW          : 287   (23.1%)
  HOLD            : 142   (11.5%)
  ESCALATE        :  68   ( 5.5%)
  Cash to Unlock  : ₹4,82,31,650.00
──────────────────────────────────────────────
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/grir-automation.git
cd grir-automation

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml — add SAP host, client, credentials, scoring weights
```

### 3. Run Pipeline

```bash
python main.py
```

### 4. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

---

## 📁 Project Structure

```
grir-automation/
│
├── main.py                    # Pipeline entry point
├── requirements.txt
│
├── config/
│   ├── config.yaml            # SAP params, thresholds, weights (gitignored)
│   └── config.example.yaml    # Safe template to commit
│
├── src/
│   ├── extractor.py           # SAP data loading & cleaning
│   ├── tfidf_matcher.py       # TF-IDF + fuzzy vendor matching
│   ├── rule_scorer.py         # Weighted scoring, bucketing, Excel export
│   └── poster.py              # SAP RFC auto-posting
│
├── dashboard/
│   └── app.py                 # Streamlit monitoring UI
│
├── data/
│   ├── input/                 # SAP raw exports        ← gitignored
│   └── output/                # Excel reports          ← gitignored
│
├── logs/
│   └── pipeline.log           # Rotating logs          ← gitignored
│
└── tests/
    └── ...                    # pytest test suite
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **NLP / Matching** | scikit-learn (TF-IDF), RapidFuzz |
| **Data Processing** | pandas 2.1, numpy 1.26 |
| **SAP Integration** | pyrfc — `BAPI_ACC_GL_POSTING_POST` |
| **Dashboard** | Streamlit 1.29, Plotly 5.18 |
| **Reports** | openpyxl 3.1 |
| **Config** | PyYAML 6.0 |
| **Logging** | Loguru 0.7 |
| **Testing** | pytest 7.4 |

---

## ⚙️ Configuration

Key parameters in `config/config.yaml`:

```yaml
matching:
  tfidf_threshold: 0.75       # Minimum cosine similarity to consider a match
  fuzzy_threshold: 80         # RapidFuzz score cutoff

scoring:
  weights:
    amount_delta:   0.35      # % difference between GR and IR amount
    date_tolerance: 0.20      # Days between GR date and invoice date
    po_match:       0.25      # Purchase Order number match
    tfidf_score:    0.20      # Vendor name similarity score

buckets:
  auto_clear_min: 0.85        # Score >= 0.85 → AUTO-CLEAR
  review_min:     0.60        # Score >= 0.60 → REVIEW
  hold_min:       0.35        # Score >= 0.35 → HOLD
                              # Score <  0.35 → ESCALATE
```

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 🔒 Security Notes

- `config/config.yaml` is **gitignored** — never commit SAP credentials
- Use `config/config.example.yaml` as a template with placeholder values
- `data/` and `logs/` folders are gitignored — no real SAP data in repo

---

## 📈 Business Impact

- ⏱️ **~80% reduction** in manual GR/IR clearing effort
- 💰 **Faster cash unlock** — auto-posts matched items same day
- 📉 **Fewer errors** — rule engine eliminates human mismatches
- 📊 **Full audit trail** — every decision logged with score breakdown

---

## 👤 Author

**Your Name**
> SAP Finance Automation | Python | NLP | AP/AR Process Optimization

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/your-username)

---

<div align="center">

*Built to eliminate manual GR/IR reconciliation — one RFC call at a time.*

</div>
