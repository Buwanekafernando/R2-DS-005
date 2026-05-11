# ui/app.py
# Run with: python -m streamlit run ui/app.py

import sys
import os
import json
import requests
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title = "NeuroMark AI — Dual System Agent",
    page_icon  = "🧠",
    layout     = "wide",
    initial_sidebar_state = "collapsed"
)

API_URL = "http://localhost:8000"

CATEGORIES = [
    "Beauty", "Electronics", "Apparel", "Grocery",
    "Baby", "Pet Products", "Sports", "Home & Kitchen",
    "Automotive", "Industrial", "Unknown"
]

# ════════════════════════════════════════════════════════
# GLOBAL CSS — NeuroMark template design system
# ════════════════════════════════════════════════════════
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">

<style>
:root {
  --bg:            #F4F2ED;
  --surface:       #FDFCF9;
  --border:        rgba(0,0,0,0.10);
  --text-primary:  #1A1916;
  --text-secondary:#6B6860;
  --text-muted:    #A09E9A;
  --blue-50:#E6F1FB;  --blue-100:#B5D4F4;  --blue-600:#185FA5;  --blue-800:#0C447C;
  --coral-50:#FAECE7; --coral-100:#F5C4B3; --coral-400:#D85A30; --coral-600:#993C1D; --coral-800:#712B13;
  --amber-50:#FAEEDA; --amber-100:#FAC775; --amber-400:#BA7517; --amber-600:#854F0B;
  --purple-50:#EEEDFE;--purple-100:#CECBF6;--purple-600:#534AB7;--purple-800:#3C3489;
  --teal-50:#E1F5EE;  --teal-100:#9FE1CB;  --teal-400:#1D9E75;  --teal-600:#0F6E56;
  --radius-sm:8px; --radius-md:12px; --radius-lg:18px;
}
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text-primary) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.7)} }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

/* NAV */
.nm-nav {
  background:var(--surface); border-bottom:1px solid var(--border);
  padding:0 40px; height:60px;
  display:flex; align-items:center; justify-content:space-between;
}
.nm-logo { font-family:'Syne',sans-serif; font-weight:800; font-size:20px; color:var(--text-primary); letter-spacing:-0.5px; display:flex; align-items:center; gap:10px; }
.nm-logo-dot { width:10px;height:10px;border-radius:50%;background:var(--coral-400);display:inline-block;animation:pulse 1.8s infinite; }
.nm-badge { font-size:11px;background:var(--purple-50);color:var(--purple-800);border:1px solid var(--purple-100);padding:3px 10px;border-radius:20px;font-weight:500; }
.api-pill { font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px; }
.api-pill.online  { background:var(--teal-50);  color:var(--teal-600);  border:1px solid var(--teal-100); }
.api-pill.offline { background:var(--coral-50); color:var(--coral-600); border:1px solid var(--coral-100); }

/* HERO */
.nm-hero { padding:48px 40px 32px;max-width:1280px;margin:0 auto;display:flex;align-items:flex-start;justify-content:space-between;gap:40px; }
.hero-tag { display:inline-flex;align-items:center;gap:6px;font-size:12px;text-transform:uppercase;letter-spacing:1.2px;color:var(--teal-600);font-weight:500;margin-bottom:16px;background:var(--teal-50);padding:5px 12px;border-radius:20px;border:1px solid var(--teal-100); }
.hero-tag::before { content:'';width:6px;height:6px;border-radius:50%;background:var(--teal-400);animation:pulse 1.8s infinite; }
.nm-h1 { font-family:'Syne',sans-serif;font-size:46px;font-weight:800;line-height:1.05;letter-spacing:-1.5px;color:var(--text-primary);margin-bottom:16px; }
.nm-h1 em { font-style:normal;color:var(--coral-400); }
.hero-sub { font-size:15px;color:var(--text-secondary);max-width:500px;line-height:1.7;font-weight:300; }
.stat-chips { display:flex;flex-direction:column;gap:10px;min-width:210px;padding-top:16px; }
.stat-chip { background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-md);padding:12px 16px;display:flex;gap:12px;align-items:center; }
.sci { width:34px;height:34px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0; }
.sci-blue{background:var(--blue-50)} .sci-coral{background:var(--coral-50)} .sci-amber{background:var(--amber-50)} .sci-teal{background:var(--teal-50)}
.sc-label{font-size:10px;color:var(--text-muted)} .sc-value{font-size:13px;font-weight:500;color:var(--text-primary);font-family:'Syne',sans-serif}

