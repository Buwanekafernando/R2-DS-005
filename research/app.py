import streamlit as st
import base64
import json
import time
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Explicitly specify the .env file path in the research directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

from scarcity_agent import ScarcityAgent
from pain_point_extractor import extract_pain_points_detailed, get_extractor
from review_reader import get_product_pain_profile

# Set Page Config
st.set_page_config(
    page_title="NeuroMark AI — Agentic Neuro-Marketing System",
    page_icon="🧠",
    layout="wide",
)

# --- CSS INJECTION (From neuromark_ui.html) ---
ST_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #F4F2ED;
    --surface: #FDFCF9;
    --border: rgba(0,0,0,0.10);
    --text-primary: #1A1916;
    --text-secondary: #6B6860;
    --text-muted: #A09E9A;
    --coral-400: #D85A30;
    --teal-600: #0F6E56;
    --teal-400: #1D9E75;
    --teal-50: #E1F5EE;
    --blue-50: #E6F1FB;
    --blue-600: #185FA5;
    --coral-50: #FAECE7;
    --amber-50: #FAEEDA;
    --amber-400: #BA7517;
    --amber-100: #FAC775;
    --purple-50: #EEEDFE;
    --purple-600: #534AB7;
    --radius-md: 12px;
    --radius-lg: 18px;
    --radius-sm: 8px;
}

/* Base Overrides */
.stApp {
    background-color: var(--bg);
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

/* NAV */
.custom-nav {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 40px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 1000;
}
.nav-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 20px;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-logo-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--coral-400);
}
.nav-badge {
    font-size: 11px;
    background: #EEEDFE;
    color: #3C3489;
    border: 1px solid #CECBF6;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 500;
}

/* HERO */
.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--teal-600);
    font-weight: 500;
    margin-bottom: 16px;
    background: var(--teal-50);
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid #9FE1CB;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -1.5px;
    color: var(--text-primary);
    margin-bottom: 18px;
}
.hero h1 em { font-style: normal; color: var(--coral-400); }
.hero-sub {
    font-size: 15px;
    color: var(--text-secondary);
    max-width: 520px;
    line-height: 1.6;
    font-weight: 300;
}

/* CARDS */
.custom-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    margin-bottom: 24px;
}
.card-header {
    padding: 18px 22px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 700;
}
.card-body { padding: 22px; }

/* AGENTS */
.agents-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}
.agent-card {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 16px;
    background: var(--surface);
}
.agent-card.active { border-color: var(--coral-400); background: var(--coral-50); }
.agent-card.done { border-color: #1D9E75; background: #E1F5EE; }

.agent-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    margin-bottom: 10px;
}
.agent-name { font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; }
.agent-theory { font-size: 10px; color: var(--text-muted); margin-bottom: 8px; }

/* STRATEGY BLOCKS */
.strategy-headline {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 800;
    padding: 14px;
    border-radius: 12px;
    background: #F4F2ED;
    border-left: 4px solid;
    margin-bottom: 12px;
    color: black !important;
}
.strategy-copy { font-size: 14px; line-height: 1.6; color: var(--text-secondary); }

/* Streamlit Widget Hiding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom text colors */
.customer-sentiment, .system-intensity, .ai-recommendation, .scarcity-strategies, .product-description {
    color: black !important;
}

/* Market category and product search labels */
.stSelectbox label, .stTextInput label {
    color: black !important;
}

/* Product buttons - white text always */
.stButton button {
    color: white !important;
    background-color: #1f77b4 !important;
    border: 1px solid #1f77b4 !important;
}

.stButton button:hover {
    background-color: #155a8a !important;
    border-color: #155a8a !important;
}

/* Selected product text */
.selected-product {
    color: black !important;
    font-weight: bold;
}

/* Checkbox text */
.stCheckbox label {
    color: black !important;
}

/* Agent analytics text */
.agent-analytics, .agent-analytics * {
    color: black !important;
}
</style>
"""

st.markdown(ST_CSS, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'review_pain_points' not in st.session_state:
    st.session_state.review_pain_points = None
if 'product_profile' not in st.session_state:
    st.session_state.product_profile = None

# Initialize ScarcityAgent with error handling
try:
    agent_logic = ScarcityAgent()
except ValueError as e:
    st.error(f"⚠️ Configuration Error: {str(e)}")
    st.info("Please ensure XAI_API_KEY is set in the .env file in the research directory.")
    st.stop()

# --- NAVBAR ---
st.markdown("""
<div class="custom-nav">
  <div class="nav-logo">
    <div class="nav-logo-dot"></div>
    Scarcity<span style="color:var(--coral-400)">Agent</span>
  </div>
