const COMPONENTS = [
  {
    n: "1",
    title: "Dual-System Reasoning",
    tag: "How people decide",
    color: "blue",
    desc: "Figures out whether a customer buying this product is more likely to decide with their gut (fast, emotional) or their head (slow, careful comparison) — then writes marketing copy matched to that.",
  },
  {
    n: "2",
    title: "Emotion Propagation",
    tag: "What they feel",
    color: "teal",
    desc: "Picks the right emotion for the product category — trust, excitement, confidence — and rewrites the message so that feeling comes through clearly, plus suggests matching colors and imagery.",
  },
  {
    n: "3",
    title: "Scarcity Optimization",
    tag: "Why act now",
    color: "amber",
    desc: "Adds urgency — limited stock, time pressure — calibrated to the product, and checks the result doesn't sound so aggressive that it damages customer trust.",
  },
  {
    n: "4",
    title: "Loss Framing",
    tag: "What they'd miss",
    color: "coral",
    desc: "Rewrites the message around what the customer loses by waiting, rather than what they gain by buying — a proven, subtle way to increase urgency without sounding pushy.",
  },
];

export default function HomePage({ onGetStarted }) {
  return (
    <div>
      {/* Hero */}
      <div className="max-w-[900px] mx-auto px-10 pt-20 pb-16 text-center">
        <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
          For small & growing businesses
        </span>
        <h1 className="font-display" style={{ fontSize: 48, fontWeight: 800, letterSpacing: "-1.5px", margin: "18px 0 16px", lineHeight: 1.1 }}>
          Marketing copy that thinks<br />like your customer.
        </h1>
        <p style={{ fontSize: 16, color: "var(--text-secondary)", maxWidth: 560, margin: "0 auto 32px", lineHeight: 1.6 }}>
          Describe your product once. Four AI agents — each built on a different
          principle of consumer psychology — work together to turn it into a
          marketing strategy: how to frame it, what emotion to lead with, and
          when urgency actually helps instead of hurts.
        </p>
        <button className="nm-btn-primary" style={{ width: "auto", padding: "14px 32px", fontSize: 15 }} onClick={onGetStarted}>
          Get Started ↗
        </button>
      </div>

      {/* How it works */}
      <div className="max-w-[1100px] mx-auto px-10 pb-10">
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <h2 className="font-display" style={{ fontSize: 24, fontWeight: 700 }}>How it works</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginTop: 6 }}>
            One product description in. Four psychology-backed agents run automatically.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {COMPONENTS.map((c) => (
            <div key={c.n} className="nm-card" style={{ margin: 0 }}>
              <div className="nm-card-body" style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
                <div
                  className="chain-circle"
                  style={{
                    flexShrink: 0,
                    borderColor: `var(--${c.color}-100)`,
                    background: `var(--${c.color}-50)`,
                    color: `var(--${c.color}-600)`,
                  }}
                >
                  {c.n}
                </div>
                <div>
                  <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: ".05em", color: "var(--text-muted)", marginBottom: 2 }}>
                    {c.tag}
                  </div>
                  <div className="font-display" style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>{c.title}</div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>{c.desc}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Understanding your results — glossary for non-technical users */}
      <div className="max-w-[900px] mx-auto px-10 pb-16">
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <h2 className="font-display" style={{ fontSize: 24, fontWeight: 700 }}>Understanding Your Results</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginTop: 6, maxWidth: 560, margin: "6px auto 0" }}>
            You don't need a marketing or data-science background to use this. Here's what
            the terms on your results page actually mean.
          </p>
        </div>

        <div className="space-y-3">
          <GlossaryItem
            term="Confidence Score"
            meaning="How sure the AI is about its own classification — shown as a percentage. A higher number means the AI found clearer signals in your product description; it doesn't mean the copy itself is better."
          />
          <GlossaryItem
            term='"Emotional" vs "Rational" product'
            meaning="Some products get bought on impulse and feeling (emotional) — think perfume or a treat. Others get bought after research and comparison (rational) — think a laptop or insurance. The AI decides which applies to your product and writes copy to match."
          />
          <GlossaryItem
            term="Scarcity Intensity (Low / Medium / High)"
            meaning="How strongly the copy pushes urgency — limited stock, time pressure, high demand. Low is subtle, High is aggressive ('only 2 left!'). The AI picks a level it thinks fits your product without sounding fake."
          />
          <GlossaryItem
            term="Trust Score"
            meaning="An estimate of how believable the urgency messaging will feel to a real customer. A low trust score or a 'Warning' doesn't mean something is broken — it's a heads-up that the messaging might come across as pushy for this particular product, so use it carefully or for a short, genuine promotion only."
          />
          <GlossaryItem
            term="Sentiment Score"
            meaning="How positive or negative a piece of text sounds, on a scale from -1 (very negative) to +1 (very positive). Used to check that urgency-driven copy doesn't accidentally turn customers off."
          />
          <GlossaryItem
            term="FOMO Score"
            meaning={'FOMO = "Fear Of Missing Out." This counts how many urgency phrases (like "don\'t miss out" or "limited time") appear in a message. A higher number means stronger urgency language.'}
          />
          <GlossaryItem
            term="Target Emotion"
            meaning="The specific feeling — excitement, trust, confidence, and so on — the AI is trying to build into your marketing copy for this product category."
          />
          <GlossaryItem
            term="Loss-Framed Copy"
            meaning="A version of your message rewritten around what the customer loses by not buying, instead of what they gain by buying. Research shows people often respond more strongly to avoiding a loss than gaining a benefit — best used sparingly, for real limited-time offers."
          />
        </div>
      </div>

      {/* What you get */}
      <div className="max-w-[900px] mx-auto px-10 py-16 text-center">
        <h2 className="font-display" style={{ fontSize: 22, fontWeight: 700, marginBottom: 10 }}>
          What you'll get
        </h2>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", maxWidth: 520, margin: "0 auto 28px", lineHeight: 1.6 }}>
          Fill in your product details and your customer profile once. You'll get
          a complete marketing strategy back — classification, ready-to-use copy,
          and a plain-language explanation of why it was written that way.
        </p>
        <button className="nm-btn-secondary" style={{ padding: "12px 28px" }} onClick={onGetStarted}>
          Try it with your product →
        </button>
      </div>
    </div>
  );
}

function GlossaryItem({ term, meaning }) {
  return (
    <div className="nm-card" style={{ margin: 0 }}>
      <div className="nm-card-body" style={{ padding: "14px 20px" }}>
        <div className="font-display" style={{ fontWeight: 700, fontSize: 14, marginBottom: 4, color: "var(--text-primary)" }}>
          {term}
        </div>
        <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>
          {meaning}
        </div>
      </div>
    </div>
  );
}
