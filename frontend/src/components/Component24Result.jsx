import CopyButton from "./CopyButton.jsx";
import ResultCode from "./ResultCode.jsx";
import Tooltip from "./Tooltip.jsx";
import { G } from "./Term.jsx";

function Field({ label, value }) {
  return (
    <div className="border rounded-lg px-3 py-2">
      <div className="mini-label">{label}</div>
      <div className="text-sm font-medium">{value}</div>
    </div>
  );
}

// Shared Component 2+4 result card, used by Component24Page and the
// Main Application page. `result` needs: target_emotion, emotion_copy,
// emotion_detected, emotion_matched, loss_message, gain_sentiment,
// loss_sentiment, fomo_score, tone_label, emotion_survived,
// emotion_after_loss, visual_suggestions — the exact shape both
// /component24/pipeline and /generate-strategy's `component24` return.
export default function Component24Result({ result, showJson = true }) {
  const toneIsRisky = result.tone_label?.toLowerCase().includes("negative") || result.tone_label?.toLowerCase().includes("adjust");

  return (
    <div className="space-y-4">
      <div className="nm-card" style={{ margin: 0 }}>
        <div className="nm-card-header"><span className="nm-card-title"><G>Emotional Appeal</G> and <G>Loss-Framed</G> messages</span></div>
      </div>

      <div className="border rounded-xl p-4" style={{ background: "var(--purple-50)", borderColor: "var(--purple-100)" }}>
        <div className="mini-label" style={{ color: "var(--purple-800)", fontWeight: 700 }}>Which one should I use?</div>
        <div className="text-sm" style={{ color: "var(--purple-800)" }}>
          Two versions below, both aimed at the "{result.target_emotion}" feeling. Use the <strong>first (emotional)</strong> version
          for everyday ads and posts. Use the <strong>second (<G>loss-framed</G>)</strong> version sparingly — for limited-time
          promotions only — since it works by making people fear missing out, and using it too often can wear thin.
        </div>
      </div>

      <div className="border rounded-xl p-4">
        <div className="flex items-center justify-between mb-1">
          <div className="mini-label">Feeling version (emotional <G>copy</G>)</div>
          {result.emotion_matched && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: "var(--teal-50)", color: "var(--teal-600)" }}>
              ✓ Hits the target feeling
            </span>
          )}
        </div>
        <p className="mb-2">{result.emotion_copy}</p>
        <CopyButton text={result.emotion_copy} />
        <div className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
          <G>target emotion</G>: <b>{result.target_emotion}</b> · AI found: <b>{result.emotion_detected}</b>{" "}
          {result.emotion_matched
            ? <span style={{ color: "var(--teal-600)", fontWeight: 600 }}>✓ exact match</span>
            : <span style={{ color: "var(--orange-600)", fontWeight: 600 }}>closest achieved</span>}
        </div>
      </div>

      <div className="border rounded-xl p-4">
        <div className="mini-label">"Don't miss out" version (<G>loss-framed</G> copy)</div>
        <p className="mb-2">{result.loss_message}</p>
        <CopyButton text={result.loss_message} />

        <div style={{
          marginTop: 10, padding: "8px 12px", borderRadius: "var(--radius-sm)",
          background: toneIsRisky ? "var(--coral-50)" : "var(--teal-50)",
          color: toneIsRisky ? "var(--coral-600)" : "var(--teal-600)",
          fontSize: 13, fontWeight: 500,
        }}>
          {toneIsRisky
            ? "⚠️ This version leans quite negative — it may come across as guilt-tripping. Consider the emotional version above instead, or use this one only briefly."
            : "✓ This version stays positive enough to feel safe for everyday use."}
        </div>

        <div className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
          <G>Sentiment</G> is scored from -1 (very negative) to +1 (very positive) — see the exact numbers below. {result.fomo_score > 0
            ? `This version uses ${result.fomo_score} "fear of missing out" phrase${result.fomo_score > 1 ? "s" : ""} (e.g. "don't miss", "limited time").`
            : "No strong fear-of-missing-out language was detected in this version."}
        </div>
      </div>

      {result.natural_tone_message && (
        <div className="border rounded-xl p-4">
          <div className="mini-label"><G>Natural-tone</G> version (a conversational rewrite of the loss-framed copy)</div>
          <p className="mb-2">{result.natural_tone_message}</p>
          <CopyButton text={result.natural_tone_message} />
        </div>
      )}

      {/* Explicit labeled metrics — wrapped in a card so the boxes are actually visible */}
      <div className="border rounded-xl p-4">
        <div className="mini-label"><G>Sentiment</G> and safety scores</div>
        <div className="metrics-row">
          <div className="metric-box"><div className="metric-val">{result.gain_sentiment.toFixed(3)}</div><div className="metric-lbl">Gain sentiment<Tooltip text="How positive the emotional version sounds, from -1 (very negative) to +1 (very positive)." /></div></div>
          <div className="metric-box"><div className="metric-val">{result.loss_sentiment.toFixed(3)}</div><div className="metric-lbl">Loss sentiment<Tooltip text="How positive the loss-framed version sounds, from -1 (very negative) to +1 (very positive)." /></div></div>
          <div className="metric-box"><div className="metric-val">{result.fomo_score}</div><div className="metric-lbl"><G>FOMO</G> score<Tooltip text={'FOMO = "Fear Of Missing Out." Counts urgency phrases like "don\'t miss out" or "limited time" in the loss-framed version.'} /></div></div>
        </div>
        <div className="metrics-row" style={{ marginTop: 10 }}>
          <div className="metric-box">
            <div className="metric-val">{result.sentiment_change > 0 ? `+${result.sentiment_change.toFixed(3)}` : result.sentiment_change.toFixed(3)}</div>
            <div className="metric-lbl">Sentiment change<Tooltip text="How much more (or less) positive the loss-framed version is compared to the emotional version." /></div>
          </div>
          <div className="metric-box" style={{ flex: 2 }}>
            <div className="metric-val" style={{ fontSize: 14 }}>{result.tone_label}</div>
            <div className="metric-lbl">Tone safety check<Tooltip text="A safety check that flags if the loss-framed version has gotten too negative or guilt-trippy to feel safe for everyday use." /></div>
          </div>
        </div>
      </div>

      <div className="border rounded-xl p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
        <div className="mini-label">Did the feeling survive the rewrite?</div>
        {result.emotion_survived
          ? <span style={{ color: "var(--teal-600)", fontWeight: 600 }}>✓ Yes — even after reframing around urgency, the copy still comes across as "{result.target_emotion}".</span>
          : <span style={{ color: "var(--coral-600)", fontWeight: 600 }}>✗ Not quite — the urgency reframing shifted the tone away from "{result.target_emotion}" toward "{result.emotion_after_loss}". Consider using the emotional version instead.</span>}
      </div>

      {result.visual_suggestions && (
        <div className="border rounded-xl p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          <div className="mini-label">Visual ideas for ads and social posts</div>
          <div>Colour palette: {result.visual_suggestions.palette}</div>
          <div className="mt-1">Image style: {result.visual_suggestions.image_style}</div>
          <div>Layout mood: {result.visual_suggestions.layout_mood}</div>
        </div>
      )}

      {showJson && <ResultCode title="Result Code (JSON) — Component 2+4" data={result} />}
    </div>
  );
}