</div>
""", unsafe_allow_html=True)

# --- HERO ---
st.markdown("""
<div class="hero">
    <div class="hero-tag">Component 3 · Scarcity Optimization</div>
    <h1>The Psychology of<br><em>Urgency.</em></h1>
    <p class="hero-sub">An autonomous AI agent designed to strategically incorporate <b>Scarcity-based elements</b> into marketing content to drive consumer action while maintaining brand authenticity.</p>
</div>
""", unsafe_allow_html=True)

st.write("---")

# --- MAIN DASHBOARD ---
col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    st.markdown('<div class="card-header"><span class="card-title">Product & Context Input</span></div>', unsafe_allow_html=True)
    with st.container():
        # Load from Dataset if available
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sample_file = os.path.join(script_dir, "sample_products.json")
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Step 1: Select Category
            unique_cats = sorted(list(set(p['category'] for p in data)))
            selected_cat = st.selectbox("Select Market Category", unique_cats)
            
            # Step 2: Search and select product
            product_search = st.text_input("Search Product", placeholder="Type to search products...")
            
            # Filter products based on search
            if product_search:
                filtered_products = [p for p in data if p['category'] == selected_cat and product_search.lower() in p['name'].lower()]
                if filtered_products:
                    # Show matching products as a list
                    st.markdown("**Matching Products:**")
                    for i, product in enumerate(filtered_products[:10]):  # Limit to 10 results
                        if st.button(f"{product['name']}", key=f"product_{i}"):
                            st.session_state.selected_product = product
                            st.rerun()
                    if len(filtered_products) > 10:
                        st.info(f"Showing first 10 of {len(filtered_products)} matches. Refine your search.")
                else:
                    st.warning("No products found matching your search.")
            
            # Display selected product
            if st.session_state.selected_product:
                p_name = st.session_state.selected_product['name']
                p_details = st.session_state.selected_product
                st.markdown(f"Selected: <span class='selected-product'>{p_name}</span>", unsafe_allow_html=True)
                
                # Clear selection button
                if st.button("Clear Selection"):
                    st.session_state.selected_product = None
                    st.session_state.results = None
                    st.rerun()
            else:
                p_name = ""
                p_details = {"pain_points": []}
        else:
            st.markdown('<p class="product-description" style="font-weight: bold; margin-bottom: 5px;">Product Name</p>', unsafe_allow_html=True)
            p_name = st.text_input("", "Luxury Handbag", label_visibility="collapsed")
            p_details = {"category": "Luxury", "pain_points": ["Stock Instability"]}

        st.markdown('<p class="product-description" style="font-weight: bold; margin-bottom: 5px;">Product Description</p>', unsafe_allow_html=True)
        p_desc = st.text_area("", "Authentic leather, handcrafted for a professional look.", label_visibility="collapsed")
        
        # ENHANCED PAIN POINT EXTRACTION DISPLAY
        # st.markdown('<h5 class="customer-sentiment">🔍 Customer Pain Point Analysis (40+ Keywords)</h5>', unsafe_allow_html=True)
        
        # Extract pain points with details from the product description
        pain_analysis = extract_pain_points_detailed(p_desc)
        
        # if pain_analysis['total_pain_points'] > 0:
        #     # Display keyword extraction stats
        #     col1, col2, col3 = st.columns(3)
        #     with col1:
        #         st.metric("Pain Points Found", pain_analysis['total_pain_points'])
        #     with col2:
        #         high_priority = pain_analysis['priority_distribution']['HIGH']
        #         st.metric("HIGH Priority", high_priority)
        #     with col3:
        #         medium_priority = pain_analysis['priority_distribution']['MEDIUM']
        #         st.metric("MEDIUM Priority", medium_priority)
        #     
        #     # Display detailed pain points with matched keywords
        #     st.markdown("**Detected Pain Points & Keywords:**")
        #     for pain_point, details in pain_analysis['matched_keywords'].items():
        #         priority = details['priority']
        #         keyword = details['keyword']
        #         weight = details['weight']
        #         
        #         # Color coding by priority
        #         priority_color = "#FF4444" if priority == "HIGH" else "#FFA500"
        #         st.markdown(f"""
        #         <div style="padding: 10px; margin: 5px 0; border-left: 4px solid {priority_color}; background: #f9f9f9; border-radius: 4px;">
        #             <strong>{pain_point}</strong> [{priority}]<br>
        #             <small>Keyword: <code>{keyword}</code> | Weight: {weight}</small>
        #         </div>
        #         """, unsafe_allow_html=True)
        # else:
        #     st.info("No specific pain points detected in the product description. Try adding customer concerns to the description.")
        
        # Show extraction method info
        # with st.expander("📊 Keyword Extraction Method"):
        #     extractor = get_extractor()
        #     coverage = extractor.get_keyword_coverage()
        #     st.markdown(f"""
        #     **Enhanced Pain Point Extraction System:**
        #     - Total Keywords: {coverage['total_keywords']}
        #     - Pain Point Categories: {coverage['total_categories']}
        #     - Avg Keywords per Category: {coverage['keywords_per_category']:.1f}
        #     
        #     **Categories Covered:**
        #     1. Shipping Delays (14 keywords)
        #     2. Stock Instability (13 keywords)
        #     3. Price Sensitivity (15 keywords)
        #     4. Quality Issues (14 keywords)
        #     5. Durability & Longevity (14 keywords)
        #     6. Poor Customer Service (12 keywords)
        #     7. Return/Refund Difficulties (13 keywords)
        #     8. Packaging Problems (11 keywords)
        #     9. Authenticity Concerns (13 keywords)
        #     10. Expectation Misalignment (13 keywords)
        #     11. Fit/Compatibility Issues (13 keywords)
        #     12. Poor Value Proposition (13 keywords)
        #     """)

        # Add mode selector
        use_llm = st.checkbox("Use AI-powered generation (requires xAI API key)", value=False)

        # Auto-run agent when product is selected
        if st.session_state.selected_product and not st.session_state.results:
            st.session_state.running = True

        if st.button("Activate Scarcity Agent", use_container_width=True, type="primary"):
            st.session_state.running = True
            st.session_state.use_llm = use_llm

