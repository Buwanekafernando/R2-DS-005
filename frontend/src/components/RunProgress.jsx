import { useEffect, useState } from "react";
import { AGENTS } from "../constants.js";
import { G } from "./Term.jsx";

// Shows what the system is doing while /generate-strategy runs.
//
// Honest note: the backend returns everything in one response, so the
// browser can't see each step finish. The steps below are listed in the
// exact order main.py runs them, and the highlight moves on based on how
// long each step usually takes. The panel says so, in plain words.
const STEP_MS = [6000, 7000, 9000, 5000]; // typical time per step; the last step waits for the server

function buildSteps(emotion) {
  return [
    { ...AGENTS.decide, title: "Working out how your customers decide", sub: "Do they buy on feeling, or only after comparing?" },
    { ...AGENTS.urgency, title: "Choosing the right amount of urgency", sub: "Enough to make people act, not so much that it feels pushy." },
    {
      ...AGENTS.feeling,
      title: emotion ? `Writing in the feeling of ${emotion}` : "Picking and writing in the right feeling",
      sub: "Our emotion AI reads the message back and rewrites it if the feeling is off, up to 3 tries.",
    },
    { ...AGENTS.missout, title: "Showing what they'd miss out on", sub: "A gentle \"don't miss out\" version that keeps the same feeling." },
    { emoji: "✨", color: null, feature: "Final step", title: "Blending it all into one message", sub: "Combining the best parts of all four into your recommended message." },
  ];
}

export default function RunProgress({ emotion, productName }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const id = setInterval(() => setElapsed(Date.now() - start), 250);
    return () => clearInterval(id);
  }, []);

  const steps = buildSteps(emotion);
  let active = 0;
  let t = elapsed;
  while (active < STEP_MS.length && t >= STEP_MS[active]) { t -= STEP_MS[active]; active += 1; }

  const secs = Math.floor(elapsed / 1000);
  const clock = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
  const pct = Math.min(94, (elapsed / 30000) * 94); // estimate; never shows "done" before the server answers

  return (
    <section className="night run-panel" aria-live="polite" aria-busy="true">

      <div className="run-left">
      <div className="run-head">
        <div>
          <h2 className="run-title">Creating your message…</h2>
          {productName && <p className="run-product">for {productName}</p>}
        </div>
        <span className="run-timer" aria-label={`${secs} seconds so far`}>⏱ {clock}</span>
      </div>
      <p style={{ fontSize: 16, color: "var(--on-night-soft)" }}>
        Four AI helpers work on it one after another. This usually takes 15 to 30 seconds.
      </p>
      <div className="run-bar" aria-hidden="true"><i style={{ width: `${pct}%` }} /></div>
      </div>

      <ol className="run-steps">
        {steps.map((s, i) => {
          const state = i < active ? "done" : i === active ? "active" : "waiting";
          const solid = s.color ? `var(--${s.color}-400)` : "#FFD43B";
          const iconStyle =
            state === "done" ? { background: solid } :
            state === "active" ? { borderColor: solid, background: "var(--night-chip)" } : undefined;
          return (
            <li key={i} className={`run-step ${state}`} style={{ "--ring-color": solid }}>
              <span className="run-icon" aria-hidden="true" style={iconStyle}>
                {state === "done" ? "✓" : s.emoji}
              </span>
              <div className="run-body">
                <div className="run-step-title">
                  {s.title}
                  <span className="sr-only">{state === "done" ? " (done)" : state === "active" ? " (in progress)" : " (waiting)"}</span>
                </div>
                <div className="run-step-sub">
                  <G>{s.sub}</G>
                  <span className="run-tag" style={{ background: "var(--night-chip)", color: "var(--on-night)", border: "1px solid var(--night-chip-border)" }}>{s.feature}</span>
                </div>
              </div>
            </li>
          );
        })}
      </ol>

      {secs >= 60 && (
        <p className="run-note" style={{ color: "var(--night-accent)" }}>
          This is taking longer than usual. The AI service may be busy, so it's fine to keep waiting.
        </p>
      )}
      <p className="run-note">
        The steps run in this order on the server. The highlight and bar show roughly where it's up to,
        based on how long each step usually takes.
      </p>
    </section>
  );
}
