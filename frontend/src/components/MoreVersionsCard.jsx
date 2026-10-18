import CopyButton from "./CopyButton.jsx";
import { AGENTS, agentColors } from "../constants.js";
import { G } from "./Term.jsx";

// The individual messages behind the final blend, each in its helper's
// colour and labelled with when to use it — so people pick by situation
// instead of by technique name.
export default function MoreVersionsCard({ result }) {
  const c3 = result?.component3;
  const c24 = result?.component24;

  const versions = [
    c24?.emotion_copy && {
      agent: AGENTS.feeling,
      name: "Feeling version",
      when: `Everyday posts and ads. Aims for ${c24.target_emotion}.`,
      text: c24.emotion_copy,
    },
    c3?.final_copy && {
      agent: AGENTS.urgency,
      name: "Urgency version",
      when: `Sales and promotions. ${capitalise(c3.recommended_intensity || "")} urgency.`,
      text: c3.final_copy,
    },
    c24?.loss_message && {
      agent: AGENTS.missout,
      name: "\"Don't miss out\" version",
      when: "Limited-time offers only, so it doesn't wear thin.",
      text: c24.loss_message,
    },
  ].filter(Boolean);

  if (!versions.length) return null;

  return (
    <div className="version-grid">
      {versions.map((v) => {
        const c = agentColors(v.agent.color);
        return (
          <article key={v.name} className="version-card" style={{ "--tile-bg": c.bg, "--tile-border": c.border, "--tile-ink": c.ink }}>
            <div className="version-head">
              <h3 className="version-name"><span aria-hidden="true">{v.agent.emoji}</span>{v.name}</h3>
              <p className="version-when"><G>{v.when}</G></p>
            </div>
            <div className="version-body">
              <p className="version-text">{v.text}</p>
              <div><CopyButton text={v.text} /></div>
            </div>
          </article>
        );
      })}
    </div>
  );
}

function capitalise(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}