# --- MAIN DASHBOARD ---
col_left = st.container()

# Only show processing status when agent is activated (FIXES BLUR ISSUE)
if st.session_state.running:
    with col_left:
        with st.status("Agentic Reasoning in progress...", expanded=True) as status:
            st.write("🔍 Reading product reviews...")
            time.sleep(0.3)
            
            # Extract pain points from real reviews
            if st.session_state.selected_product:
                product_profile = get_product_pain_profile(
                    st.session_state.selected_product['name'],
                    st.session_state.selected_product.get('category', None),
                    review_limit=100
                )
                st.session_state.product_profile = product_profile
                
                if product_profile.get('reviews_found', 0) > 0:
                    st.write(f"✅ Found {product_profile['reviews_found']} reviews | Avg Rating: {product_profile['avg_rating']:.1f}⭐")
                    st.session_state.review_pain_points = product_profile['pain_analysis']
            
            st.write("🔍 Identifying suitable scarcity context...")
            time.sleep(0.6)
            st.write("📊 Analyzing customer sentiment patterns...")
            time.sleep(0.6)
            st.write("✍️ Generating all intensity variations...")
            all_copies = agent_logic.generate_all_intensities(
                p_name,
                p_desc,
                pain_points=p_details.get('pain_points', []),
                product_info=p_details
            )
            st.write("🔧 Evaluating and recommending optimal intensity...")
            recommendation = agent_logic.recommend_best_intensity(
                p_name,
                p_desc,
                all_copies,
                pain_points=p_details.get('pain_points', []),
                product_info=p_details
            )
            trust_metrics = agent_logic.calibrate_trust_level(all_copies[recommendation['recommended_intensity']])
            time.sleep(0.6)
            st.write("⚖️ Calibrating for brand authenticity...")
            time.sleep(0.6)
            status.update(label="Scarcity Optimization Complete!", state="complete", expanded=False)
        
        st.session_state.results = {
            "all_copies": all_copies,
            "recommendation": recommendation,
            "trust": trust_metrics,
            "product": p_name,
            "category": p_details.get('category', 'General')
        }
        st.session_state.running = False

