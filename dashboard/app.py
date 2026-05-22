
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import date, timedelta
import io

# ── PAGE CONFIG ─────────────────────────────────────────────────
st.set_page_config(
    page_title="GR/IR Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SETTINGS ─────────────────────────────────────────────────────
REAL_DATA        = False
CLEARED_XLSX     = "data/output/cleared_items.xlsx"
POSTING_LOG_CSV  = "data/output/posting_log.csv"

# ── COLORS ───────────────────────────────────────────────────────
GREEN  = "#059669"
AMBER  = "#d97706"
BLUE   = "#2563eb"
RED    = "#dc2626"
PURPLE = "#7c3aed"
TEAL   = "#0d9488"
ORANGE = "#ea580c"
NAVY   = "#1e3a5f"

# ── BASE PLOTLY THEME (applied to every figure) ──────────────────
PBASE = dict(
    font=dict(family="DM Sans, sans-serif", size=11.5, color="#1f2937"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,252,0.6)",
    margin=dict(l=12, r=12, t=42, b=12),
)

# Dark outline style reused on every bar/slice
BAR_LINE  = dict(color="rgba(0,0,0,0.30)", width=1.6)
PIE_LINE  = dict(color="rgba(255,255,255,0.85)", width=2.8)
GRID_CLR  = "rgba(0,0,0,0.07)"
AXIS_CLR  = "rgba(0,0,0,0.15)"

def _apply_axes(fig, xtitle="", ytitle="", angle=0, secondary=False):
    """Apply consistent grid + axis styling."""
    fig.update_xaxes(
        gridcolor=GRID_CLR, gridwidth=1,
        linecolor=AXIS_CLR, linewidth=1.2,
        tickangle=angle,
        title_text=xtitle,
        title_font=dict(size=11),
        showgrid=True, zeroline=False,
    )
    fig.update_yaxes(
        gridcolor=GRID_CLR, gridwidth=1,
        linecolor=AXIS_CLR, linewidth=1.2,
        title_text=ytitle,
        title_font=dict(size=11),
        showgrid=True, zeroline=False,
    )
    return fig

def snum(s):
    return pd.to_numeric(s, errors="coerce").fillna(0)

def fmtcr(v):
    if v >= 1e7:  return f"₹{v/1e7:.2f}Cr"
    if v >= 1e5:  return f"₹{v/1e5:.1f}L"
    return f"₹{v:,.0f}"

# ── SAMPLE DATA ──────────────────────────────────────────────────
@st.cache_data
def make_data():
    random.seed(42); np.random.seed(42)
    vendors = [
        ("V001","Tata Consultancy Services Ltd","IT Services"),
        ("V002","Infosys Limited","IT Services"),
        ("V003","Wipro Limited","IT Services"),
        ("V004","HCL Technologies Ltd","IT Services"),
        ("V005","Tech Mahindra Limited","IT Services"),
        ("V006","Larsen & Toubro Infotech","Engineering"),
        ("V007","Siemens Ltd","Engineering"),
        ("V008","ABB India Limited","Engineering"),
        ("V009","Reliance Industries Ltd","Manufacturing"),
        ("V010","Tata Steel Limited","Manufacturing"),
    ]
    vvariants = {
        "V001":["TCS Ltd","Tata Consultancy Svcs","T.C.S. Limited"],
        "V002":["Infosys Ltd","INFOSYS LIMITED","Infosys Technologies"],
        "V003":["Wipro Ltd","WIPRO LIMITED","Wipro Technologies"],
        "V004":["HCL Tech Ltd","HCL TECHNOLOGIES","HCL Tech"],
        "V005":["Tech Mahindra Ltd","TechMahindra","Tech-Mahindra"],
        "V006":["L&T Infotech","LTI Limited","Larsen Toubro Infotech"],
        "V007":["Siemens India Ltd","SIEMENS LIMITED","Siemens India"],
        "V008":["ABB India Ltd","ABB LIMITED","A.B.B. India"],
        "V009":["Reliance Inds Ltd","RELIANCE INDUSTRIES","RIL"],
        "V010":["Tata Steel Ltd","TATA STEEL LIMITED","Tatasteel"],
    }
    today = date(2025, 3, 31)
    recs  = []
    for i in range(200):
        vc, vn, vs = random.choice(vendors)
        gr_date  = today - timedelta(days=random.randint(5,180))
        base_amt = round(random.uniform(50000, 2000000), 2)
        po_num   = f"45{random.randint(10000000,99999999)}"
        sc_list  = ["EXACT MATCH","ROUNDING - PAISE","ROUNDING - RUPEE",
                    "TDS DEDUCTED","GST MISMATCH","PARTIAL INVOICE",
                    "TIMING DIFF","MISSING INVOICE","DUPLICATE IR"]
        sc_wt    = [0.12,0.18,0.15,0.12,0.12,0.10,0.11,0.06,0.04]
        scenario = random.choices(sc_list, weights=sc_wt)[0]
        ir_vname = random.choice(vvariants[vc])
        ir_date  = gr_date + timedelta(days=random.randint(1,60))

        if scenario == "EXACT MATCH":
            ir_amt,diff = base_amt, 0.0; ir_vname = vn
        elif scenario == "ROUNDING - PAISE":
            ir_amt = round(base_amt+random.choice([-0.5,-0.25,0.25,0.5]),2); diff=round(ir_amt-base_amt,2)
        elif scenario == "ROUNDING - RUPEE":
            ir_amt = round(base_amt+random.choice([-5,-2,-1,1,2,5]),2); diff=round(ir_amt-base_amt,2)
        elif scenario == "TDS DEDUCTED":
            tds=round(base_amt*random.choice([0.01,0.02,0.05,0.10]),2); ir_amt=round(base_amt-tds,2); diff=round(ir_amt-base_amt,2)
        elif scenario == "GST MISMATCH":
            gst=round(base_amt*random.choice([0.05,0.12,0.18,0.28]),2); ir_amt=round(base_amt+gst,2); diff=round(ir_amt-base_amt,2)
        elif scenario == "PARTIAL INVOICE":
            ir_amt=round(base_amt*random.choice([0.25,0.50,0.75]),2); diff=round(ir_amt-base_amt,2)
        elif scenario == "TIMING DIFF":
            ir_date=gr_date+timedelta(days=random.randint(61,120)); ir_amt=base_amt; diff=0.0
        elif scenario == "MISSING INVOICE":
            ir_amt=None; ir_vname="-"; diff=None
        else:
            ir_amt=base_amt; diff=base_amt

        aging=(today-gr_date).days
        if aging<=30:     bucket="0-30 Days"
        elif aging<=60:   bucket="31-60 Days"
        elif aging<=90:   bucket="61-90 Days"
        else:             bucket=">90 Days"

        if scenario=="EXACT MATCH":
            score=round(random.uniform(90,99),1); dec="AUTO-CLEAR"
        elif scenario in ("ROUNDING - PAISE","ROUNDING - RUPEE"):
            score=round(random.uniform(80,92),1); dec="AUTO-CLEAR"
        elif scenario in ("TIMING DIFF","TDS DEDUCTED","GST MISMATCH"):
            score=round(random.uniform(55,79),1); dec="REVIEW"
        elif scenario=="PARTIAL INVOICE":
            score=round(random.uniform(40,60),1); dec="HOLD"
        elif scenario=="MISSING INVOICE":
            score=round(random.uniform(20,40),1); dec="ESCALATE"
        else:
            score=round(random.uniform(10,30),1); dec="ESCALATE"

        tfidf=round(random.uniform(0.4,0.95) if scenario!="MISSING INVOICE" else random.uniform(0.0,0.2),3)
        vmq  ="HIGH" if tfidf>=0.65 else "MEDIUM" if tfidf>=0.45 else "LOW"

        recs.append({
            "Sr No":i+1,"PO Number":po_num,
            "Vendor Code":vc,"Vendor Name":vn,"Vendor Sector":vs,
            "GR Document No":f"500{random.randint(1000000,9999999)}",
            "GR Posting Date":gr_date,"GR Amount":base_amt,
            "GR Vendor Name (SAP)":vn,
            "IR Document No":f"510{random.randint(1000000,9999999)}",
            "IR Posting Date":ir_date,"IR Amount":ir_amt,
            "IR Vendor Name (Invoice)":ir_vname,
            "Difference (IR-GR)":diff,
            "Currency":random.choices(["INR","INR","INR","USD","EUR"],[60,60,60,10,10])[0],
            "Plant":random.choice(["1001","1002","1003","1004"]),
            "Aging (Days)":aging,"Aging Bucket":bucket,
            "Discrepancy Flag":scenario,
            "confidence_score":score,"tfidf_vendor_score":tfidf,
            "vendor_match_quality":vmq,"decision":dec,
        })

    df  = pd.DataFrame(recs)
    ac  = df[df["decision"]=="AUTO-CLEAR"].copy()
    rv  = df[df["decision"]=="REVIEW"].copy()
    hd  = df[df["decision"]=="HOLD"].copy()
    esc = df[df["decision"]=="ESCALATE"].copy()

    pl_rows=[]
    for _,row in ac.iterrows():
        ok=random.random()<0.96
        pl_rows.append({
            "gr_document":row["GR Document No"],
            "ir_document":row["IR Document No"],
            "po_number":row["PO Number"],
            "vendor_code":row["Vendor Code"],
            "gr_amount":row["GR Amount"],
            "confidence_score":row["confidence_score"],
            "status":"CLEARED" if ok else "FAILED",
            "sap_clearing_doc":f"190{random.randint(10000000,99999999)}" if ok else None,
            "posting_date":str(date.today()),
            "error_msg":None if ok else "SAP lock: doc in use",
        })
    pl = pd.DataFrame(pl_rows)
    return df,ac,rv,hd,esc,pl

# ── LOAD DATA ─────────────────────────────────────────────────────
if REAL_DATA:
    try:
        ac  = pd.read_excel(CLEARED_XLSX, sheet_name="AUTO-CLEAR")
        rv  = pd.read_excel(CLEARED_XLSX, sheet_name="REVIEW QUEUE")
        hd  = pd.read_excel(CLEARED_XLSX, sheet_name="HOLD")
        esc = pd.read_excel(CLEARED_XLSX, sheet_name="ESCALATE")
        pl  = pd.read_csv(POSTING_LOG_CSV)
        all_df = pd.concat([ac,rv,hd,esc],ignore_index=True)
        st.sidebar.success("✅ Real data loaded")
    except Exception as e:
        st.sidebar.warning(f"Real data load fail: {e}\nSample data use ho raha hai.")
        all_df,ac,rv,hd,esc,pl = make_data()
else:
    all_df,ac,rv,hd,esc,pl = make_data()

total    = len(all_df)
total_gr = snum(all_df["GR Amount"]).sum()
cash_ul  = snum(ac["GR Amount"]).sum()
cleared_ok = len(pl[pl["status"]=="CLEARED"]) if "status" in pl.columns else len(pl)

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 GR/IR Dashboard")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠 Overview",
        "📊 Decision Analysis",
        "🏢 Vendor Analysis",
        "⏳ Aging & Trends",
        "🔍 Review Queue",
        "📝 Posting Log",
        "🚨 Escalation",
    ])
    st.markdown("---")
    st.markdown("**Filters**")
    curr_opts   = ["All"] + sorted(all_df["Currency"].dropna().unique().tolist())
    sel_curr    = st.selectbox("Currency", curr_opts)
    vendor_opts = ["All"] + sorted(all_df["Vendor Code"].dropna().unique().tolist())
    sel_vendor  = st.selectbox("Vendor", vendor_opts)
    st.markdown("---")
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.caption(f"Date: {date.today()}")
    st.caption("Company: 1000 | TF-IDF Engine")

