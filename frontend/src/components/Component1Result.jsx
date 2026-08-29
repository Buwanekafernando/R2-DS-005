import { useState } from "react";
import CopyButton from "./CopyButton.jsx";
import ResultCode from "./ResultCode.jsx";
import { apiPost } from "../api.js";

// The full, rich Component 1 result card — shared between Component1Page
// and the Main Application page so both show identical detail.
// `result` must be the full AnalysisResult shape: { classification, generated_copy, recommendation, agent_output }
export default function Component1Result({ result, showJson = true, productText = "", category = "" }) {
  const clf      = result.classification;
  const gen      = result.generated_copy;
  const rec      = result.recommendation;

  const isS1      = clf.cognitive_mode === "System1";
  const bg        = isS1 ? "var(--amber-50)"  : "var(--blue-50)";
  const bdr       = isS1 ? "var(--amber-100)" : "var(--blue-100)";
  const txt       = isS1 ? "var(--amber-600)" : "var(--blue-800)";
  const bar       = isS1 ? "var(--amber-400)" : "var(--blue-600)";
  const modeLabel = isS1
    ? "Emotional / Impulse Buy Product"
    : "Rational / Research-Based Buy Product";
  const plainMeaning = isS1
    ? "Consumers are likely to buy this based on feeling and instinct, not research."
    : "Consumers typically research and compare before buying this product.";

  const strategy  = rec.strategy;
  const isEmoRec  = strategy === "emotional";
  const winningCopy = isEmoRec ? gen.emotional.text : gen.rational.text;

  const [channelVariants, setChannelVariants] = useState(null);
  const [channelLoading, setChannelLoading] = useState(false);
  const [channelError, setChannelError] = useState("");

  const generateChannelVariants = async () => {
    setChannelLoading(true);
    setChannelError("");
    try {
      const data = await apiPost("/component1/channel-variants", {
        product_text: productText || winningCopy,
        category: category || "unknown",
        winning_copy: winningCopy,
      });
      setChannelVariants(data);
    } catch (err) {
      setChannelError(err.message);
    } finally {
      setChannelLoading(false);
    }
  };

  return (
    <>
      {/* Classification Result */}
      <div className="nm-card" style={{ animation: "fadeUp .4s ease" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">1 · Dual-System Reasoning — Classification Result</span>
          <span className="nm-badge" style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}>
            ✓ AI Analysed
          </span>
        </div>
        <div className="nm-card-body">
          <div className="clf-badge" style={{ background: bg, borderColor: bdr }}>
            <div className="clf-mode" style={{ color: txt }}>{modeLabel}</div>
            <div style={{ fontSize: 11, color: txt, marginBottom: 4 }}>Confidence</div>
            <div className="clf-bar-wrap">
              <div className="clf-bar" style={{ width: `${clf.confidence * 100}%`, background: bar }} />
            </div>
            <div style={{ fontSize: 13, color: txt, fontWeight: 700, marginTop: 4 }}>
              {(clf.confidence * 100).toFixed(0)}% confident in this classification
            </div>
          </div>

          <div style={{
            background: isS1 ? "var(--amber-50)" : "var(--blue-50)",
            border: `1px solid ${isS1 ? "var(--amber-100)" : "var(--blue-100)"}`,
            borderRadius: "var(--radius-sm)", padding: "8px 12px", marginTop: 10,
            fontSize: 13, color: isS1 ? "var(--amber-600)" : "var(--blue-800)",
            fontWeight: 500,
          }}>
            💡 {plainMeaning}
          </div>

          <div style={{ fontSize: 12, color: "var(--text-muted)", fontStyle: "italic", marginTop: 8, lineHeight: 1.6 }}>
            {clf.reasoning}
          </div>
        </div>
      </div>

      {/* Generated Marketing Copy */}
      <div className="nm-card" style={{ animation: "fadeUp .4s ease .1s both" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">Generated Marketing Copy</span>
        </div>
        <div className="nm-card-body">
          <div className="copy-grid">
            <div className="copy-card" style={{ background: "var(--amber-50)", border: isEmoRec ? "2px solid var(--amber-400)" : "1px solid var(--amber-100)" }}>
              {isEmoRec && (
                <div style={{ background: "var(--amber-400)", color: "#fff", fontSize: 11, fontWeight: 700, padding: "4px 10px", borderRadius: "var(--radius-sm)", marginBottom: 8, display: "inline-block", letterSpacing: ".05em" }}>
                  ★ USE THIS ONE
                </div>
              )}
              <div className="copy-label" style={{ color: "var(--amber-600)" }}>⚡ Emotional Copy</div>
              <div className="copy-text" style={{ color: "#3d2200" }}>{gen.emotional.text}</div>
              <div className="copy-meta" style={{ color: "var(--amber-600)" }}>
                Tone Score: {gen.emotional.quality.sentiment_compound.toFixed(2)} · Content Quality: {(gen.emotional.quality.mode_alignment * 100).toFixed(0)}%
              </div>
              <CopyButton text={gen.emotional.text} />
            </div>

            <div className="copy-card" style={{ background: "var(--blue-50)", border: !isEmoRec ? "2px solid var(--blue-600)" : "1px solid var(--blue-100)" }}>
              {!isEmoRec && (
                <div style={{ background: "var(--blue-600)", color: "#fff", fontSize: 11, fontWeight: 700, padding: "4px 10px", borderRadius: "var(--radius-sm)", marginBottom: 8, display: "inline-block", letterSpacing: ".05em" }}>
                  ★ USE THIS ONE
                </div>
              )}
              <div className="copy-label" style={{ color: "var(--blue-800)" }}>🔍 Rational Copy</div>
              <div className="copy-text" style={{ color: "#0a2d52" }}>{gen.rational.text}</div>
              <div className="copy-meta" style={{ color: "var(--blue-800)" }}>
                Tone Score: {gen.rational.quality.sentiment_compound.toFixed(2)} · Content Quality: {(gen.rational.quality.mode_alignment * 100).toFixed(0)}%
              </div>
              <CopyButton text={gen.rational.text} />
            </div>
          </div>

          <div className="strategy-box" style={{ background: isEmoRec ? "var(--amber-50)" : "var(--blue-50)", borderColor: isEmoRec ? "var(--amber-100)" : "var(--blue-100)" }}>
            <div style={{ width: "100%" }}>
              <div className="strategy-box-label" style={{ color: isEmoRec ? "var(--amber-600)" : "var(--blue-800)" }}>
                What to do with this result
              </div>
              <div className="strategy-box-text" style={{ color: isEmoRec ? "var(--amber-600)" : "var(--blue-800)", marginBottom: 8 }}>
                {isEmoRec
                  ? "This product sells through emotion. Use the emotional copy above in your ads, social media posts, or product listing to connect with buyers instantly."
                  : "This product sells through logic. Use the rational copy above in your ads, product listings, or emails to help buyers make a confident decision."}
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: isEmoRec ? "var(--amber-600)" : "var(--blue-800)", borderTop: `1px solid ${isEmoRec ? "var(--amber-100)" : "var(--blue-100)"}`, paddingTop: 8, marginTop: 4 }}>
                ✓ Click the Copy button on the highlighted copy above and paste it into your
                Facebook ad, Instagram post, product listing, or email campaign.
              </div>
            </div>
          </div>

          <div className="metrics-row">
            <div className="metric-box"><div className="metric-val">{(clf.confidence * 100).toFixed(0)}%</div><div className="metric-lbl">AI Confidence</div></div>
            <div className="metric-box"><div className="metric-val">{(gen.emotional.quality.mode_alignment * 100).toFixed(0)}%</div><div className="metric-lbl">Emotional Quality</div></div>
            <div className="metric-box"><div className="metric-val">{(gen.rational.quality.mode_alignment * 100).toFixed(0)}%</div><div className="metric-lbl">Rational Quality</div></div>
          </div>
        </div>
      </div>

      {/* Channel-specific copy formats */}
      <div className="nm-card" style={{ animation: "fadeUp .4s ease .15s both" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">More Copy Formats</span>
        </div>
        <div className="nm-card-body">
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
            The paragraph above works as a starting point, but a Facebook ad, an Instagram caption,
            a product listing, and a marketing email all need different lengths and structures.
            Generate ready-to-use versions of your winning copy for each.
          </div>

          {!channelVariants && (
            <button className="nm-btn-secondary" disabled={channelLoading} onClick={generateChannelVariants} style={{ width: "100%" }}>
              {channelLoading ? "Generating formats…" : "Generate Social Media, Listing & Email Copy"}
            </button>
          )}
          {channelError && <p className="text-sm mt-2" style={{ color: "var(--coral-600)" }}>{channelError}</p>}

          {channelVariants && (
            <div className="space-y-3">
              <div className="copy-card" style={{ background: "var(--teal-50)", border: "1px solid var(--teal-100)" }}>
                <div className="copy-label" style={{ color: "var(--teal-600)" }}>📱 Social Media Caption</div>
                <div className="copy-text" style={{ whiteSpace: "pre-line" }}>{channelVariants.social_media}</div>
                <CopyButton text={channelVariants.social_media} />
              </div>
              <div className="copy-card" style={{ background: "var(--purple-50)", border: "1px solid var(--purple-100)" }}>
                <div className="copy-label" style={{ color: "var(--purple-800)" }}>🛒 Product Listing</div>
                <div className="copy-text" style={{ whiteSpace: "pre-line" }}>{channelVariants.product_listing}</div>
                <CopyButton text={channelVariants.product_listing} />
              </div>
              <div className="copy-card" style={{ background: "var(--coral-50)", border: "1px solid var(--coral-100)" }}>
                <div className="copy-label" style={{ color: "var(--coral-600)" }}>✉️ Email Campaign</div>
                <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 4 }}>Subject: {channelVariants.email_subject}</div>
                <div className="copy-text">{channelVariants.email_body}</div>
                <CopyButton text={`Subject: ${channelVariants.email_subject}\n\n${channelVariants.email_body}`} />
              </div>
              <button className="nm-btn-ghost" onClick={generateChannelVariants} disabled={channelLoading}>
                {channelLoading ? "Regenerating…" : "↻ Regenerate these formats"}
              </button>
            </div>
          )}
        </div>
      </div>

      {showJson && <ResultCode title="Result Code (JSON) — full Component 1 response" data={result} />}
    </>
  );
}