# REVIEW-BASED PAIN POINTS DISPLAY
# if st.session_state.get('review_pain_points'):
#     st.divider()
#     st.markdown('<h3 class="scarcity-strategies">📊 Pain Points Analysis from Product Reviews</h3>', unsafe_allow_html=True)
#     
#     profile = st.session_state.get('product_profile', {})
#     pain_stats = st.session_state.get('review_pain_points', {})
#     
#     # Display statistics
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("Reviews Analyzed", profile.get('reviews_found', 0))
#     with col2:
#         st.metric("Avg Rating", f"{profile.get('avg_rating', 0):.1f}⭐")
#     with col3:
#         st.metric("Unique Pain Points", len(pain_stats.get('pain_point_frequency', {})))
#     with col4:
#         st.metric("Avg Pain Points/Review", f"{pain_stats.get('avg_pain_points_per_review', 0):.1f}")
#     
#     # Display top pain points with percentages
#     st.markdown("**Top Pain Points from Reviews:**")
#     top_pain_points = pain_stats.get('top_pain_points', [])
#     
#     for idx, (pain_point, count) in enumerate(top_pain_points, 1):
#         percentage = pain_stats['pain_point_percentages'].get(pain_point, 0)
#         st.markdown(f"""
#         <div style="padding: 10px; margin: 8px 0; background: #f0f0f0; border-radius: 6px; border-left: 4px solid #D85A30;">
#             <strong>{idx}. {pain_point}</strong><br>
#             <small>Frequency: {count} mentions ({percentage:.1f}% of reviews) | Priority: {pain_stats['priority_distribution'].get('HIGH', 0)} HIGH</small>
#         </div>
#         """, unsafe_allow_html=True)
#     
#     # Show sample reviews with extracted pain points
#     st.markdown("**Sample Reviews with Pain Points:**")
#     for i, review in enumerate(profile.get('review_sample', [])[:2], 1):
#         with st.expander(f"Review {i} - Rating: {review['rating']}⭐"):
#             st.markdown(f"*{review['review_text'][:200]}...*")
#             if review['pain_points']:
#                 st.markdown(f"**Extracted Pain Points:** {', '.join(review['pain_points'])}")
#             else:
#                 st.markdown("*No pain points detected in this review*")

# RESULTS DISPLAY
if st.session_state.results:
        st.divider()
        st.markdown('<h3 class="scarcity-strategies">Scarcity-Optimized Strategies</h3>', unsafe_allow_html=True)
        
        # Display all three intensity variations
        intensity_colors = {"low": "#E1F5EE", "medium": "#FAEEDA", "high": "#FAECE7"}
        intensity_borders = {"low": "#9FE1CB", "medium": "#FAC775", "high": "#F4A261"}
        
        for intensity, copy in st.session_state.results['all_copies'].items():
            st.markdown(f"""
<div class="strategy-headline" style="border-left-color:{intensity_borders[intensity]}; background:{intensity_colors[intensity]}; font-size: 18px; padding: 20px; margin-bottom: 15px;">
    <div style="font-weight: bold; margin-bottom: 10px;">{intensity.upper()} INTENSITY</div>
    {copy}
</div>""", unsafe_allow_html=True)
        
        # Recommendation section
        st.markdown('<h3 class="ai-recommendation">AI Recommendation</h3>', unsafe_allow_html=True)
        rec_intensity = st.session_state.results['recommendation']['recommended_intensity']
        st.markdown(f"""
<div class="strategy-headline" style="border-left-color:#BA7517; background:#FAEEDA; font-size: 20px; padding: 25px;">
    <div style="font-weight: bold; margin-bottom: 10px;">RECOMMENDED: {rec_intensity.upper()} INTENSITY</div>
    {st.session_state.results['recommendation']['reason']}
</div>""", unsafe_allow_html=True)
        
        # Strategy Badges
        st.markdown(f'''
            <span class="nav-badge" style="background:#FAEEDA; color:#854F0B; border-color:#FAC775;">SCARCITY PRINCIPLE</span>
            <span class="nav-badge" style="background:#E1F5EE; color:#0F6E56; border-color:#9FE1CB;">RESEARCH COMPONENT 3</span>
        ''', unsafe_allow_html=True)

        st.divider()
        
        # st.markdown('<h4 class="agent-analytics">Agent Analytics</h4>', unsafe_allow_html=True)
        # r1, r2, r3 = st.columns(3)
        # r1.metric("Trust Retained", f"{int(st.session_state.results['trust']['score']*100)}%")
        # r2.metric("Recommended Intensity", rec_intensity.upper())
        # r3.metric("Response Status", st.session_state.results['trust']['status'])
        
        # st.markdown(f'<span class="agent-analytics">**Researcher Commentary:** The AI has evaluated all intensity levels and recommends **{rec_intensity}** scarcity intensity as optimal for the **{st.session_state.results["category"]}** category to maximize conversion while maintaining authenticity.</span>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; padding: 60px; color: grey;">
            <div style="font-size: 50px;">Test Tube</div>
            <div style="font-size: 18px; font-weight: 700; margin-top: 10px;">Waiting for Research Input</div>
            <div>Enter product details and activate the agent to see results.</div>
    </div>
    """, unsafe_allow_html=True)

# --- ABOUT SECTION ---
# st.markdown("<p style='text-align: center; color: grey; font-size: 12px;'>NeuroMark AI · Final Year Research Demo · BSc Data Science</p>", unsafe_allow_html=True)
