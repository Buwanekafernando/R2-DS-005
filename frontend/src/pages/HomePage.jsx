import { AGENTS, EXAMPLES, agentColors, agentVars } from "../constants.js";
import { G, Term } from "../components/Term.jsx";

const HELPERS = [
  {
    agent: AGENTS.decide,
    desc: "Works out whether people buy your product on gut feeling or only after comparing, then writes in the style that suits them.",
  },
  {
    agent: AGENTS.urgency,
    desc: "Adds the right amount of “act now”, such as limited stock, and checks it doesn't sound pushy or fake.",
  },
  {
    agent: AGENTS.feeling,
    desc: "Writes your message so it carries one clear feeling, like trust or excitement. Our own emotion AI reads it back to check the feeling really comes through, and suggests matching colours.",
  },
  {
    agent: AGENTS.missout,
    desc: "Rewrites the message around what people miss if they wait. Used gently, it helps people decide without scaring them.",
  },
];

const HOW = [
  { who: "Your turn", title: "Describe your product", text: "Its name, what kind of product it is, a sentence or two, and a rough idea of who buys it. About two minutes.", color: "cyan" },
  { who: "We do the work", title: "Four AI helpers get to work", text: "Each one is built on a proven idea from consumer psychology. You can watch them work, step by step.", color: "violet" },
  { who: "Your turn", title: "Copy your message", text: "One message ready to post, plus other versions for sales and offers, and colour ideas for your picture.", color: "orange" },
];

const FAQ = [
  ["Why does it ask about my customer?", "Some products are bought on feeling and impulse, like a treat or perfume. Others are bought after research, like a laptop. A rough idea of your typical customer helps the AI judge which kind your product is."],
  ["What is the “feeling check”?", "After the message is written, our own emotion AI (a RoBERTa model trained on thousands of real comments) reads it back and says which feeling comes across. If it's not the one you chose, the message is rewritten and checked again, with up to 3 tries in total."],
  ["What does “urgency” mean, and what are low, medium and high?", "Urgency is wording that encourages people to act now, such as “limited stock”. Low is a gentle nudge, high is strong (“only 2 left!”). The AI picks the level that suits your product without sounding fake."],
  ["What is a trust score?", "An estimate of how believable the urgency wording will feel to a real customer. A low score isn't an error. It means the wording may feel pushy for this product, so use it only for short, genuine offers."],
  ["What is the sentiment score?", "How positive or negative the words sound, from −1 (very negative) to +1 (very positive). It's used to make sure urgency wording doesn't turn customers off."],
  ["What is a FOMO score?", "FOMO means “fear of missing out”. The score counts phrases like “don't miss out” or “limited time”. A higher number means stronger urgency."],
  ["What is the “don't miss out” version?", "The same message, rewritten around what customers lose by waiting instead of what they gain by buying. People often react more strongly to avoiding a loss, so it works well for real limited-time offers. Use it sparingly."],
  ["What does the confidence percentage mean?", "How sure the AI is about its own decision, for example that your product is bought on feeling. It's not a score for how good the message is."],
  ["Is my information saved anywhere?", "Your answers and results are saved only in this browser on this device, so you can come back to them in History. Clearing your browser data removes them."],
];

const WORDS = ["urgency", "FOMO", "sentiment score", "trust score", "loss framing", "RoBERTa", "call to action", "channel"];

