import { buildStrategySummary } from "../strategySummary.js";
import { AGENTS, agentColors } from "../constants.js";

// "At a glance": one tile per AI helper, in that helper's colour, each
// answering one simple question with a short verdict. Built only from
// scores the agents actually measured (see strategySummary.js), not from
// an extra AI guess.
export default function StrategySummaryCard({ result }) {
  const s = buildStrategySummary(result);

  const tiles = [
    { agent: AGENTS.decide, q: "How do your customers decide?", ...s.customerMindset, tone: "neutral" },
    { agent: AGENTS.urgency, q: "Should you add urgency?", ...s.urgency, tone: s.urgency.verdict.startsWith("Use carefully") ? "warn" : "good" },
    { agent: AGENTS.feeling, q: "Does the feeling come through?", ...s.emotional, tone: s.emotional.verdict.startsWith("Yes") ? "good" : "neutral" },
    { agent: AGENTS.missout, q: "Is \"don't miss out\" wording OK?", ...s.lossFraming, tone: s.lossFraming.verdict === "Use sparingly" ? "warn" : "good" },
  ];

  const verdictColor = { good: "var(--teal-600)", warn: "var(--coral-600)", neutral: "var(--ink)" };
  const mix = s.overallMix ? s.overallMix.charAt(0).toUpperCase() + s.overallMix.slice(1) : "";

  return (
    <>
      <div className="glance-grid">
        {tiles.map((t) => {
          const c = agentColors(t.agent.color);
          return (
            <div key={t.q} className="glance-tile" style={{ "--tile-bg": c.bg, "--tile-border": c.border, "--tile-ink": c.ink }}>
              <span className="glance-icon" aria-hidden="true">{t.agent.emoji}</span>
              <div>
                <div className="glance-q">{t.q}</div>
                <div className="glance-verdict" style={{ color: verdictColor[t.tone] }}>
                  {t.tone === "good" && <span aria-hidden="true">✓ </span>}
                  {t.tone === "warn" && <span aria-hidden="true">! </span>}
                  {t.verdict}
                </div>
                {t.detail && <div className="glance-detail">{t.detail}</div>}
              </div>
            </div>
          );
        })}
      </div>
      {mix && (
        <div className="advice night">
          <span aria-hidden="true" style={{ fontSize: 22 }}>💡</span>
          <span><b>Our advice: </b>{mix}</span>
        </div>
      )}
    </>
  );
}
