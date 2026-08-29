import CopyButton from "./CopyButton.jsx";
import ResultCode from "./ResultCode.jsx";

const INTENSITY_BG = { low: "var(--teal-50)", medium: "var(--amber-50)", high: "var(--coral-50)" };
const INTENSITY_BORDER = { low: "var(--teal-100)", medium: "var(--amber-100)", high: "var(--coral-100)" };

// Shared Component 3 result card. `data` uses the flat shape:
// { suitability_score, recommended_intensity, intensity_score, reason,
//   trust_status, trust_score, all_copies }
// This is exactly the shape /generate-strategy returns as `component3`.
export default function Component3Result({ data, showJson = true, rawData = null }) {
  const isWarning = data.trust_status?.toLowerCase().includes("warning");

  return (
    <>
      <div className="nm-card" style={{ animation: "fadeUp .4s ease" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">3 · Scarcity Optimization — Strategies</span>
          <span className="nm-badge" style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}>
            ✓ AI Analysed
          </span>
        </div>
        <div className="nm-card-body space-y-3">
          {Object.entries(data.all_copies || {}).map(([intensity, copy]) => {
            const isRec = intensity === data.recommended_intensity;
            return (
              <div key={intensity} style={{ background: INTENSITY_BG[intensity], border: isRec ? `2px solid ${INTENSITY_BORDER[intensity].replace("100", "400")}` : `1px solid ${INTENSITY_BORDER[intensity]}`, borderRadius: "var(--radius-md)", padding: 16 }}>
                {isRec && (
                  <div style={{ background: "var(--amber-400)", color: "#fff", fontSize: 11, fontWeight: 700, padding: "4px 10px", borderRadius: "var(--radius-sm)", marginBottom: 8, display: "inline-block", letterSpacing: ".05em" }}>
                    ★ USE THIS ONE
                  </div>
                )}
                <div className="copy-label" style={{ color: "var(--text-primary)" }}>{intensity.toUpperCase()} INTENSITY</div>
                <div className="copy-text">{copy}</div>
                <CopyButton text={copy} />
              </div>
            );
          })}
        </div>
      </div>

      <div className="nm-card" style={{ animation: "fadeUp .4s ease .1s both" }}>
        <div className="nm-card-header"><span className="nm-card-title">AI Recommendation</span></div>
        <div className="nm-card-body">
          <div className="strategy-box" style={{ background: "var(--amber-50)", borderColor: "var(--amber-100)" }}>
            <div style={{ width: "100%" }}>
              <div className="strategy-box-label" style={{ color: "var(--amber-600)" }}>
                Recommended: {data.recommended_intensity?.toUpperCase()} Intensity
              </div>
              <div className="strategy-box-text" style={{ color: "var(--amber-600)" }}>{data.reason}</div>
            </div>
          </div>

          <div style={{
            background: isWarning ? "var(--coral-50)" : "var(--teal-50)",
            border: `1px solid ${isWarning ? "var(--coral-100)" : "var(--teal-100)"}`,
            borderRadius: "var(--radius-sm)", padding: "10px 14px", marginTop: 12,
            fontSize: 13, color: isWarning ? "var(--coral-600)" : "var(--teal-600)",
            fontWeight: 500,
          }}>
            {isWarning
              ? "⚠️ This messaging is more aggressive than usual for this product — some customers may find it pushy or less believable. Consider a lower intensity, or use it only for short, genuine promotions."
              : "✓ This messaging feels natural and credible — the urgency level matches what customers would expect for this kind of product."}
          </div>

          <div className="metrics-row">
            <div className="metric-box"><div className="metric-val">{(data.suitability_score * 100).toFixed(0)}%</div><div className="metric-lbl">Fits This Product</div></div>
            <div className="metric-box"><div className="metric-val">{(data.trust_score * 100).toFixed(0)}%</div><div className="metric-lbl">Feels Trustworthy</div></div>
            <div className="metric-box"><div className="metric-val">{data.recommended_intensity?.toUpperCase()}</div><div className="metric-lbl">Recommended Level</div></div>
          </div>

          <div style={{ marginTop: 14 }}>
            <span className="nm-badge" style={{ background: "var(--amber-50)", color: "var(--amber-600)", border: "1px solid var(--amber-100)", marginRight: 6 }}>SCARCITY PRINCIPLE</span>
            <span className="nm-badge" style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}>RESEARCH COMPONENT 3</span>
          </div>
        </div>
      </div>

      {showJson && <ResultCode title="Result Code (JSON) — Component 3" data={rawData || data} />}
    </>
  );
}
