
import sys
import os
import requests
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components import (
    render_header,
    render_classification_badge,
    render_reasoning_tags,
    render_copy_cards,
    render_strategy_box,
    render_json_output
)

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title = "Dual System Reasoning Agent",
    page_icon  = "🧠",
    layout     = "wide"
)

API_URL = "http://localhost:8000"

CATEGORIES = [
    "Beauty", "Electronics", "Apparel", "Grocery",
    "Baby", "Pet Products", "Sports", "Home & Kitchen",
    "Automotive", "Industrial", "Unknown"
]


render_header()
st.divider()

#Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    mode = st.radio(
        "Input mode",
        ["Single product", "Batch (multiple products)"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📡 API Status")

    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        if health.status_code == 200:
            st.success("API running ✓")
        else:
            st.error("API error")
    except:
        st.error("API offline — run:\n`uvicorn api.main:app --reload`")

    st.markdown("---")
    st.markdown("### 📖 About")
    st.caption(
        "Component 1 of the Neuro-Marketing "
        "Multi-Agent System. Classifies consumer "
        "decision mode and generates "
        "psychologically aligned marketing copy "
        "using Dual Process Theory."
    )

#sigle product
if mode == "Single product":

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("#### Product Input")

        product_text = st.text_area(
            "Product description",
            placeholder=(
                "Enter product name and description...\n\n"
                "e.g. Sony WH-1000XM5 Noise Cancelling Headphones "
                "with 30-hour battery life and industry-leading "
                "noise cancellation technology."
            ),
            height=130
        )

        category = st.selectbox("Product category", CATEGORIES)

        analyze_btn = st.button(
            "🔍 Analyze & Generate Strategy",
            type="primary",
            use_container_width=True,
            disabled=not product_text.strip()
        )

    with col_right:
        st.markdown("####  Example products")

        examples = [
            ("Neutrogena Hydro Boost Water Gel Moisturizer", "Beauty"),
            ("Sony WH-1000XM5 Noise Cancelling Headphones",  "Electronics"),
            ("Haribo Gold-Bears Gummy Candy 5lb Party Bag",  "Grocery"),
            ("Garmin Forerunner 955 Solar GPS Smartwatch",   "Sports"),
            ("Fisher-Price Laugh & Learn Baby Toy Gift Set", "Baby"),
        ]

        for ex_product, ex_cat in examples:
            if st.button(
                f"  {ex_product[:45]}...",
                key=ex_product,
                use_container_width=True
            ):
                st.session_state["ex_product"] = ex_product
                st.session_state["ex_category"] = ex_cat
                st.rerun()

    # Pre-fill from example click
    if "ex_product" in st.session_state:
        product_text = st.session_state.pop("ex_product")
        category     = st.session_state.pop("ex_category", "Unknown")
        analyze_btn  = True

    # ── Run analysis ─────────────────────────────────────
    if analyze_btn and product_text.strip():

        with st.spinner("Classifying product and generating copy..."):
            try:
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={
                        "product_text": product_text,
                        "category":     category
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state["last_result"] = result
                else:
                    st.error(f"API error {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                st.error("Request timed out. The model may still be loading.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Make sure it is running.")

    # ── Display results ───────────────────────────────────
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]

        st.divider()
        st.markdown("#### 📊 Analysis Results")

        clf       = result["classification"]
        gen_copy  = result["generated_copy"]
        rec       = result["recommendation"]
        agent_out = result["agent_output"]

        # Classification badge + reasoning tags
        render_classification_badge(
            clf["cognitive_mode"],
            clf["confidence"]
        )
        render_reasoning_tags(
            clf["reasoning"],
            clf["s1_probability"],
            clf["s2_probability"]
        )

        st.caption(f"_{clf['reasoning']}_")
        st.markdown("---")

        # Copy cards
        st.markdown("#### ✍️ Generated Marketing Copy")
        render_copy_cards(
            emotional_copy        = gen_copy["emotional"]["text"],
            rational_copy         = gen_copy["rational"]["text"],
            recommended_strategy  = rec["strategy"],
            emo_quality           = gen_copy["emotional"]["quality"],
            rat_quality           = gen_copy["rational"]["quality"]
        )

        # Strategy recommendation
        render_strategy_box(rec["strategy"], rec["explanation"])

        # JSON output for teammates
        st.markdown("---")
        with st.expander("🔗 JSON Output for Components 2, 3, 4"):
            render_json_output(agent_out)

        # Download button
        import json
        st.download_button(
            label     = "⬇️ Download full result (JSON)",
            data      = json.dumps(result, indent=2),
            file_name = "agent_result.json",
            mime      = "application/json"
        )


# ════════════════════════════════════════════════════════
# BATCH MODE
# ════════════════════════════════════════════════════════
else:
    st.markdown("#### 📋 Batch Analysis")
    st.caption("Enter one product per line in format: `Product description | Category`")

    batch_input = st.text_area(
        "Products (one per line)",
        placeholder=(
            "Sony Headphones XM5 noise cancelling | Electronics\n"
            "Neutrogena Hydro Boost face moisturizer | Beauty\n"
            "Haribo Gummy Bears party bag 5lb | Grocery"
        ),
        height=180
    )

    if st.button("🔍 Analyze All", type="primary",
                 disabled=not batch_input.strip()):

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
            st.warning("Maximum 10 products per batch. Trimming to first 10.")
            payload = payload[:10]

        with st.spinner(f"Analyzing {len(payload)} products..."):
            try:
                response = requests.post(
                    f"{API_URL}/batch-analyze",
                    json    = payload,
                    timeout = 120
                )

                if response.status_code == 200:
                    batch_results = response.json()["results"]

                    st.success(
                        f"Completed {len(batch_results)} products"
                    )

                    # Summary table
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
                        st.dataframe(
                            pd.DataFrame(rows),
                            use_container_width=True
                        )

                    # Download all results
                    import json
                    st.download_button(
                        label     = "⬇️ Download all results (JSON)",
                        data      = json.dumps(batch_results, indent=2),
                        file_name = "batch_results.json",
                        mime      = "application/json"
                    )

            except Exception as e:
                st.error(f"Batch analysis failed: {e}")