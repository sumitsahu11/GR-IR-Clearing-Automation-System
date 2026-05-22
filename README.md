<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GR/IR Clearing Automation — README</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #050810;
    --surface: #0d1117;
    --card: #111827;
    --border: rgba(99,179,237,0.15);
    --accent: #38bdf8;
    --accent2: #818cf8;
    --accent3: #34d399;
    --gold: #fbbf24;
    --text: #e2e8f0;
    --muted: #64748b;
    --glow: 0 0 40px rgba(56,189,248,0.25);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    overflow-x: hidden;
    line-height: 1.7;
  }

  /* ─── GRID BG ─── */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(56,189,248,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56,189,248,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  /* ─── HERO ─── */
  .hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 24px;
    z-index: 1;
    overflow: hidden;
  }

  .hero-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    pointer-events: none;
    animation: float 8s ease-in-out infinite;
  }
  .orb1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(56,189,248,0.18), transparent 70%); top: -100px; left: -150px; }
  .orb2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(129,140,248,0.15), transparent 70%); bottom: -80px; right: -100px; animation-delay: -4s; }
  .orb3 { width: 300px; height: 300px; background: radial-gradient(circle, rgba(52,211,153,0.12), transparent 70%); top: 50%; left: 50%; transform: translate(-50%,-50%); animation-delay: -2s; }

  @keyframes float {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-30px) scale(1.05); }
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 100px;
    padding: 6px 18px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 32px;
    animation: fadeDown 0.8s ease both;
  }
  .badge::before { content: '●'; font-size: 8px; animation: blink 1.5s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 7vw, 6rem);
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 12px;
    animation: fadeDown 0.9s ease 0.1s both;
  }

  .hero-title .line1 { display: block; color: #fff; }
  .hero-title .line2 {
    display: block;
    background: linear-gradient(135deg, var(--accent), var(--accent2), var(--accent3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .hero-sub {
    font-size: 1.1rem;
    color: var(--muted);
    max-width: 580px;
    margin: 20px auto 40px;
    animation: fadeDown 1s ease 0.2s both;
  }

  .hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin-bottom: 48px;
    animation: fadeDown 1s ease 0.3s both;
  }

  .tag {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #94a3b8;
    transition: all 0.3s;
  }
  .tag:hover { border-color: var(--accent); color: var(--accent); background: rgba(56,189,248,0.08); }

  /* ─── STAT BANNER ─── */
  .stats-banner {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
    justify-content: center;
    animation: fadeDown 1s ease 0.4s both;
    perspective: 600px;
  }

  .stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 36px;
    text-align: center;
    transition: transform 0.4s, box-shadow 0.4s, border-color 0.4s;
    transform-style: preserve-3d;
    cursor: default;
    min-width: 150px;
  }
  .stat-card:hover {
    transform: translateY(-8px) rotateX(6deg) scale(1.03);
    box-shadow: 0 20px 60px rgba(56,189,248,0.2);
    border-color: var(--accent);
  }
  .stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }

  /* ─── SECTION ─── */
  section {
    position: relative;
    z-index: 1;
    max-width: 1100px;
    margin: 0 auto;
    padding: 80px 24px;
  }

  .section-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 12px;
    opacity: 0.8;
  }

  .section-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.8rem, 3.5vw, 2.6rem);
    font-weight: 700;
    color: #fff;
    margin-bottom: 40px;
  }

  .section-title span {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* ─── PIPELINE ─── */
  .pipeline {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }

  .pipe-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    transform-style: preserve-3d;
    cursor: default;
  }
  .pipe-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.4s;
  }
  .pipe-card:hover::before { transform: scaleX(1); }
  .pipe-card:hover {
    transform: translateY(-6px) rotateX(4deg);
    box-shadow: 0 24px 50px rgba(0,0,0,0.4), 0 0 0 1px rgba(56,189,248,0.2);
    border-color: rgba(56,189,248,0.3);
  }

  .pipe-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    margin-bottom: 8px;
  }
  .pipe-icon {
    font-size: 2rem;
    margin-bottom: 12px;
    display: block;
    filter: drop-shadow(0 0 10px currentColor);
  }
  .pipe-name {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
  }
  .pipe-desc { font-size: 0.875rem; color: var(--muted); line-height: 1.6; }

  /* ─── TECH GRID ─── */
  .tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  .tech-item {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.3s;
    transform-style: preserve-3d;
  }
  .tech-item:hover {
    transform: translateY(-4px) rotateX(5deg) rotateY(-3deg);
    border-color: var(--accent);
    box-shadow: 0 12px 30px rgba(56,189,248,0.15);
  }
  .tech-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .tech-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #cbd5e1;
  }

  /* ─── ARCHITECTURE BOX ─── */
  .arch-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 40px;
    perspective: 1000px;
  }

  .arch-flow {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0;
    justify-content: center;
  }

  .arch-node {
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 12px;
    padding: 14px 20px;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--accent);
    transition: all 0.3s;
    white-space: nowrap;
  }
  .arch-node:hover {
    background: rgba(56,189,248,0.15);
    transform: scale(1.05);
    box-shadow: var(--glow);
  }
  .arch-node.highlight {
    background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(129,140,248,0.2));
    border-color: var(--accent2);
    color: #fff;
  }

  .arch-arrow {
    color: var(--muted);
    font-size: 1.2rem;
    padding: 0 8px;
  }

  /* ─── CODE BLOCK ─── */
  .code-block {
    background: #0a0f1a;
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 14px;
    padding: 28px 32px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.8;
    overflow-x: auto;
    position: relative;
  }
  .code-block::before {
    content: '● ● ●';
    position: absolute;
    top: 14px; left: 20px;
    color: #334155;
    font-size: 10px;
    letter-spacing: 4px;
  }
  .code-block pre { padding-top: 20px; }
  .c-comment { color: #4a6a8a; }
  .c-cmd { color: var(--accent3); }
  .c-path { color: var(--accent); }
  .c-flag { color: var(--gold); }
  .c-kw { color: var(--accent2); }

  /* ─── BUCKET TABLE ─── */
  .bucket-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 14px;
  }

  .bucket {
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    transform-style: preserve-3d;
    cursor: default;
  }
  .bucket:hover { transform: translateY(-8px) rotateX(5deg) scale(1.02); }
  .bucket.green { background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(16,185,129,0.05)); border: 1px solid rgba(52,211,153,0.3); }
  .bucket.yellow { background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.05)); border: 1px solid rgba(251,191,36,0.3); }
  .bucket.orange { background: linear-gradient(135deg, rgba(251,146,60,0.12), rgba(234,88,12,0.05)); border: 1px solid rgba(251,146,60,0.3); }
  .bucket.red { background: linear-gradient(135deg, rgba(248,113,113,0.12), rgba(239,68,68,0.05)); border: 1px solid rgba(248,113,113,0.3); }

  .bucket-name {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 8px;
  }
  .bucket.green .bucket-name { color: #34d399; }
  .bucket.yellow .bucket-name { color: #fbbf24; }
  .bucket.orange .bucket-name { color: #fb923c; }
  .bucket.red .bucket-name { color: #f87171; }

  .bucket-desc { font-size: 0.85rem; color: var(--muted); line-height: 1.5; }

  /* ─── FEATURE GRID ─── */
  .feat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
  }

  .feat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.35s;
    transform-style: preserve-3d;
  }
  .feat-card:hover {
    transform: translateY(-5px) rotateX(4deg) rotateY(2deg);
    border-color: var(--accent2);
    box-shadow: 0 20px 40px rgba(129,140,248,0.15);
  }
  .feat-icon { font-size: 1.6rem; margin-bottom: 12px; }
  .feat-title { font-family: 'Syne', sans-serif; font-weight: 700; color: #fff; margin-bottom: 6px; }
  .feat-desc { font-size: 0.875rem; color: var(--muted); }

  /* ─── DIVIDER ─── */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 0 24px;
  }

  /* ─── FOOTER ─── */
  footer {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 60px 24px;
    border-top: 1px solid var(--border);
  }
  .footer-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
  }
  .footer-role { color: var(--muted); font-size: 0.9rem; margin-bottom: 20px; }
  .footer-links { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
  .footer-link {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    color: var(--muted);
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    transition: all 0.3s;
  }
  .footer-link:hover { color: var(--accent); border-color: var(--accent); background: rgba(56,189,248,0.08); }

  /* ─── ANIMATIONS ─── */
  @keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.7s ease, transform 0.7s ease;
  }
  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }

  /* ─── SCROLLBAR ─── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }

  /* ─── HIGHLIGHT BAR ─── */
  .highlight-bar {
    background: linear-gradient(135deg, rgba(56,189,248,0.08), rgba(129,140,248,0.08));
    border: 1px solid rgba(129,140,248,0.25);
    border-radius: 16px;
    padding: 24px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 0.95rem;
    color: #cbd5e1;
  }
  .highlight-bar strong { color: #fff; }
</style>
</head>
<body>

<!-- ═══ HERO ═══ -->
<div class="hero">
  <div class="hero-orb orb1"></div>
  <div class="hero-orb orb2"></div>
  <div class="hero-orb orb3"></div>

  <div class="badge">Production-Grade SAP Automation</div>

  <h1 class="hero-title">
    <span class="line1">GR/IR Clearing</span>
    <span class="line2">Automation Engine</span>
  </h1>

  <p class="hero-sub">
    An intelligent TF-IDF + Rule-Based pipeline that automatically reconciles Goods Receipt / Invoice Receipt discrepancies in SAP — cutting manual effort by up to <strong style="color:#38bdf8">80%</strong>.
  </p>

  <div class="hero-tags">
    <span class="tag">Python 3.11</span>
    <span class="tag">SAP Integration</span>
    <span class="tag">TF-IDF NLP</span>
    <span class="tag">Scikit-Learn</span>
    <span class="tag">Streamlit Dashboard</span>
    <span class="tag">RapidFuzz</span>
    <span class="tag">Pandas</span>
    <span class="tag">Plotly</span>
  </div>

  <div class="stats-banner">
    <div class="stat-card">
      <div class="stat-num">80%</div>
      <div class="stat-label">Manual Effort Saved</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">4</div>
      <div class="stat-label">Decision Buckets</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">8</div>
      <div class="stat-label">Pipeline Steps</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">∞</div>
      <div class="stat-label">SAP Items Processed</div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══ ABOUT ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// overview</p>
    <h2 class="section-title">What is <span>GR/IR Automation?</span></h2>
    <div class="highlight-bar" style="margin-bottom:28px;">
      <span style="font-size:1.4rem;">💡</span>
      <span>In SAP, GR/IR (Goods Receipt / Invoice Receipt) accounts accumulate unmatched debit/credit line items. Manual clearing is time-consuming and error-prone. This engine automates the entire matching and clearing workflow using ML + rule-based scoring.</span>
    </div>
    <div class="feat-grid">
      <div class="feat-card">
        <div class="feat-icon">🔍</div>
        <div class="feat-title">Intelligent Matching</div>
        <div class="feat-desc">TF-IDF cosine similarity + RapidFuzz fuzzy matching to reconcile vendor names across GR and IR documents.</div>
      </div>
      <div class="feat-card">
        <div class="feat-icon">⚖️</div>
        <div class="feat-title">Weighted Rule Scoring</div>
        <div class="feat-desc">Multi-criteria rule engine scores each item pair on amount tolerance, date proximity, PO references, and more.</div>
      </div>
      <div class="feat-card">
        <div class="feat-icon">🤖</div>
        <div class="feat-title">Auto-Posting to SAP</div>
        <div class="feat-desc">HIGH confidence matches are automatically posted via SAP RFC calls — zero human touch needed.</div>
      </div>
      <div class="feat-card">
        <div class="feat-icon">📊</div>
        <div class="feat-title">Live Dashboard</div>
        <div class="feat-desc">Streamlit dashboard with real-time Plotly charts to monitor pipeline results, cash unlocked, and exception queues.</div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ PIPELINE ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// pipeline</p>
    <h2 class="section-title">8-Step <span>Processing Pipeline</span></h2>
    <div class="pipeline">
      <div class="pipe-card">
        <div class="pipe-num">STEP 01</div>
        <span class="pipe-icon">⚙️</span>
        <div class="pipe-name">Load Configuration</div>
        <div class="pipe-desc">Reads <code style="color:#38bdf8;font-family:monospace">config/config.yaml</code> — thresholds, SAP connection params, scoring weights, file paths.</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 02</div>
        <span class="pipe-icon">📥</span>
        <div class="pipe-name">Extract SAP Data</div>
        <div class="pipe-desc">Pulls open GR/IR line items from SAP export, cleans and normalises vendor names, amounts, and dates.</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 03</div>
        <span class="pipe-icon">🧠</span>
        <div class="pipe-name">TF-IDF Matching</div>
        <div class="pipe-desc">Vectorises vendor strings, computes cosine similarity matrix. RapidFuzz handles abbreviations and typos.</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 04</div>
        <span class="pipe-icon">📐</span>
        <div class="pipe-name">Rule-Based Scoring</div>
        <div class="pipe-desc">Weighted scoring across: amount delta %, date tolerance, PO match, currency, company code, and TF-IDF score.</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 05</div>
        <span class="pipe-icon">🪣</span>
        <div class="pipe-name">Decision Bucketing</div>
        <div class="pipe-desc">Items bucketed into AUTO-CLEAR, REVIEW, HOLD, or ESCALATE based on composite confidence score.</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 06</div>
        <span class="pipe-icon">📋</span>
        <div class="pipe-name">Summary Report</div>
        <div class="pipe-desc">Logs bucket distribution, percentages, and total cash-to-unlock (₹ value of AUTO-CLEAR items).</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 07</div>
        <span class="pipe-icon">📁</span>
        <div class="pipe-name">Save Excel Reports</div>
        <div class="pipe-desc">Exports each bucket to a separate Excel sheet in <code style="color:#38bdf8;font-family:monospace">data/output/</code> with formatted columns.</div>
      </div>
      <div class="pipe-card">
        <div class="pipe-num">STEP 08</div>
        <span class="pipe-icon">🚀</span>
        <div class="pipe-name">Auto-Post to SAP</div>
        <div class="pipe-desc">Calls SAP RFC <code style="color:#38bdf8;font-family:monospace">BAPI_ACC_GL_POSTING_POST</code> for HIGH-confidence items. Returns a posting log.</div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ ARCHITECTURE ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// architecture</p>
    <h2 class="section-title">System <span>Architecture</span></h2>
    <div class="arch-box">
      <div class="arch-flow">
        <div class="arch-node highlight">SAP Export / RFC</div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">extractor.py</div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">tfidf_matcher.py</div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">rule_scorer.py</div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">Decision Buckets</div>
        <div class="arch-arrow">→</div>
        <div class="arch-node highlight">poster.py → SAP</div>
      </div>
      <div style="margin-top:24px; display:flex; gap:12px; flex-wrap:wrap; justify-content:center;">
        <div class="arch-node" style="font-size:11px; color:#818cf8;">📊 Streamlit Dashboard</div>
        <div class="arch-node" style="font-size:11px; color:#818cf8;">📝 Loguru Logger</div>
        <div class="arch-node" style="font-size:11px; color:#818cf8;">📁 Excel Reports</div>
        <div class="arch-node" style="font-size:11px; color:#818cf8;">⚙️ config.yaml</div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ DECISION BUCKETS ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// output</p>
    <h2 class="section-title">Decision <span>Buckets</span></h2>
    <div class="bucket-grid">
      <div class="bucket green">
        <div class="bucket-name">🟢 AUTO-CLEAR</div>
        <div class="bucket-desc">High confidence match. Posted directly to SAP via RFC. No human review needed. Cash unlocked immediately.</div>
      </div>
      <div class="bucket yellow">
        <div class="bucket-name">🟡 REVIEW</div>
        <div class="bucket-desc">Moderate confidence. Analyst reviews in dashboard and approves or rejects the suggested match.</div>
      </div>
      <div class="bucket orange">
        <div class="bucket-name">🟠 HOLD</div>
        <div class="bucket-desc">Low confidence or partial match. Flagged for senior review. Possibly needs vendor/PO master data fix.</div>
      </div>
      <div class="bucket red">
        <div class="bucket-name">🔴 ESCALATE</div>
        <div class="bucket-desc">Very low score or anomaly detected. Sent to AP team for dispute resolution or SAP master data correction.</div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ TECH STACK ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// stack</p>
    <h2 class="section-title">Tech <span>Stack</span></h2>
    <div class="tech-grid">
      <div class="tech-item"><div class="tech-dot" style="background:#38bdf8"></div><span class="tech-name">Python 3.11</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#fbbf24"></div><span class="tech-name">pandas 2.1</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#a78bfa"></div><span class="tech-name">scikit-learn</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#34d399"></div><span class="tech-name">rapidfuzz</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#f472b6"></div><span class="tech-name">streamlit</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#fb923c"></div><span class="tech-name">plotly</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#38bdf8"></div><span class="tech-name">openpyxl</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#818cf8"></div><span class="tech-name">loguru</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#fbbf24"></div><span class="tech-name">PyYAML</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#34d399"></div><span class="tech-name">pytest</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#f87171"></div><span class="tech-name">SAP RFC (pyrfc)</span></div>
      <div class="tech-item"><div class="tech-dot" style="background:#a78bfa"></div><span class="tech-name">numpy 1.26</span></div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ QUICK START ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// quickstart</p>
    <h2 class="section-title">Get Started <span>in 4 Steps</span></h2>

    <div class="code-block" style="margin-bottom:16px;">
      <pre><span class="c-comment"># 1. Clone the repository</span>
<span class="c-cmd">git</span> clone https://github.com/your-username/grir-automation.git
<span class="c-cmd">cd</span> grir-automation

<span class="c-comment"># 2. Create virtual environment &amp; install dependencies</span>
<span class="c-cmd">python</span> <span class="c-flag">-m</span> venv venv
<span class="c-cmd">source</span> venv/bin/activate  <span class="c-comment"># Windows: venv\Scripts\activate</span>
<span class="c-cmd">pip</span> install <span class="c-flag">-r</span> requirements.txt

<span class="c-comment"># 3. Configure SAP connection</span>
<span class="c-cmd">cp</span> config/config.example.yaml config/config.yaml
<span class="c-comment"># Edit config.yaml with your SAP host, client, credentials</span>

<span class="c-comment"># 4. Run the pipeline</span>
<span class="c-cmd">python</span> main.py</pre>
    </div>

    <div class="code-block">
      <pre><span class="c-comment"># Launch the Streamlit dashboard</span>
<span class="c-cmd">streamlit</span> run <span class="c-path">dashboard/app.py</span>

<span class="c-comment"># Run tests</span>
<span class="c-cmd">pytest</span> <span class="c-flag">-v</span></pre>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ PROJECT STRUCTURE ═══ -->
<section>
  <div class="reveal">
    <p class="section-tag">// structure</p>
    <h2 class="section-title">Project <span>Structure</span></h2>
    <div class="code-block">
      <pre><span class="c-path">grir-automation/</span>
├── <span class="c-kw">main.py</span>                   <span class="c-comment"># Pipeline entry point</span>
├── <span class="c-kw">requirements.txt</span>
├── <span class="c-path">config/</span>
│   ├── config.yaml            <span class="c-comment"># Thresholds, weights, SAP params</span>
│   └── config.example.yaml    <span class="c-comment"># Template (safe to commit)</span>
├── <span class="c-path">src/</span>
│   ├── extractor.py           <span class="c-comment"># SAP data loading &amp; cleaning</span>
│   ├── tfidf_matcher.py       <span class="c-comment"># TF-IDF + fuzzy vendor matching</span>
│   ├── rule_scorer.py         <span class="c-comment"># Weighted scoring &amp; bucketing</span>
│   └── poster.py              <span class="c-comment"># SAP RFC auto-posting</span>
├── <span class="c-path">dashboard/</span>
│   └── app.py                 <span class="c-comment"># Streamlit UI</span>
├── <span class="c-path">data/</span>
│   ├── input/                 <span class="c-comment"># SAP raw exports (gitignored)</span>
│   └── output/                <span class="c-comment"># Excel reports (gitignored)</span>
└── <span class="c-path">logs/</span>
    └── pipeline.log           <span class="c-comment"># Rotating log (gitignored)</span></pre>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══ FOOTER ═══ -->
<footer>
  <div class="footer-name">GR/IR Clearing Automation Engine</div>
  <div class="footer-role">Built with Python · SAP Integration · NLP · Streamlit</div>
  <div class="footer-links">
    <a class="footer-link" href="#">📁 GitHub Repo</a>
    <a class="footer-link" href="#">📊 Live Dashboard</a>
    <a class="footer-link" href="#">📧 Contact</a>
  </div>
  <p style="color:#1e293b;font-size:12px;margin-top:32px;font-family:'JetBrains Mono',monospace;">
    © 2025 — Made with precision for SAP Finance Automation
  </p>
</footer>

<script>
  // Scroll reveal
  const reveals = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => e.target.classList.add('visible'), i * 80);
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  reveals.forEach(r => observer.observe(r));

  // 3D card tilt on mousemove
  document.querySelectorAll('.pipe-card, .feat-card, .stat-card, .tech-item, .bucket').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      card.style.transform = `translateY(-8px) rotateX(${-y * 12}deg) rotateY(${x * 12}deg) scale(1.02)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });

  // Animate stat numbers on scroll
  const statNums = document.querySelectorAll('.stat-num');
  const statTargets = ['80%', '4', '8', '∞'];
  const statObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.animation = 'fadeDown 0.6s ease both';
        statObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  statNums.forEach(s => statObserver.observe(s));
</script>

</body>
</html>