/* CARD */
.nm-card { background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;margin-bottom:20px; }
.nm-card-header { padding:15px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between; }
.nm-card-title { font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:var(--text-primary);letter-spacing:-.2px; }
.nm-card-body { padding:20px; }

/* FIELD LABEL */
.field-label { font-size:11px;font-weight:500;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;display:block; }

/* STREAMLIT INPUT OVERRIDES */
.stTextArea textarea { font-family:'DM Sans',sans-serif !important;font-size:14px !important;color:var(--text-primary) !important;background:var(--bg) !important;border:1px solid var(--border) !important;border-radius:var(--radius-sm) !important;padding:12px 14px !important;line-height:1.6 !important;resize:none !important; }
.stTextArea textarea:focus { border-color:var(--coral-400) !important;box-shadow:none !important; }
.stTextArea label, .stSelectbox label { display:none !important; }
.stSelectbox > div > div { background:var(--bg) !important;border:1px solid var(--border) !important;border-radius:var(--radius-sm) !important;font-family:'DM Sans',sans-serif !important;font-size:14px !important;color:var(--text-primary) !important; }

/* BUTTONS */
.stButton > button { width:100% !important;padding:13px !important;background:var(--text-primary) !important;color:#fff !important;border:none !important;border-radius:var(--radius-md) !important;font-family:'Syne',sans-serif !important;font-size:14px !important;font-weight:700 !important;letter-spacing:-.2px !important;transition:opacity .2s !important; }
.stButton > button:hover { opacity:.85 !important; }
.stButton > button:disabled { opacity:.4 !important; }
.stButton > button p { font-family:'Syne',sans-serif !important;font-weight:700 !important; }
.stDownloadButton > button { background:var(--surface) !important;color:var(--text-secondary) !important;border:1px solid var(--border) !important;border-radius:var(--radius-sm) !important;font-size:13px !important;font-weight:500 !important;font-family:'DM Sans',sans-serif !important;padding:9px 18px !important;width:auto !important; }
.stDownloadButton > button:hover { border-color:var(--text-primary) !important;color:var(--text-primary) !important; }

/* RESULTS */
.clf-badge { border-radius:var(--radius-md);padding:14px 18px;margin-bottom:10px;border:1px solid; }
.clf-mode { font-size:15px;font-weight:600;margin-bottom:8px;font-family:'Syne',sans-serif; }
.clf-bar-wrap { background:rgba(0,0,0,0.08);border-radius:4px;height:8px;overflow:hidden;margin:6px 0 4px; }
.clf-bar { height:8px;border-radius:4px; }
.clf-probs { font-size:11px;margin-top:6px;display:flex;gap:14px; }
.copy-grid { display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px; }
.copy-card { border-radius:var(--radius-md);padding:14px 16px;border:1px solid;min-height:130px; }
.copy-label { font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px; }
.copy-text { font-size:13px;line-height:1.65; }
.copy-meta { font-size:11px;margin-top:10px;opacity:.75; }
.strategy-box { border-radius:var(--radius-md);padding:12px 16px;margin-top:14px;display:flex;align-items:flex-start;gap:12px;border:1px solid; }
.strategy-box-label { font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px; }
.strategy-box-text { font-size:13px;line-height:1.55; }
.metrics-row { display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px;padding-top:16px;border-top:1px solid var(--border); }
.metric-box { text-align:center;padding:12px;background:var(--bg);border-radius:var(--radius-sm); }
.metric-val { font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:var(--text-primary); }
.metric-lbl { font-size:11px;color:var(--text-muted);margin-top:2px; }

/* EMPTY STATE */
.empty-state { text-align:center;padding:48px 20px; }
.empty-icon { width:60px;height:60px;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius-md);display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto 16px; }
.empty-title { font-family:'Syne',sans-serif;font-size:16px;font-weight:700;margin-bottom:6px; }
.empty-desc { font-size:13px;color:var(--text-muted);max-width:260px;margin:0 auto; }

