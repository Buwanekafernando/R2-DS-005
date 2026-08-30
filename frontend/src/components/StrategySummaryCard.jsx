import { buildStrategySummary } from "../strategySummary.js";

function SummaryRow({ icon, title, verdict, detail, verdictColor }) {
  return (
    <div style={{ display: "flex", gap: 12, padding: "12px 0", borderBottom: "1px solid var(--border)" }}>
      <div style={{ fontSize: 20, lineHeight: 1 }}>{icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".04em", marginBottom: 2 }}>
          {title}
        </div>
        <div style={{ fontWeight: 700, fontSize: 14, color: verdictColor || "var(--text-primary)", marginBottom: 4 }}>
          {verdict}
        </div>
        {detail && <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }}>{detail}</div>}
      </div>
    </div>
  );
}

// Answers "why," not "what to write" — a decision-oriented briefing a
// business owner can use to plan a campaign, sitting alongside (not
// replacing) the ready-to-use copy in FinalRecommendationCard.
export default function StrategySummaryCard({ result }) {
  const summary = buildStrategySummary(result);

  return (
    <div className="nm-card" style={{ animation: "fadeUp .4s ease .02s both" }}>
      <div className="nm-card-header">
        <span className="nm-card-title">Marketing Strategy Summary</span>
        <span className="nm-badge" style={{ background: "var(--blue-50)", color: "var(--blue-800)", border: "1px solid var(--blue-100)" }}>
          Analysis, not copy
        </span>
      </div>
      <div className="nm-card-body">
        <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
          Before you commit budget to a campaign, here's what the analysis actually found —
          how your customer decides, and which persuasion techniques are worth using.
        </div>

        <SummaryRow
          icon="🧠" title="How the customer decides"
          verdict={summary.customerMindset.verdict} detail={summary.customerMindset.detail}
        />
        <SummaryRow
          icon="⏳" title="Urgency & Scarcity — worth using?"
          verdict={summary.urgency.verdict} detail={summary.urgency.detail}
          verdictColor={summary.urgency.verdict.startsWith("Use carefully") ? "var(--coral-600)" : "var(--teal-600)"}
        />
        <SummaryRow
          icon="💛" title="Emotional Appeal — worth using?"
          verdict={summary.emotional.verdict} detail={summary.emotional.detail}
        />
        <SummaryRow
          icon="⚠️" title="Loss-Framed Messaging — worth using?"
          verdict={summary.lossFraming.verdict} detail={summary.lossFraming.detail}
          verdictColor={summary.lossFraming.verdict === "Use sparingly" ? "var(--coral-600)" : "var(--teal-600)"}
        />

        <div style={{
          marginTop: 14, background: "var(--blue-50)", border: "1px solid var(--blue-100)",
          borderRadius: "var(--radius-md)", padding: "12px 16px",
        }}>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".05em", color: "var(--blue-800)", marginBottom: 4 }}>
            Recommended overall approach
          </div>
          <div style={{ fontSize: 13, color: "var(--blue-800)", lineHeight: 1.6 }}>{summary.overallMix}</div>
        </div>
      </div>
    </div>
  );
}
