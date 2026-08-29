import CopyButton from "./CopyButton.jsx";

// The synthesis step: one blended, AI-reasoned recommendation combining
// all four components' analyses into a single ready-to-use answer.
// `rec` is the FinalRecommendation shape: { recommendation, rationale, best_for }
export default function FinalRecommendationCard({ rec }) {
  if (!rec) return null;

  return (
    <div className="nm-card" style={{
      animation: "fadeUp .4s ease .3s both",
      border: "2px solid var(--purple-100)",
      background: "linear-gradient(180deg, var(--purple-50) 0%, var(--surface) 60%)",
    }}>
      <div className="nm-card-header" style={{ borderBottom: "1px solid var(--purple-100)" }}>
        <span className="nm-card-title" style={{ color: "var(--purple-800)" }}>
          ✦ AI's Final Recommendation
        </span>
        <span className="nm-badge" style={{ background: "var(--purple-600)", color: "#fff" }}>
          Combines all 4 analyses
        </span>
      </div>
      <div className="nm-card-body">
        <div style={{ fontSize: 12, color: "var(--purple-800)", marginBottom: 12, lineHeight: 1.6 }}>
          This isn't just one of the messages above — it's a new blend, written after reviewing
          the buying-psychology, urgency, and emotional analyses together, aiming for the single
          strongest version of your marketing message.
        </div>

        <div style={{
          background: "var(--surface)", border: "1px solid var(--purple-100)",
          borderRadius: "var(--radius-md)", padding: 16, marginBottom: 12,
        }}>
          <div className="copy-text" style={{ fontSize: 15, fontWeight: 500 }}>{rec.recommendation}</div>
          <CopyButton text={rec.recommendation} />
        </div>

        <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 10 }}>
          <strong style={{ color: "var(--text-primary)" }}>Why this works: </strong>
          {rec.rationale}
        </div>

        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12 }}>
          <span style={{ color: "var(--text-muted)" }}>Best used for:</span>
          <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
            {rec.best_for}
          </span>
        </div>
      </div>
    </div>
  );
}