/* FOOTER */
.nm-footer { border-top:1px solid var(--border);padding:18px 40px;display:flex;align-items:center;justify-content:space-between;background:var(--surface);margin-top:20px; }
.nm-footer p { font-size:12px;color:var(--text-muted); }
.team-row { display:flex;align-items:center;gap:6px; }
.avatar { width:26px;height:26px;border-radius:50%;border:2px solid var(--surface);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;color:#fff;margin-left:-8px; }
.avatar:first-child { margin-left:0; }
.av-a{background:var(--blue-600)} .av-b{background:var(--coral-400)} .av-c{background:var(--amber-400)} .av-d{background:var(--purple-600)}
.team-label { font-size:12px;color:var(--text-muted);margin-left:8px; }

::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border);border-radius:3px; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════
def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        return r.status_code == 200
    except:
        return False


def error_box(msg):
    st.markdown(f"""
    <div style="background:var(--coral-50);border:1px solid var(--coral-100);
                border-radius:var(--radius-md);padding:14px 18px;
                color:var(--coral-600);font-size:13px;margin-bottom:12px">
      {msg}
    </div>""", unsafe_allow_html=True)


def success_box(msg):
    st.markdown(f"""
    <div style="background:var(--teal-50);border:1px solid var(--teal-100);
                border-radius:var(--radius-md);padding:12px 16px;
                color:var(--teal-600);font-size:13px;font-weight:500;margin-bottom:12px">
      ✓ {msg}
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# NAV BAR
# ════════════════════════════════════════════════════════
api_online = check_api()
api_label  = "● API online"   if api_online else "● API offline"
api_cls    = "api-pill online" if api_online else "api-pill offline"

st.markdown(f"""
<div class="nm-nav">
  <div class="nm-logo">
    <span class="nm-logo-dot"></span>
    NeuroMark<span style="color:var(--coral-400)">AI</span>
    <span class="nm-badge">Component 1</span>
  </div>
  <span class="{api_cls}">{api_label}</span>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="nm-hero">
  <div>
    <div class="hero-tag">Dual Process Theory · Kahneman 2011</div>
    <div class="nm-h1">Dual System<br><em>Reasoning</em><br>Agent</div>
    <div class="hero-sub">
      Classifies consumer decision-making mode and generates
      psychologically aligned marketing copy using System 1 &amp;
      System 2 cognitive principles.
    </div>
  </div>
  <div class="stat-chips">
    <div class="stat-chip">
      <div class="sci sci-blue">🧠</div>
      <div><div class="sc-label">Classification Model</div><div class="sc-value">RoBERTa Fine-tuned</div></div>
    </div>
    <div class="stat-chip">
      <div class="sci sci-coral">✍️</div>
      <div><div class="sc-label">Copy Generation</div><div class="sc-value">Grok / Gemini LLM</div></div>
    </div>
    <div class="stat-chip">
      <div class="sci sci-amber">⚡</div>
      <div><div class="sc-label">Framework</div><div class="sc-value">Dual Process Theory</div></div>
    </div>
    <div class="stat-chip">
      <div class="sci sci-teal">🔗</div>
      <div><div class="sc-label">Pipeline Role</div><div class="sc-value">Agent 1 of 4</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# MODE TOGGLE  (replaces sidebar radio)
# ════════════════════════════════════════════════════════
if "mode" not in st.session_state:
    st.session_state.mode = "single"

st.markdown('<div style="max-width:1280px;margin:0 auto;padding:0 40px 8px;display:flex;gap:8px;">', unsafe_allow_html=True)
c1, c2, c_rest = st.columns([1.2, 1.5, 9])
with c1:
    if st.button("Single Product", key="m_single"):
        st.session_state.mode = "single"
        st.rerun()
with c2:
    if st.button("Batch Analysis", key="m_batch"):
        st.session_state.mode = "batch"
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# Active tab indicator
single_active = "background:var(--text-primary);color:#fff"
batch_active  = "background:var(--text-primary);color:#fff"
single_idle   = "background:var(--surface);color:var(--text-secondary);border:1px solid var(--border)"
batch_idle    = "background:var(--surface);color:var(--text-secondary);border:1px solid var(--border)"
st.markdown(f"""
<div style="max-width:1280px;margin:0 auto;padding:0 40px 20px;display:flex;gap:8px;">
  <span style="font-size:12px;font-weight:500;padding:4px 16px;border-radius:20px;
    {single_active if st.session_state.mode=='single' else single_idle}">
    ○ Single Product
  </span>
  <span style="font-size:12px;font-weight:500;padding:4px 16px;border-radius:20px;
    {batch_active if st.session_state.mode=='batch' else batch_idle}">
    ○ Batch Analysis
  </span>
</div>
""", unsafe_allow_html=True)

mode = st.session_state.mode


# ════════════════════════════════════════════════════════
# SINGLE PRODUCT MODE
# ════════════════════════════════════════════════════════
if mode == "single":

    st.markdown('<div style="max-width:1280px;margin:0 auto;padding:0 40px;">', unsafe_allow_html=True)
    col_left, col_right = st.columns([1.1, 1.7], gap="large")

    # ── LEFT ─────────────────────────────────────────
    with col_left:

        # Input card
        st.markdown("""
        <div class="nm-card">
          <div class="nm-card-header">
            <span class="nm-card-title">Product Input</span>
          </div>
          <div class="nm-card-body">
        """, unsafe_allow_html=True)

        st.markdown('<span class="field-label">Product Description</span>', unsafe_allow_html=True)
        product_text = st.text_area(
            label       = "desc",
            placeholder = (
                "Enter product name and description...\n\n"
                "e.g. Sony WH-1000XM5 Noise Cancelling Headphones "
                "with 30-hour battery life and industry-leading "
                "noise cancellation technology."
            ),
            height = 120,
            key    = "product_desc"
        )

        st.markdown('<span class="field-label" style="margin-top:12px;display:block">Product Category</span>', unsafe_allow_html=True)
        category = st.selectbox("cat", CATEGORIES, key="sel_category")
        st.markdown("</div></div>", unsafe_allow_html=True)

        analyze_btn = st.button(
            "Analyze & Generate Strategy ↗",
            type                = "primary",
            use_container_width = True,
            disabled            = not product_text.strip()
        )

        # Example products
        st.markdown("""
        <div class="nm-card" style="margin-top:16px">
          <div class="nm-card-header">
            <span class="nm-card-title">Example Products</span>
          </div>
          <div class="nm-card-body">
        """, unsafe_allow_html=True)

        examples = [
            ("Neutrogena Hydro Boost Water Gel Moisturizer", "Beauty"),
            ("Sony WH-1000XM5 Noise Cancelling Headphones",  "Electronics"),
            ("Haribo Gold-Bears Gummy Candy 5lb Party Bag",  "Grocery"),
            ("Garmin Forerunner 955 Solar GPS Smartwatch",   "Sports"),
            ("Fisher-Price Laugh & Learn Baby Toy Gift Set", "Baby"),
        ]

        for ex_product, ex_cat in examples:
            if st.button(f"→  {ex_product[:46]}…", key=f"ex_{ex_product}", use_container_width=True):
                st.session_state["ex_product"]  = ex_product
                st.session_state["ex_category"] = ex_cat
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # Pre-fill from example click
    if "ex_product" in st.session_state:
        product_text = st.session_state.pop("ex_product")
        category     = st.session_state.pop("ex_category", "Unknown")
        analyze_btn  = True

    # ── RIGHT ─────────────────────────────────────────
    with col_right:

        # Run analysis when button clicked
        if analyze_btn and product_text.strip():
            with st.spinner("Classifying cognitive mode and generating copy…"):
                try:
                    response = requests.post(
                        f"{API_URL}/analyze",
                        json    = {"product_text": product_text, "category": category},
                        timeout = 60
                    )
                    if response.status_code == 200:
                        st.session_state["last_result"] = response.json()
                    else:
                        error_box(f"API Error {response.status_code} — {response.text}")

                except requests.exceptions.Timeout:
                    error_box("Request timed out. Try again.")
                except requests.exceptions.ConnectionError:
                    error_box("Cannot connect to API. Run: <code>uvicorn api.main:app --reload</code>")

        # Show results
        if "last_result" in st.session_state:
            result    = st.session_state["last_result"]
            clf       = result["classification"]
            gen_copy  = result["generated_copy"]
            rec       = result["recommendation"]
            agent_out = result["agent_output"]

            mode_val   = clf["cognitive_mode"]
            confidence = clf["confidence"]
            s1_prob    = clf["s1_probability"]
            s2_prob    = clf["s2_probability"]
            strategy   = rec["strategy"]
            emo        = gen_copy["emotional"]
            rat        = gen_copy["rational"]

            # Mode colors
            if mode_val == "System1":
                bg_c, bdr_c, txt_c, bar_c = "var(--amber-50)", "var(--amber-100)", "var(--amber-600)", "var(--amber-400)"
                mode_icon, mode_label = "⚡", "System 1 — Emotional / Impulsive"
            else:
                bg_c, bdr_c, txt_c, bar_c = "var(--blue-50)", "var(--blue-100)", "var(--blue-600)", "var(--blue-600)"
                mode_icon, mode_label = "🔍", "System 2 — Rational / Deliberative"

            # ── Classification result card ────────────
            st.markdown(f"""
            <div class="nm-card" style="animation:fadeUp .4s ease">
              <div class="nm-card-header">
                <span class="nm-card-title">Classification Result</span>
                <span style="font-size:10px;background:var(--teal-50);color:var(--teal-600);
                             border:1px solid var(--teal-100);padding:2px 8px;
                             border-radius:20px;font-weight:500">RoBERTa</span>
              </div>
              <div class="nm-card-body">
                <div class="clf-badge" style="background:{bg_c};border-color:{bdr_c}">
                  <div class="clf-mode" style="color:{txt_c}">{mode_icon} {mode_label}</div>
                  <div style="font-size:11px;color:{txt_c};margin-bottom:4px">Confidence</div>
                  <div class="clf-bar-wrap">
                    <div class="clf-bar" style="width:{confidence*100:.0f}%;background:{bar_c}"></div>
                  </div>
                  <div class="clf-probs" style="color:{txt_c}">
                    <span><strong>{confidence*100:.1f}%</strong></span>
                    <span>S1: {s1_prob:.3f}</span>
                    <span>S2: {s2_prob:.3f}</span>
                  </div>
                </div>
                <div style="font-size:12px;color:var(--text-muted);font-style:italic;margin-top:8px">
                  {clf['reasoning']}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Copy cards ────────────────────────────
            is_emo_rec = strategy == "emotional"
            is_rat_rec = strategy == "rational"
            emo_bdr    = "2px solid var(--amber-400)" if is_emo_rec else "1px solid var(--amber-100)"
            rat_bdr    = "2px solid var(--blue-600)"  if is_rat_rec else "1px solid var(--blue-100)"
            emo_rec    = "✅ Recommended" if is_emo_rec else ""
            rat_rec    = "✅ Recommended" if is_rat_rec else ""

            s_bg  = "var(--amber-50)"  if strategy == "emotional" else "var(--blue-50)"
            s_bdr = "var(--amber-100)" if strategy == "emotional" else "var(--blue-100)"
            s_txt = "var(--amber-600)" if strategy == "emotional" else "var(--blue-800)"
            s_ico = "⚡"               if strategy == "emotional" else "🔍"

            st.markdown(f"""
            <div class="nm-card" style="animation:fadeUp .4s ease .1s both">
              <div class="nm-card-header">
                <span class="nm-card-title">Generated Marketing Copy</span>
              </div>
              <div class="nm-card-body">
                <div class="copy-grid">
                  <div class="copy-card" style="background:var(--amber-50);border:{emo_bdr}">
                    <div class="copy-label" style="color:var(--amber-600)">⚡ Emotional &nbsp;{emo_rec}</div>
                    <div class="copy-text" style="color:#3d2200">{emo["text"]}</div>
                    <div class="copy-meta" style="color:var(--amber-600)">
                      Sentiment: {emo["quality"]["sentiment_compound"]:.2f} &nbsp;·&nbsp;
                      Alignment: {emo["quality"]["mode_alignment"]:.0%}
                    </div>
                  </div>
                  <div class="copy-card" style="background:var(--blue-50);border:{rat_bdr}">
                    <div class="copy-label" style="color:var(--blue-800)">🔍 Rational &nbsp;{rat_rec}</div>
                    <div class="copy-text" style="color:#0a2d52">{rat["text"]}</div>
                    <div class="copy-meta" style="color:var(--blue-800)">
                      Sentiment: {rat["quality"]["sentiment_compound"]:.2f} &nbsp;·&nbsp;
                      Alignment: {rat["quality"]["mode_alignment"]:.0%}
                    </div>
                  </div>
                </div>
                <div class="strategy-box" style="background:{s_bg};border-color:{s_bdr}">
                  <span style="font-size:1.2rem">{s_ico}</span>
                  <div>
                    <div class="strategy-box-label" style="color:{s_txt}">Recommended Strategy</div>
                    <div class="strategy-box-text" style="color:{s_txt}">{rec["explanation"]}</div>
                  </div>
                </div>
                <div class="metrics-row">
                  <div class="metric-box">
                    <div class="metric-val">{confidence*100:.0f}%</div>
                    <div class="metric-lbl">Confidence</div>
                  </div>
                  <div class="metric-box">
                    <div class="metric-val">{emo["quality"]["word_count"]}</div>
                    <div class="metric-lbl">Emotional Words</div>
                  </div>
                  <div class="metric-box">
                    <div class="metric-val">{rat["quality"]["word_count"]}</div>
                    <div class="metric-lbl">Rational Words</div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── JSON output ───────────────────────────
            st.markdown("""
            <div class="nm-card" style="animation:fadeUp .4s ease .2s both">
              <div class="nm-card-header">
                <span class="nm-card-title">🔗 Output for Components 2, 3, 4</span>
              </div>
              <div class="nm-card-body">
                <div style="font-size:10px;text-transform:uppercase;letter-spacing:1px;
                            color:var(--text-muted);font-weight:500;margin-bottom:8px">
                  Agent JSON Output
                </div>
            """, unsafe_allow_html=True)

            st.json({
                "cognitive_mode":   agent_out["cognitive_mode"],
                "confidence":       agent_out["confidence"],
                "strategy":         agent_out["strategy"],
                "emotional_copy":   agent_out["emotional_copy"][:80] + "…",
                "rational_copy":    agent_out["rational_copy"][:80]  + "…",
                "recommended_copy": agent_out["recommended_copy"][:80] + "…"
            })
            st.markdown("</div></div>", unsafe_allow_html=True)

            st.download_button(
                label     = "⬇  Download full result (JSON)",
                data      = json.dumps(result, indent=2),
                file_name = "agent_result.json",
                mime      = "application/json"
            )

        else:
            st.markdown("""
            <div class="nm-card">
              <div class="nm-card-body">
                <div class="empty-state">
                  <div class="empty-icon">🧠</div>
                  <div class="empty-title">Ready to Analyze</div>
                  <div class="empty-desc">
                    Enter a product description and click
                    Analyze to classify cognitive mode and
                    generate marketing copy.
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# BATCH MODE
# ════════════════════════════════════════════════════════
else:
    st.markdown('<div style="max-width:1280px;margin:0 auto;padding:0 40px;">', unsafe_allow_html=True)

    st.markdown("""
    <div class="nm-card">
      <div class="nm-card-header">
        <span class="nm-card-title">Batch Analysis</span>
      </div>
      <div class="nm-card-body">
    """, unsafe_allow_html=True)

    st.markdown(
        '<span class="field-label">One product per line — format: Product description | Category</span>',
        unsafe_allow_html=True
    )
    batch_input = st.text_area(
        label       = "batch",
        placeholder = (
            "Sony Headphones XM5 noise cancelling | Electronics\n"
            "Neutrogena Hydro Boost face moisturizer | Beauty\n"
            "Haribo Gummy Bears party bag 5lb | Grocery"
        ),
        height = 180,
        key    = "batch_input"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    run_batch = st.button(
        "Analyze All ↗",
        type                = "primary",
        use_container_width = True,
        disabled            = not batch_input.strip()
    )

    if run_batch and batch_input.strip():
        lines   = [l.strip() for l in batch_input.strip().split("\n") if l.strip()]
        payload = []
        for line in lines:
            if "|" in line:
                parts = line.split("|")
                payload.append({
                    "product_text": parts[0].strip(),
                    "category":     parts[1].strip() if len(parts) > 1 else "Unknown"
                })
            else:
                payload.append({"product_text": line, "category": "Unknown"})

        if len(payload) > 10:
            st.markdown("""<div style="background:var(--amber-50);border:1px solid var(--amber-100);
                          border-radius:var(--radius-md);padding:12px 16px;
                          color:var(--amber-600);font-size:13px;margin-bottom:12px">
              Maximum 10 products per batch. Trimming to first 10.
            </div>""", unsafe_allow_html=True)
            payload = payload[:10]

        with st.spinner(f"Analyzing {len(payload)} products…"):
            try:
                response = requests.post(
                    f"{API_URL}/batch-analyze",
                    json    = payload,
                    timeout = 120
                )
                if response.status_code == 200:
                    batch_results = response.json()["results"]
                    success_box(f"Completed {len(batch_results)} products")

                    import pandas as pd
                    rows = []
                    for r in batch_results:
                        if r["success"]:
                            d = r["data"]
                            rows.append({
                                "Product":    d["input"]["product_text"][:50],
                                "Category":   d["input"]["category"],
                                "Mode":       d["agent_output"]["cognitive_mode"],
                                "Confidence": f"{d['agent_output']['confidence']:.0%}",
                                "Strategy":   d["agent_output"]["strategy"].capitalize(),
                            })

                    if rows:
                        st.markdown("""
                        <div class="nm-card">
                          <div class="nm-card-header">
                            <span class="nm-card-title">Batch Results</span>
                          </div>
                          <div class="nm-card-body">
                        """, unsafe_allow_html=True)
                        st.dataframe(pd.DataFrame(rows), use_container_width=True)
                        st.markdown("</div></div>", unsafe_allow_html=True)

                    st.download_button(
                        label     = "⬇  Download all results (JSON)",
                        data      = json.dumps(batch_results, indent=2),
                        file_name = "batch_results.json",
                        mime      = "application/json"
                    )

            except Exception as e:
                error_box(f"Batch analysis failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="nm-footer">
  <p>NeuroMark AI · Final Year Research Demo · BSc Data Science</p>
  <div class="team-row">
    <div class="avatar av-a">M1</div>
    <div class="avatar av-b">M2</div>
    <div class="avatar av-c">M3</div>
    <div class="avatar av-d">M4</div>
    <span class="team-label">Group of 4</span>
  </div>
</div>
""", unsafe_allow_html=True)