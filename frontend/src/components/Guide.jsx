import { AGENTS, agentVars } from "../constants.js";
import { G } from "./Term.jsx";

// The always-visible "what's happening and what do I do" panel beside the
// Create form. It answers the two questions a first-time user has:
// where am I in the journey, and what do I have to do right now.
const JOURNEY = [
  { id: 1, who: "You", title: "Tell us about your product", d: "Name, type and a short description." },
  { id: 2, who: "You", title: "Describe your customer", d: "A rough picture of who buys it." },
  { id: 3, who: "You", title: "Pick the feeling", d: "How should people feel when they read it?" },
  { id: 4, who: "AI", title: "Four AI helpers write it", d: "Takes about 15 to 30 seconds." },
  { id: 5, who: "You", title: "Copy and post", d: "Paste it into Instagram, Facebook, WhatsApp or email." },
];

const TODO = {
  1: "Give your product a name, pick its type and describe it in a sentence or two. Not sure what to write? Tap one of the examples above the form.",
  2: "Picture one typical customer and choose the closest answers. These help the AI judge whether people buy on feeling or after comparing. Unsure? Keep the answers already selected.",
  3: "Choose the feeling you want people to have. The ones that suit your product type are shown first. When you're happy, press the orange button and we'll do the rest.",
};

export default function Guide({ step }) {
  return (
    <aside className="guide" aria-label="Guide">
      <section className="guide-card guide-todo" aria-live="polite">
        <h2 className="guide-title">What to do now</h2>
        <p><G>{TODO[step]}</G></p>
      </section>

      <section className="guide-card">
        <h2 className="guide-title">What happens next</h2>
        <ol className="guide-steps">
          {JOURNEY.map((j) => {
            const state = j.id < step ? "done" : j.id === step ? "now" : "todo";
            return (
              <li key={j.id} className={state}>
                <span className="n" aria-hidden="true">{state === "done" ? "✓" : j.id}</span>
                <div>
                  <b>{j.title} <span className="nm-badge" style={{ fontSize: 11, padding: "0 8px", background: j.who === "AI" ? "var(--violet-50)" : "var(--surface-sunk)", color: j.who === "AI" ? "var(--violet-800)" : "var(--text-secondary)", border: "1px solid var(--border)" }}>{j.who === "AI" ? "We do this" : "You"}</span></b>
                  <span className="d">{j.d}</span>
                </div>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="guide-card">
        <h2 className="guide-title">The four helpers behind it</h2>
        <div className="guide-helpers">
          {[AGENTS.decide, AGENTS.urgency, AGENTS.feeling, AGENTS.missout].map((a) => (
            <span key={a.research} style={agentVars(a.color)}><span aria-hidden="true">{a.emoji}</span>{a.name}</span>
          ))}
        </div>
      </section>
    </aside>
  );
}
