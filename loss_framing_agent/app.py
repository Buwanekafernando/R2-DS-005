

import gradio as gr
from groq import Groq
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#  Config 

analyzer     = SentimentIntensityAnalyzer()

loss_keywords = [
    "missing", "losing", "without", "don't miss", "never have",
    "left behind", "falling behind", "can't afford", "risk",
    "too late", "regret", "wasting", "miss out", "lose out",
    "no longer", "won't have", "disadvantage", "lack", "overlook"
]

def get_sentiment(text):
    return round(analyzer.polarity_scores(str(text))['compound'], 3)

def get_fomo_score(text):
    return sum(1 for kw in loss_keywords if kw in text.lower())

def get_tone_label(score):
    if score >= 0.05:
        return "Positive — Safe to use"
    elif score <= -0.5:
        return "Too Negative — Needs adjustment"
    else:
        return "Acceptable — Within safe range"

def run_agent(product_name, category, gain_message):
    if not product_name.strip() or not gain_message.strip():
        return "Please fill in all fields.", "", "", "", "", ""
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""You are a marketing expert specializing in loss aversion psychology.

Product: {product_name}
Category: {category}
Original gain-framed review: "{gain_message}"

Rewrite this as a SHORT loss-framed marketing message (2-3 sentences only).
- Emphasize what the customer LOSES or MISSES by NOT having this product
- Create FOMO (fear of missing out)
- Stay factual, not scary
- Vary your style

Return ONLY the rewritten message. Nothing else."""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        loss_message = response.choices[0].message.content.strip()

        gain_sent = get_sentiment(gain_message)
        loss_sent = get_sentiment(loss_message)
        fomo      = get_fomo_score(loss_message)
        tone      = get_tone_label(loss_sent)
        change    = round(loss_sent - gain_sent, 3)

        return (
            loss_message,
            f"{gain_sent}",
            f"{loss_sent}",
            f"{fomo} loss keywords",
            f"{change:+.3f}",
            tone
        )
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", "", ""


# ── UI ──
with gr.Blocks(title="Loss Framing Agent") as demo:

    gr.Markdown("""
    ### Behavioral AI Marketing System
    Convert gain-framed product messages into **loss-framed** alternatives using Loss Aversion Psychology.
    > *Kahneman & Tversky (1979): People respond 2x more strongly to losses than equivalent gains.*
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            product_name = gr.Textbox(
                label="Product Name",
                placeholder="e.g. Sony WH-1000XM5 Headphones"
            )
            category = gr.Dropdown(
                choices=["Apparel","Baby","Beauty",
                         "Electronics","Grocery",
                         "Pet Products","Sports"],
                label="Product Category",
                value="Electronics"
            )
            gain_message = gr.Textbox(
                label="Gain-Framed Message",
                placeholder="Paste a positive product review here...",
                lines=5
            )
            submit_btn = gr.Button(
                "Convert to Loss Framing",
                variant="primary",
                size="lg"
            )

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            loss_output = gr.Textbox(
                label="Loss-Framed Message",
                lines=5,
                interactive=False
            )
            with gr.Row():
                gain_sent_out = gr.Textbox(label="Gain Sentiment", interactive=False)
                loss_sent_out = gr.Textbox(label="Loss Sentiment", interactive=False)
            with gr.Row():
                fomo_out   = gr.Textbox(label="FOMO Score",       interactive=False)
                change_out = gr.Textbox(label="Sentiment Change", interactive=False)
            tone_out = gr.Textbox(label="Tone Safety Check",      interactive=False)

    gr.Markdown("### Click an example to try it")
    gr.Examples(
        examples=[
            ["Sony WH-1000XM5",      "Electronics",  "These headphones changed my life. Noise cancellation is unreal and sound quality is perfect."],
            ["Baby Swaddle Blanket",  "Baby",         "My baby sleeps so well with this blanket. Super soft and very easy to use for a newborn."],
            ["Running Shoes",         "Sports",       "These shoes improved my running dramatically. Very lightweight and incredibly comfortable."],
            ["Anti-Aging Serum",      "Beauty",       "This serum works wonders. My skin looks 10 years younger after just 2 weeks of use."],
            ["Organic Dog Food",      "Pet Products", "My dog loves this food. His coat is shinier and he has so much more energy now."],
        ],
        inputs=[product_name, category, gain_message]
    )

    submit_btn.click(
        fn=run_agent,
        inputs=[product_name, category, gain_message],
        outputs=[loss_output, gain_sent_out, loss_sent_out,
                 fomo_out, change_out, tone_out]
    )

# ── Run locally ──
if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), share=True)