def filt(df):
    if df is None or df.empty: return df
    if sel_curr!="All" and "Currency" in df.columns:
        df=df[df["Currency"]==sel_curr]
    if sel_vendor!="All" and "Vendor Code" in df.columns:
        df=df[df["Vendor Code"]==sel_vendor]
    return df

# ================================================================
# PAGE: OVERVIEW
# ================================================================
if "Overview" in page:
    st.title("📊 GR/IR Clearing Dashboard")
    st.caption(f"Company: 1000 | Engine: TF-IDF + Rule-Based | {date.today()}")
    st.divider()

    # KPIs
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("📦 Total Items",   f"{total:,}",      f"GR: {fmtcr(total_gr)}")
    k2.metric("✅ Auto-Cleared",  f"{len(ac):,}",    f"{round(len(ac)/max(total,1)*100,1)}%")
    k3.metric("🔍 Review",        f"{len(rv):,}",    "Manual check")
    k4.metric("⏸️ On Hold",       f"{len(hd):,}",    "Low score")
    k5.metric("🚨 Escalate",      f"{len(esc):,}",   "Urgent")
    k6.metric("💸 Cash Unlocked", fmtcr(cash_ul),    f"{cleared_ok} posted")

    st.divider()

    # ── Row 2: Donut + Stacked Bar ─────────────────────────────────
    c1,c2 = st.columns([1,2])

    with c1:
        st.subheader("Where Each Item Ended Up")
        fig = go.Figure(go.Pie(
            labels=["Auto-Clear","Review","Hold","Escalate"],
            values=[len(ac),len(rv),len(hd),len(esc)],
            hole=0.58,
            marker=dict(
                colors=[GREEN, AMBER, BLUE, RED],
                line=PIE_LINE,
            ),
            textinfo="label+percent",
            textfont=dict(size=11.5, family="DM Sans, sans-serif"),
            hovertemplate="<b>%{label}</b><br>Items: %{value}<br>Share: %{percent}<extra></extra>",
            pull=[0.03, 0, 0, 0.04],
        ))
        fig.add_annotation(
            text=f"<b>{total}</b><br><span style='font-size:11px'>Total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#111827"),
        )
        fig.update_layout(
            **PBASE, height=310,
            showlegend=True,
            legend=dict(orientation="h", y=-0.18, x=0.05,
                        font=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("What's Causing Mismatches — and What We Did About It")
        fg = (all_df.groupby(["Discrepancy Flag","decision"])
              .size().reset_index(name="count"))
        cm = {"AUTO-CLEAR": GREEN, "REVIEW": AMBER, "HOLD": BLUE, "ESCALATE": RED}
        fig2 = px.bar(
            fg, x="count", y="Discrepancy Flag", color="decision",
            orientation="h", text="count", color_discrete_map=cm,
            labels={"count": "Items", "Discrepancy Flag": ""},
        )
        fig2.update_traces(
            textposition="inside",
            textfont=dict(size=10, color="white", family="DM Sans, sans-serif"),
            marker_line=BAR_LINE,
        )
        fig2.update_layout(
            **PBASE, height=310,
            barmode="stack",
            bargap=0.22,
            legend=dict(title="Decision", orientation="h",
                        y=-0.22, x=0, font=dict(size=11)),
        )
        _apply_axes(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Row 3: Histogram + Aging ────────────────────────────────────
    c3,c4 = st.columns(2)

    with c3:
        st.subheader("How Confident the System Was — Score Spread")
        scores = snum(all_df["confidence_score"])
        fig3 = go.Figure()
        # Shaded zones
        fig3.add_vrect(x0=80, x1=100, fillcolor=GREEN,  opacity=0.06, line_width=0,
                       annotation_text="Auto-Clear Zone",
                       annotation_font=dict(size=9, color=GREEN),
                       annotation_position="top left")
        fig3.add_vrect(x0=55, x1=80,  fillcolor=AMBER,  opacity=0.06, line_width=0,
                       annotation_text="Review Zone",
                       annotation_font=dict(size=9, color=AMBER),
                       annotation_position="top left")
        fig3.add_vrect(x0=0,  x1=55,  fillcolor=RED,    opacity=0.04, line_width=0,
                       annotation_text="Hold Zone",
                       annotation_font=dict(size=9, color=RED),
                       annotation_position="top left")
        fig3.add_trace(go.Histogram(
            x=scores, nbinsx=25,
            marker=dict(
                color=BLUE, opacity=0.80,
                line=dict(color="rgba(0,0,0,0.28)", width=1.4),
            ),
            hovertemplate="Score %{x}<br>Items: %{y}<extra></extra>",
            name="Items",
        ))
        fig3.add_vline(x=80, line_dash="dash", line_color=GREEN, line_width=1.8,
                       annotation_text="80", annotation_font=dict(color=GREEN, size=10))
        fig3.add_vline(x=55, line_dash="dash", line_color=AMBER, line_width=1.8,
                       annotation_text="55", annotation_font=dict(color=AMBER, size=10))
        fig3.update_layout(
            **PBASE, height=310, showlegend=False,
            xaxis=dict(title="Score (0–100)", tickvals=list(range(0,101,10)),
                       gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            yaxis=dict(title="Number of Items",
                       gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            bargap=0.06,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("How Long Items Have Been Waiting")
        border = ["0-30 Days","31-60 Days","61-90 Days",">90 Days"]
        ag = (all_df.groupby("Aging Bucket")
              .agg(Items=("GR Amount","count"),
                   Amount=("GR Amount", lambda x: snum(x).sum()))
              .reset_index())
        ag["Aging Bucket"] = pd.Categorical(ag["Aging Bucket"],
                                             categories=border, ordered=True)
        ag = ag.sort_values("Aging Bucket")
        age_colors = [GREEN, AMBER, ORANGE, RED]
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(go.Bar(
            x=ag["Aging Bucket"], y=ag["Items"],
            marker=dict(color=age_colors, line=BAR_LINE, opacity=0.88),
            text=ag["Items"], textposition="outside",
            textfont=dict(size=11, color="#1f2937"),
            name="Items",
            hovertemplate="%{x}<br><b>%{y} items</b><extra></extra>",
        ), secondary_y=False)
        fig4.add_trace(go.Scatter(
            x=ag["Aging Bucket"], y=ag["Amount"]/1e5,
            name="Amount (₹L)", mode="lines+markers",
            line=dict(color=PURPLE, width=2.8),
            marker=dict(size=9, color=PURPLE,
                        line=dict(color="white", width=2.5)),
            hovertemplate="%{x}<br><b>₹%{y:.1f}L</b><extra></extra>",
        ), secondary_y=True)
        fig4.update_layout(
            **PBASE, height=310,
            bargap=0.25,
            legend=dict(orientation="h", y=-0.22, font=dict(size=11)),
        )
        fig4.update_xaxes(gridcolor=GRID_CLR, linecolor=AXIS_CLR)
        fig4.update_yaxes(title_text="Number of Items",  secondary_y=False,
                          gridcolor=GRID_CLR, linecolor=AXIS_CLR)
        fig4.update_yaxes(title_text="Amount (₹L)", secondary_y=True,
                          gridcolor=GRID_CLR, linecolor=AXIS_CLR, showgrid=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ── Row 4: VMQ + GR vs IR ────────────────────────────────────────
    c5,c6 = st.columns(2)

    with c5:
        st.subheader("How Well Vendor Names Were Matched")
        vmq = all_df["vendor_match_quality"].value_counts().reset_index()
        vmq.columns = ["Quality","Count"]
        vmq["Quality"] = pd.Categorical(vmq["Quality"], ["HIGH","MEDIUM","LOW"], ordered=True)
        vmq = vmq.sort_values("Quality")
        vmq_colors = {"HIGH": GREEN, "MEDIUM": AMBER, "LOW": RED}
        fig5 = go.Figure()
        for _, row in vmq.iterrows():
            fig5.add_trace(go.Bar(
                x=[row["Quality"]], y=[row["Count"]],
                name=row["Quality"],
                marker=dict(color=vmq_colors[row["Quality"]], line=BAR_LINE, opacity=0.88),
                text=[row["Count"]], textposition="outside",
                textfont=dict(size=12, color="#1f2937"),
                hovertemplate=f"<b>{row['Quality']}</b><br>Items: {row['Count']}<extra></extra>",
            ))
        fig5.update_layout(
            **PBASE, height=290, showlegend=False,
            bargap=0.30,
        )
        _apply_axes(fig5, ytitle="Items")
        st.plotly_chart(fig5, use_container_width=True)

    with c6:
        st.subheader("Purchase Amount vs Invoice Amount by Issue Type")
        fa = (all_df.groupby("Discrepancy Flag")
              .agg(GR=("GR Amount", lambda x: snum(x).sum()),
                   IR=("IR Amount", lambda x: snum(x).sum()))
              .reset_index())
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=fa["Discrepancy Flag"], y=fa["GR"]/1e5,
            name="GR (Purchase)",
            marker=dict(color=BLUE, line=BAR_LINE, opacity=0.88),
            hovertemplate="%{x}<br>GR: ₹%{y:.1f}L<extra></extra>",
        ))
        fig6.add_trace(go.Bar(
            x=fa["Discrepancy Flag"], y=fa["IR"]/1e5,
            name="IR (Invoice)",
            marker=dict(color=TEAL, line=BAR_LINE, opacity=0.75),
            hovertemplate="%{x}<br>IR: ₹%{y:.1f}L<extra></extra>",
        ))
        fig6.update_layout(
            **PBASE, height=290,
            barmode="group",
            bargap=0.22, bargroupgap=0.06,
            xaxis=dict(tickangle=-30, tickfont_size=9,
                       gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            yaxis=dict(title="Amount (₹L)",
                       gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            legend=dict(orientation="h", y=-0.30, font=dict(size=11)),
        )
        st.plotly_chart(fig6, use_container_width=True)


# ================================================================
# PAGE: DECISION ANALYSIS
# ================================================================
elif "Decision" in page:
    st.title("📊 Decision Analysis")
    st.divider()

    c1,c2 = st.columns(2)

    with c1:
        st.subheader("Confidence Score Range per Decision Type")
        fig1 = go.Figure()
        box_palette = {
            "AUTO-CLEAR": GREEN, "REVIEW": AMBER,
            "HOLD": BLUE, "ESCALATE": RED
        }
        for dec, clr in box_palette.items():
            sub = snum(all_df[all_df["decision"]==dec]["confidence_score"])
            if len(sub):
                fig1.add_trace(go.Box(
                    y=sub, name=dec,
                    marker=dict(color=clr, size=5,
                                line=dict(color="rgba(0,0,0,0.35)", width=1.2)),
                    line=dict(color="rgba(0,0,0,0.40)", width=1.8),
                    fillcolor=clr,
                    opacity=0.82,
                    boxmean=True,
                    hovertemplate=f"<b>{dec}</b><br>Score: %{{y}}<extra></extra>",
                ))
        fig1.update_layout(
            **PBASE, height=360, showlegend=False,
            yaxis=dict(title="Confidence Score (0–100)",
                       gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            xaxis=dict(linecolor=AXIS_CLR),
            boxgap=0.35,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Which Issues Lead to Which Decisions")
        hmap = pd.crosstab(all_df["Discrepancy Flag"], all_df["decision"])
        fig2 = go.Figure(go.Heatmap(
            z=hmap.values,
            x=hmap.columns.tolist(),
            y=hmap.index.tolist(),
            colorscale=[
                [0.0, "#f0f9ff"],
                [0.4, "#60a5fa"],
                [0.7, "#2563eb"],
                [1.0, "#1e3a5f"],
            ],
            text=hmap.values,
            texttemplate="<b>%{text}</b>",
            textfont=dict(size=13, family="DM Sans, sans-serif"),
            showscale=True,
            colorbar=dict(
                thickness=14, len=0.85,
                tickfont=dict(size=10),
                outlinecolor="rgba(0,0,0,0.2)", outlinewidth=1,
            ),
            xgap=2, ygap=2,
            hovertemplate="Issue: <b>%{y}</b><br>Decision: <b>%{x}</b><br>Items: <b>%{z}</b><extra></extra>",
        ))
        fig2.update_layout(
            **PBASE, height=360,
            xaxis=dict(title="Decision", linecolor=AXIS_CLR, tickfont=dict(size=11)),
            yaxis=dict(title="", linecolor=AXIS_CLR, tickfont=dict(size=10)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Summary — What Happened to All Items")
    rows=[]
    for lbl,dfb,em in [("AUTO-CLEAR",ac,"✅"),("REVIEW",rv,"🔍"),
                        ("HOLD",hd,"⏸️"),("ESCALATE",esc,"🚨")]:
        gr=snum(dfb["GR Amount"]).sum()
        ir=snum(dfb["IR Amount"]).sum()
        sc=snum(dfb.get("confidence_score",pd.Series())).mean()
        rows.append({
            "Decision": f"{em} {lbl}",
            "Items": len(dfb),
            "% Share": f"{round(len(dfb)/max(total,1)*100,1)}%",
            "GR Amount": fmtcr(gr),
            "IR Amount": fmtcr(ir),
            "Avg Score": f"{sc:.1f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ================================================================
# PAGE: VENDOR ANALYSIS
# ================================================================
elif "Vendor" in page:
    st.title("🏢 Vendor Analysis")
    st.divider()

    vg = (all_df.groupby("Vendor Code").agg(
        Name       =("Vendor Name","first"),
        Sector     =("Vendor Sector","first"),
        Items      =("GR Amount","count"),
        GR_Amt     =("GR Amount", lambda x: snum(x).sum()),
        IR_Amt     =("IR Amount", lambda x: snum(x).sum()),
        Avg_Score  =("confidence_score", lambda x: snum(x).mean()),
        Auto_Clear =("decision", lambda x: (x=="AUTO-CLEAR").sum()),
        Review     =("decision", lambda x: (x=="REVIEW").sum()),
        Hold       =("decision", lambda x: (x=="HOLD").sum()),
        Escalate   =("decision", lambda x: (x=="ESCALATE").sum()),
    ).reset_index())
    vg["Auto_Rate"] = (vg["Auto_Clear"]/vg["Items"]*100).round(1)
    vg = vg.sort_values("GR_Amt", ascending=False)

    c1,c2 = st.columns(2)

    with c1:
        st.subheader("Top Vendors by Purchase Amount")
        top = vg.head(10)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=top["GR_Amt"]/1e5, y=top["Vendor Code"],
            orientation="h", name="GR (Purchase)",
            marker=dict(color=BLUE, line=BAR_LINE, opacity=0.88),
            text=[fmtcr(v) for v in top["GR_Amt"]],
            textposition="inside",
            textfont=dict(color="white", size=10),
            hovertemplate="%{y}<br>GR: ₹%{x:.1f}L<extra></extra>",
        ))
        fig1.add_trace(go.Bar(
            x=top["IR_Amt"]/1e5, y=top["Vendor Code"],
            orientation="h", name="IR (Invoice)",
            marker=dict(color=TEAL, line=BAR_LINE, opacity=0.55),
            hovertemplate="%{y}<br>IR: ₹%{x:.1f}L<extra></extra>",
        ))
        fig1.update_layout(
            **PBASE, height=380,
            barmode="overlay",
            bargap=0.22,
            xaxis=dict(title="Amount (₹L)", gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            yaxis=dict(linecolor=AXIS_CLR),
            legend=dict(orientation="h", y=-0.18, font=dict(size=11)),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("How Often Each Vendor Gets Auto-Approved (%)")
        fig2 = go.Figure(go.Bar(
            x=vg["Vendor Code"],
            y=vg["Auto_Rate"],
            marker=dict(
                color=vg["Auto_Rate"],
                colorscale=[[0, RED], [0.4, AMBER], [1, GREEN]],
                cmin=0, cmax=100,
                showscale=True,
                colorbar=dict(
                    title=dict(text="%", font=dict(size=11)),
                    thickness=13, len=0.8,
                    outlinecolor="rgba(0,0,0,0.2)", outlinewidth=1,
                    tickfont=dict(size=10),
                ),
                line=BAR_LINE,
                opacity=0.88,
            ),
            text=[f"{v:.0f}%" for v in vg["Auto_Rate"]],
            textposition="outside",
            textfont=dict(size=11),
            hovertemplate="%{x}<br>Auto-Clear Rate: <b>%{y:.1f}%</b><extra></extra>",
        ))
        fig2.add_hline(
            y=80, line_dash="dash", line_color=GREEN, line_width=2,
            annotation_text="Target: 80%",
            annotation_font=dict(size=10, color=GREEN),
            annotation_position="top right",
        )
        fig2.update_layout(
            **PBASE, height=380,
            bargap=0.30,
            yaxis=dict(title="Auto-Clear %", range=[0, 118],
                       gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            xaxis=dict(tickangle=-30, linecolor=AXIS_CLR),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Vendor-Wise Breakdown Table")
    sv = vg.copy()
    sv["GR_Amt"]    = sv["GR_Amt"].apply(fmtcr)
    sv["IR_Amt"]    = sv["IR_Amt"].apply(fmtcr)
    sv["Avg_Score"] = sv["Avg_Score"].apply(lambda x: f"{x:.1f}")
    sv["Auto_Rate"] = sv["Auto_Rate"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(sv[["Vendor Code","Name","Sector","Items","GR_Amt",
                      "IR_Amt","Avg_Score","Auto_Rate","Auto_Clear",
                      "Review","Hold","Escalate"]].rename(columns={
        "Name":"Vendor","GR_Amt":"GR Amount","IR_Amt":"IR Amount",
        "Avg_Score":"Avg Score","Auto_Rate":"Auto %",
        "Auto_Clear":"Auto-Clear"}),
        use_container_width=True, hide_index=True)


# ================================================================
# PAGE: AGING & TRENDS
# ================================================================
elif "Aging" in page:
    st.title("⏳ Aging & Trends")
    st.divider()

    c1,c2 = st.columns(2)

    with c1:
        st.subheader("Items Pending — Grouped by Time Waiting")
        border = ["0-30 Days","31-60 Days","61-90 Days",">90 Days"]
        ag = (all_df.groupby("Aging Bucket")
              .agg(Items=("GR Amount","count"),
                   Amount=("GR Amount", lambda x: snum(x).sum()),
                   Esc=("decision", lambda x: (x=="ESCALATE").sum()))
              .reset_index())
        ag["Aging Bucket"] = pd.Categorical(ag["Aging Bucket"],
                                             categories=border, ordered=True)
        ag = ag.sort_values("Aging Bucket")
        age_colors = [GREEN, AMBER, ORANGE, RED]
        fig1 = go.Figure()
        for idx, (_, row) in enumerate(ag.iterrows()):
            fig1.add_trace(go.Bar(
                x=[row["Aging Bucket"]], y=[row["Items"]],
                name=row["Aging Bucket"],
                marker=dict(color=age_colors[idx], line=BAR_LINE, opacity=0.88),
                text=[row["Items"]], textposition="outside",
                textfont=dict(size=12),
                hovertemplate=f"{row['Aging Bucket']}<br><b>{row['Items']} items</b><extra></extra>",
            ))
        fig1.update_layout(
            **PBASE, height=310, showlegend=False,
            bargap=0.28,
        )
        _apply_axes(fig1, ytitle="Number of Items")
        st.plotly_chart(fig1, use_container_width=True)
        ag2 = ag.copy()
        ag2["Amount"] = ag2["Amount"].apply(fmtcr)
        ag2["% Share"] = ag2["Items"].apply(lambda x: f"{round(x/max(total,1)*100,1)}%")
        st.dataframe(
            ag2[["Aging Bucket","Items","% Share","Amount","Esc"]].rename(
                columns={"Esc":"Escalated"}),
            use_container_width=True, hide_index=True,
        )

    with c2:
        st.subheader("Month-by-Month Volume and Value")
        all_df["GR Posting Date"] = pd.to_datetime(all_df["GR Posting Date"], errors="coerce")
        monthly = (all_df.dropna(subset=["GR Posting Date"])
                   .assign(Month=lambda d: d["GR Posting Date"].dt.to_period("M"))
                   .groupby("Month").agg(
                       Items=("GR Amount","count"),
                       Amount=("GR Amount", lambda x: snum(x).sum()))
                   .reset_index())
        monthly["Month"] = monthly["Month"].astype(str)
        monthly = monthly.tail(12)
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(
            x=monthly["Month"], y=monthly["Items"],
            name="Items",
            marker=dict(color=BLUE, line=BAR_LINE, opacity=0.80),
            hovertemplate="%{x}<br>Items: <b>%{y}</b><extra></extra>",
        ), secondary_y=False)
        fig2.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Amount"]/1e5,
            name="Amount (₹L)", mode="lines+markers",
            line=dict(color=GREEN, width=2.8),
            marker=dict(size=8, color=GREEN,
                        line=dict(color="white", width=2.5)),
            hovertemplate="%{x}<br>Amount: ₹<b>%{y:.1f}L</b><extra></extra>",
        ), secondary_y=True)
        fig2.update_layout(
            **PBASE, height=310,
            bargap=0.22,
            xaxis=dict(tickangle=-30, gridcolor=GRID_CLR, linecolor=AXIS_CLR),
            legend=dict(orientation="h", y=-0.28, font=dict(size=11)),
        )
        fig2.update_yaxes(title_text="Items", secondary_y=False,
                          gridcolor=GRID_CLR, linecolor=AXIS_CLR)
        fig2.update_yaxes(title_text="Amount (₹L)", secondary_y=True,
                          gridcolor=GRID_CLR, linecolor=AXIS_CLR, showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)


# ================================================================
# PAGE: REVIEW QUEUE
# ================================================================
elif "Review" in page:
    st.title("🔍 Review Queue")
    rv_f = filt(rv.copy())
    st.warning(f"⚠️ {len(rv_f)} items need a manual look (confidence score: 55–79)")
    st.divider()

    fc1,fc2,fc3 = st.columns(3)
    with fc1:
        flags = ["All"] + sorted(rv_f["Discrepancy Flag"].dropna().unique().tolist())
        sf    = st.selectbox("Filter by Issue Type", flags)
        if sf!="All": rv_f=rv_f[rv_f["Discrepancy Flag"]==sf]
    with fc2:
        mn = st.slider("Minimum Confidence Score", 0, 100, 55)
        rv_f = rv_f[snum(rv_f["confidence_score"]) >= mn]
    with fc3:
        srt = st.selectbox("Sort By", ["confidence_score","GR Amount","Aging (Days)"])
        if srt in rv_f.columns:
            rv_f = rv_f.sort_values(srt, ascending=False)

    st.info(f"Showing {len(rv_f)} items")
    scols = [c for c in ["PO Number","Vendor Code","GR Vendor Name (SAP)",
                          "IR Vendor Name (Invoice)","GR Amount","IR Amount",
                          "Difference (IR-GR)","tfidf_vendor_score",
                          "confidence_score","Discrepancy Flag","Aging (Days)"]
             if c in rv_f.columns]
    st.dataframe(rv_f[scols], use_container_width=True, height=400, hide_index=True)

    d1,d2 = st.columns(2)
    with d1:
        st.download_button("⬇️ Download as CSV", rv_f.to_csv(index=False).encode(),
                           "review_queue.csv", "text/csv", use_container_width=True)
    with d2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            rv_f.to_excel(w, index=False)
        st.download_button("⬇️ Download as Excel", buf.getvalue(),
                           "review_queue.xlsx",
                           "application/vnd.ms-excel", use_container_width=True)


# ================================================================
# PAGE: POSTING LOG
# ================================================================
elif "Posting" in page:
    st.title("📝 SAP Posting Log")
    st.divider()

    if pl.empty:
        st.info("No posting log found. Run main.py first.")
    else:
        ok_pl   = pl[pl["status"]=="CLEARED"] if "status" in pl.columns else pl
        fail_pl = pl[pl["status"]=="FAILED"]  if "status" in pl.columns else pd.DataFrame()
        ok_cash = snum(ok_pl.get("gr_amount", pd.Series())).sum()
        sr      = round(len(ok_pl)/max(len(pl),1)*100, 1)

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total Posted",  f"{len(pl):,}")
        m2.metric("✅ Cleared",    f"{len(ok_pl):,}",  f"{sr}% success")
        m3.metric("❌ Failed",     f"{len(fail_pl):,}")
        m4.metric("Cash Cleared",  fmtcr(ok_cash))

        st.divider()
        c1,c2 = st.columns([1,2])

        with c1:
            st.subheader("Posting Success Rate")
            fig1 = go.Figure(go.Pie(
                labels=["Cleared","Failed"],
                values=[len(ok_pl), max(len(fail_pl), 0)],
                hole=0.58,
                marker=dict(
                    colors=[GREEN, RED],
                    line=PIE_LINE,
                ),
                textinfo="label+percent",
                textfont=dict(size=11.5),
                pull=[0.03, 0.06],
                hovertemplate="<b>%{label}</b><br>%{value} items<extra></extra>",
            ))
            fig1.add_annotation(
                text=f"<b>{sr}%</b><br><span style='font-size:11px'>Success</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#111827"),
            )
            fig1.update_layout(**PBASE, height=270, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader("Recently Posted Items")
            scl = [c for c in ["gr_document","ir_document","po_number","vendor_code",
                                "gr_amount","confidence_score","status",
                                "sap_clearing_doc","posting_date"] if c in pl.columns]
            st.dataframe(pl[scl].head(50), use_container_width=True,
                         height=270, hide_index=True)

        if not fail_pl.empty:
            st.error(f"❌ {len(fail_pl)} items failed — retry needed")
            st.dataframe(fail_pl, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Download Full Posting Log",
            pl.to_csv(index=False).encode(),
            "posting_log.csv", "text/csv",
        )


# ================================================================
# PAGE: ESCALATION
# ================================================================
elif "Escalation" in page:
    st.title("🚨 Escalation Center")
    st.divider()
    esc_f = filt(esc.copy())

    if esc_f.empty:
        st.success("✅ No escalated items! Everything looks clean.")
    else:
        st.error(f"🚨 {len(esc_f)} items need immediate action!")

        if "Discrepancy Flag" in esc_f.columns:
            ce = st.columns(len(esc_f["Discrepancy Flag"].unique()))
            for i,(fl,cnt) in enumerate(esc_f["Discrepancy Flag"].value_counts().items()):
                with ce[i]:
                    st.metric(fl, cnt, "Needs action")

        st.divider()
        st.warning("🔴 **MISSING INVOICE:** Contact the vendor — if invoice doesn't arrive in 30 days, consider cancelling the PO.")
        st.error("🟠 **DUPLICATE IR:** Verify with AP team immediately — fraud check required.")

        se = [c for c in ["PO Number","Vendor Code","GR Vendor Name (SAP)",
                           "GR Amount","IR Amount","Discrepancy Flag",
                           "Aging (Days)","Aging Bucket","confidence_score"]
              if c in esc_f.columns]
        st.dataframe(esc_f[se], use_container_width=True, height=380, hide_index=True)
        st.download_button(
            "⬇️ Download Escalation List",
            esc_f.to_csv(index=False).encode(),
            "escalation.csv", "text/csv",
        )