import CopyButton from "./CopyButton.jsx";
import ResultCode from "./ResultCode.jsx";
import Tooltip from "./Tooltip.jsx";
import { G } from "./Term.jsx";

const INTENSITY_BG = { low: "var(--teal-50)", medium: "var(--orange-50)", high: "var(--coral-50)" };
const INTENSITY_BORDER = { low: "var(--teal-100)", medium: "var(--orange-100)", high: "var(--coral-100)" };

// Shared Component 3 result card. `data` uses the flat shape:
// { suitability_score, recommended_intensity, intensity_score, reason,
//   trust_status, trust_score, all_copies }
// This is exactly the shape /generate-strategy returns as `component3`.
export default function Component3Result({ data, showJson = true, rawData = null }) {
  const isWarning = data.trust_status?.toLowerCase().includes("warning");

  return (
    <>
      <div className="nm-card">
        <div className="nm-card-header">
          <span className="nm-card-title"><G>Urgency & Scarcity</G>: three strengths to choose from</span>
          <span className="nm-badge" style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}>
            ✓ Done
          </span>
        </div>
        <div className="nm-card-body space-y-3">
          {Object.entries(data.all_copies || {}).map(([intensity, copy]) => {
            const isRec = intensity === data.recommended_intensity;
            return (
              <div key={intensity} style={{ background: INTENSITY_BG[intensity], border: isRec ? `2px solid ${INTENSITY_BORDER[intensity].replace("100", "400")}` : `1px solid ${INTENSITY_BORDER[intensity]}`, borderRadius: "var(--radius-md)", padding: 16 }}>
                {isRec && (
                  <div style={{ background: "var(--orange-400)", color: "var(--on-accent)", fontSize: 13, fontWeight: 700, padding: "4px 10px", borderRadius: "var(--radius-sm)", marginBottom: 8, display: "inline-block", letterSpacing: ".05em" }}>
                    ★ Use this one
                  </div>
                )}
                <div className="copy-label" style={{ color: "var(--text-primary)" }}><G>{`${intensity.charAt(0).toUpperCase() + intensity.slice(1)} intensity`}</G></div>
                <div className="copy-text">{copy}</div>
                <CopyButton text={copy} />
              </div>
            );
          })}
        </div>
      </div>

      <div className="nm-card">
        <div className="nm-card-header"><span className="nm-card-title">Our recommendation</span></div>
        <div className="nm-card-body">
          <div className="strategy-box" style={{ background: "var(--orange-50)", borderColor: "var(--orange-100)" }}>
            <div style={{ width: "100%" }}>
              <div className="strategy-box-label" style={{ color: "var(--orange-600)" }}>
                <G>{`Recommended: ${cap(data.recommended_intensity)} intensity`}</G>
              </div>
              <div className="strategy-box-text" style={{ color: "var(--orange-600)" }}>{data.reason}</div>
            </div>
          </div>

          <div style={{
            background: isWarning ? "var(--coral-50)" : "var(--teal-50)",
            border: `1px solid ${isWarning ? "var(--coral-100)" : "var(--teal-100)"}`,
            borderRadius: "var(--radius-sm)", padding: "10px 14px", marginTop: 12,
            fontSize: 13, color: isWarning ? "var(--coral-600)" : "var(--teal-600)",
            fontWeight: 500,
          }}>
            <G>{isWarning
              ? "⚠️ This messaging is more aggressive than usual for this product — some customers may find it pushy or less believable. Consider a lower intensity, or use it only for short, genuine promotions."
              : "✓ This messaging feels natural and credible — the urgency level matches what customers would expect for this kind of product."}</G>
          </div>

          <div className="metrics-row">
            <div className="metric-box"><div className="metric-val">{(data.suitability_score * 100).toFixed(0)}%</div><div className="metric-lbl">Fits this product<Tooltip text="How well urgency/scarcity messaging suits this type of product in general." /></div></div>
            <div className="metric-box"><div className="metric-val">{(data.trust_score * 100).toFixed(0)}%</div><div className="metric-lbl">Feels trustworthy<Tooltip text="How believable this urgency messaging will feel to a real customer. A lower score isn't an error — it's a heads-up to use this messaging carefully." /></div></div>
            <div className="metric-box"><div className="metric-val">{cap(data.recommended_intensity)}</div><div className="metric-lbl">Recommended level<Tooltip text="How strongly to push urgency: Low is subtle, High is aggressive (e.g. 'only 2 left!')." /></div></div>
          </div>

          <div style={{ marginTop: 14 }}>
            <span className="nm-badge" style={{ background: "var(--orange-50)", color: "var(--orange-600)", border: "1px solid var(--orange-100)", marginRight: 6 }}>Scarcity principle</span>
            <span className="nm-badge" style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}>Urgency & scarcity</span>
          </div>
        </div>
      </div>

      {showJson && <ResultCode title="Result Code (JSON) — Component 3" data={rawData || data} />}
    </>
  );
}

function cap(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
}
