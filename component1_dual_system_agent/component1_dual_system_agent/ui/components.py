# ui/components.py

import streamlit as st

def render_header():
    st.markdown("""
        <div style='text-align:center; padding: 1.5rem 0 1rem 0'>
            <h2 style='margin:0; font-size:1.6rem'>
                Dual System Reasoning Agent
            </h2>
            <p style='color:gray; margin-top:6px; font-size:0.95rem'>
                Component 1 — Neuro-Marketing Strategy Generator
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_classification_badge(cognitive_mode, confidence):
    if cognitive_mode == "System1":
        color   = "#FAEEDA"
        border  = "#FAC775"
        text_c  = "#633806"
        label   = "System 1 — Emotional / Impulsive"
        icon    = ""
    else:
        color   = "#E6F1FB"
        border  = "#B5D4F4"
        text_c  = "#0C447C"
        label   = "System 2 — Rational / Deliberative"
        icon    = ""

    st.markdown(f"""
        <div style='background:{color}; border:1px solid {border};
                    border-radius:10px; padding:14px 18px; margin:10px 0'>
            <div style='font-size:1.1rem; font-weight:600; color:{text_c}'>
                {icon} {label}
            </div>
            <div style='margin-top:8px; font-size:0.85rem; color:{text_c}'>
                Confidence
            </div>
            <div style='background:rgba(0,0,0,0.08); border-radius:6px;
                        height:10px; margin-top:4px; overflow:hidden'>
                <div style='background:{text_c}; height:10px; width:{confidence*100:.0f}%;
                            border-radius:6px'></div>
            </div>
            <div style='font-size:0.8rem; color:{text_c}; margin-top:4px'>
                {confidence*100:.1f}%
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_reasoning_tags(reasoning, s1_prob, s2_prob, price_tier="unknown"):
    tags = []

    if s1_prob > 0.7:
        tags.append(("Impulse signal", "#FAEEDA", "#633806"))
    if s2_prob > 0.7:
        tags.append(("Deliberate signal", "#E6F1FB", "#0C447C"))
    if price_tier in ["high", "premium"]:
        tags.append(("High price tier", "#EEEDFE", "#3C3489"))
    elif price_tier == "low":
        tags.append(("Low price tier", "#EAF3DE", "#27500A"))

    tag_html = ""
    for label, bg, color in tags:
        tag_html += f"""
            <span style='background:{bg}; color:{color}; font-size:11px;
                         padding:3px 10px; border-radius:20px;
                         margin-right:6px; font-weight:500'>
                {label}
            </span>"""

    if tag_html:
        st.markdown(
            f"<div style='margin:8px 0'>{tag_html}</div>",
            unsafe_allow_html=True
        )


def render_copy_cards(emotional_copy, rational_copy,
                      recommended_strategy, emo_quality, rat_quality):

    col1, col2 = st.columns(2)

    rec_emo = recommended_strategy == "emotional"
    rec_rat = recommended_strategy == "rational"

    with col1:
        badge = "✓ Recommended" if rec_emo else ""
        border = "2px solid #FAC775" if rec_emo else "1px solid #FAC775"
        st.markdown(f"""
            <div style='background:#FAEEDA; border:{border};
                        border-radius:10px; padding:14px 16px; height:100%'>
                <div style='font-size:11px; font-weight:600;
                            color:#633806; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:.05em'>
                     Emotional Copy {badge}
                </div>
                <div style='font-size:0.9rem; color:#3d2200;
                            line-height:1.6'>
                    {emotional_copy}
                </div>
                <div style='margin-top:10px; font-size:11px; color:#633806'>
                    Sentiment: {emo_quality.get("sentiment_compound", 0):.2f} &nbsp;|&nbsp;
                    Alignment: {emo_quality.get("mode_alignment", 0):.0%}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        badge  = "Recommended" if rec_rat else ""
        border = "2px solid #B5D4F4" if rec_rat else "1px solid #B5D4F4"
        st.markdown(f"""
            <div style='background:#E6F1FB; border:{border};
                        border-radius:10px; padding:14px 16px; height:100%'>
                <div style='font-size:11px; font-weight:600;
                            color:#0C447C; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:.05em'>
                    🔍 Rational Copy {badge}
                </div>
                <div style='font-size:0.9rem; color:#0a2d52;
                            line-height:1.6'>
                    {rational_copy}
                </div>
                <div style='margin-top:10px; font-size:11px; color:#0C447C'>
                    Sentiment: {rat_quality.get("sentiment_compound", 0):.2f} &nbsp;|&nbsp;
                    Alignment: {rat_quality.get("mode_alignment", 0):.0%}
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_strategy_box(strategy, explanation):
    color  = "#EAF3DE" if strategy == "emotional" else "#E6F1FB"
    border = "#A4D06B" if strategy == "emotional" else "#B5D4F4"
    tcolor = "#27500A" if strategy == "emotional" else "#0C447C"
    icon   = ""       if strategy == "emotional" else ""

    st.markdown(f"""
        <div style='background:{color}; border:1px solid {border};
                    border-radius:10px; padding:12px 16px; margin-top:12px;
                    display:flex; align-items:center; gap:12px'>
            <span style='font-size:1.3rem'>{icon}</span>
            <div>
                <div style='font-size:12px; font-weight:600;
                            color:{tcolor}; text-transform:uppercase;
                            letter-spacing:.05em'>
                    Recommended Strategy
                </div>
                <div style='font-size:0.85rem; color:{tcolor};
                            margin-top:3px'>
                    {explanation}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_json_output(agent_output):
    """Shows the JSON that gets sent to other components"""
    st.markdown(
        "<div style='font-size:12px; font-weight:500; color:gray;"
        "margin-bottom:6px'>Output sent to Components 2, 3, 4</div>",
        unsafe_allow_html=True
    )
    st.json({
        "cognitive_mode":   agent_output.get("cognitive_mode"),
        "confidence":       agent_output.get("confidence"),
        "strategy":         agent_output.get("strategy"),
        "emotional_copy":   agent_output.get("emotional_copy", "")[:80] + "...",
        "rational_copy":    agent_output.get("rational_copy",  "")[:80] + "...",
        "recommended_copy": agent_output.get("recommended_copy","")[:80] + "..."
    })