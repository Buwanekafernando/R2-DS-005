import CopyButton from "./CopyButton.jsx";

// The quick "two alternate options" card — pulls Component 3's scarcity
// copy and Component 4's loss-framed message directly (not blended, unlike
// FinalRecommendationCard). Shared between the Main Application page and
// History so a reopened past strategy looks identical to when it was
// first generated.
export default function TwoMessagesSummaryCard({ result }) {
  if (!result?.component3 || !result?.component24) return null;

  return (
    <div className="nm-card" style={{ background: "var(--text-primary)", border: "none" }}>
      <div className="nm-card-body">
        <div style={{ color: "var(--surface)", fontFamily: "Plus Jakarta Sans, sans-serif", fontWeight: 700, fontSize: 14, marginBottom: 14 }}>
          Two more ready-to-use marketing messages for "{result.product}"
        </div>
        <div className="copy-grid">
          <div className="copy-card" style={{ background: "rgba(255,255,255,0.08)" }}>
            <div className="copy-label" style={{ color: "var(--orange-100)" }}>Urgency-driven</div>
            <div className="copy-text" style={{ color: "var(--surface)" }}>{result.component3.final_copy}</div>
            <CopyButton text={result.component3.final_copy} />
          </div>
          <div className="copy-card" style={{ background: "rgba(255,255,255,0.08)" }}>
            <div className="copy-label" style={{ color: "var(--coral-100)" }}>Emotion + loss-driven</div>
            <div className="copy-text" style={{ color: "var(--surface)" }}>{result.component24.loss_message}</div>
            <CopyButton text={result.component24.loss_message} />
          </div>
        </div>
        <div style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 10 }}>
          Full breakdown of how each was produced is below.
        </div>
      </div>
    </div>
  );
}