export default function HomePage({ onGetStarted, onTryExample }) {
  return (
    <div>
      {/* ── Hero: what it is, what to do, and a real-looking result ── */}
      <section className="night hero">

        <div className="wrap">
          <div className="hero-grid">
            <div>
              <span className="hero-pill"><span aria-hidden="true">🏪</span> For small and growing businesses</span>
              <h1 className="hero-title">Marketing copy that thinks like your customer.</h1>
              <p className="hero-sub">
                Describe your product. Four AI helpers work out how your customers decide, the feeling
                to lead with and how much urgency to use. You get one message, ready to post.
              </p>
              <button className="btn-sun" onClick={onGetStarted}>✨ Create my message</button>
              <p style={{ fontSize: 15, fontWeight: 700, margin: "26px 0 10px", color: "var(--on-night)" }}>
                Or watch it work with an example:
              </p>
              <div className="chip-row">
                {EXAMPLES.map((ex) => (
                  <button key={ex.id} type="button" className="choice-chip chip-dark" onClick={() => onTryExample(ex.id)}>
                    <span className="chip-emoji" aria-hidden="true">{ex.emoji}</span>{ex.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ position: "relative", padding: "24px 8px" }}>
              <SampleResult />
            </div>
          </div>
        </div>
      </section>

      {/* ── How it works: a real 3-step sequence, with who does what ── */}
      <section className="wrap section" aria-labelledby="how-h">
        <h2 id="how-h" className="section-title">How it works</h2>
        <p className="section-lede">Three steps. You only do two of them.</p>
        <ol className="steps-row">
          {HOW.map((h, i) => (
            <li key={h.title} className="nm-card" style={{ margin: 0, ...agentVars(h.color) }}>
              <div className="nm-card-body">
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, gap: 8, flexWrap: "wrap" }}>
                  <span className="how-num" aria-hidden="true" style={{ background: "var(--h-solid)", marginBottom: 0 }}>{i + 1}</span>
                  <span className="nm-badge" style={{ background: "var(--h-bg)", color: "var(--h-ink)", border: "1px solid var(--h-border)" }}>{h.who}</span>
                </div>
                <h3 style={{ fontWeight: 800, fontSize: 20, marginBottom: 6 }}>{h.title}</h3>
                <p style={{ fontSize: 15.5, color: "var(--text-secondary)", lineHeight: 1.6 }}><G>{h.text}</G></p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* ── The four helpers, each in its own colour ── */}
      <section className="wrap section" aria-labelledby="helpers-h">
        <h2 id="helpers-h" className="section-title">Meet the four AI helpers</h2>
        <p className="section-lede">
          Each one handles one part of a good marketing message. Look out for their colours in your results.
        </p>
        <div className="helpers-row">
          {HELPERS.map(({ agent, desc }) => {
            const c = agentColors(agent.color);
            return (
              <article key={agent.research} className="helper-card" style={{ ...agentVars(agent.color), borderColor: c.border }}>
                <span className="helper-icon" aria-hidden="true">{agent.emoji}</span>
                <div>
                  <h3 style={{ fontWeight: 800, fontSize: 20, marginBottom: 6, color: c.ink }}>{agent.name}</h3>
                  <p style={{ fontSize: 15.5, color: "var(--text-secondary)", lineHeight: 1.6 }}><G>{desc}</G></p>
                  <p style={{ fontSize: 13.5, fontWeight: 700, color: c.ink, marginTop: 12, display: "inline-block", background: c.bg, border: `1px solid ${c.border}`, padding: "3px 11px", borderRadius: 12 }}>
                    {agent.component}: <Term>{agent.research}</Term>
                  </p>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* ── Questions + plain-English word list, side by side ── */}
      <section className="wrap section" aria-labelledby="faq-h">
        <div className="faq-split">
          <div>
            <h2 id="faq-h" className="section-title">Questions about your results</h2>
            <p className="section-lede">You don't need a marketing background. Tap a question to see the answer.</p>
            {FAQ.map(([q, a]) => (
              <details key={q} className="faq">
                <summary>{q}</summary>
                <div className="faq-body"><G>{a}</G></div>
              </details>
            ))}
          </div>
          <aside className="words-card" aria-labelledby="words-h">
            <h2 id="words-h" className="section-title" style={{ fontSize: 24 }}>Words you'll see</h2>
            <p style={{ fontSize: 15, color: "var(--text-secondary)", marginBottom: 16 }}>
              Anywhere in the app, hover over, tap or Tab to a word with a dotted underline to see what it means.
            </p>
            <dl>
              {WORDS.map((w) => (
                <div key={w}>
                  <dt><Term>{w}</Term></dt>
                </div>
              ))}
            </dl>
            <p style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 16 }}>
              Try it now: hover over any word above.
            </p>
          </aside>
        </div>
      </section>

      <section className="wrap section" style={{ paddingBottom: 96 }}>
        <div className="night cta-band">
          <h2 className="section-title" style={{ marginBottom: 10 }}>Ready to try it with your product?</h2>
          <p style={{ fontSize: 17, color: "var(--on-night-soft)", marginBottom: 24 }}>About two minutes to fill in, half a minute to create.</p>
          <button className="btn-sun" onClick={onGetStarted}>✨ Create my message</button>
        </div>
      </section>
    </div>
  );
}

// A static picture of what a finished result looks like, so first-time
// visitors understand the output before filling anything in.
function SampleResult() {
  return (
    <figure aria-label="Example of a finished result" style={{ margin: 0, position: "relative", zIndex: 2 }}>
      <div className="result-hero" style={{ marginBottom: 0, boxShadow: "var(--shadow-card)" }}>
        <div className="result-hero-top">
          <span className="result-hero-kicker"><span aria-hidden="true">✨</span> Your message is ready</span>
          <span className="nm-badge" style={{ background: "var(--violet-50)", color: "var(--violet-800)", border: "1px solid var(--violet-100)" }}>
            Best for: Instagram posts
          </span>
        </div>
        <p className="result-message" style={{ fontSize: 18 }}>
          Made with the Ayurvedic herbs Sri Lankan families have trusted for generations, our lavender
          neem lotion keeps dry skin soft from morning to night. Gentle, natural and made to last.
        </p>
        <div className="result-section">
          <div className="check-row">
            <span className="check-pill tone-good"><span className="check-icon" aria-hidden="true">🤝</span><span>Feeling check: comes across as <b>trust</b></span></span>
            <span className="check-pill tone-good"><span className="check-icon" aria-hidden="true">🙂</span><span>Tone: friendly and positive</span></span>
          </div>
        </div>
        <div className="result-section" style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          {[AGENTS.decide, AGENTS.urgency, AGENTS.feeling, AGENTS.missout].map((a) => {
            const c = agentColors(a.color);
            return (
              <span key={a.research} className="nm-badge" style={{ background: c.bg, border: `1px solid ${c.border}`, color: c.ink }}>
                {a.emoji} {a.name}
              </span>
            );
          })}
        </div>
      </div>
      <figcaption style={{ fontSize: 14, color: "var(--on-night-soft)", marginTop: 14, textAlign: "center" }}>
        An example of what you get back
      </figcaption>
    </figure>
  );
}
