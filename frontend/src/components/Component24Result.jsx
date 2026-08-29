import CopyButton from "./CopyButton.jsx";
import ResultCode from "./ResultCode.jsx";

function Field({ label, value }) {
  return (
    <div className="border rounded-lg px-3 py-2">
      <div className="text-xs uppercase text-gray-400">{label}</div>
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
        <div className="nm-card-header"><span className="nm-card-title">2 → 4 · Emotion Propagation + Loss Framing</span></div>
      </div>

      <div className="border rounded-xl p-4" style={{ background: "var(--purple-50)", borderColor: "var(--purple-100)" }}>
        <div className="text-xs uppercase tracking-wide mb-1" style={{ color: "var(--purple-800)", fontWeight: 700 }}>Which one should I use?</div>
        <div className="text-sm" style={{ color: "var(--purple-800)" }}>
          Two versions below, both aimed at the "{result.target_emotion}" feeling. Use the <strong>first (emotional)</strong> version
          for everyday ads and posts. Use the <strong>second (loss-framed)</strong> version sparingly — for limited-time
          promotions only — since it works by making people fear missing out, and using it too often can wear thin.
        </div>
      </div>

      <div className="border rounded-xl p-4">
        <div className="flex items-center justify-between mb-1">
          <div className="text-xs uppercase text-gray-400">Emotional Copy</div>
          {result.emotion_matched && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: "var(--teal-50)", color: "var(--teal-600)" }}>
              ✓ Hits the target feeling
            </span>
          )}
        </div>
        <p className="mb-2">{result.emotion_copy}</p>
        <CopyButton text={result.emotion_copy} />
        <div className="text-sm text-gray-600 mt-2">
          Aimed for: <b>{result.target_emotion}</b> · AI detected: <b>{result.emotion_detected}</b>{" "}
          {result.emotion_matched
            ? <span className="text-green-600">✓ exact match</span>
            : <span className="text-amber-600">closest achieved</span>}
        </div>
      </div>

      <div className="border rounded-xl p-4">
        <div className="text-xs uppercase text-gray-400 mb-1">Loss-Framed Copy (urgency version)</div>
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

        <div className="text-xs text-gray-500 mt-3">
          Positivity is scored from -1 (very negative) to +1 (very positive) — see the exact numbers below. {result.fomo_score > 0
            ? `This version uses ${result.fomo_score} "fear of missing out" phrase${result.fomo_score > 1 ? "s" : ""} (e.g. "don't miss", "limited time").`
            : "No strong fear-of-missing-out language was detected in this version."}
        </div>
      </div>

      {/* Explicit labeled metrics — wrapped in a card so the boxes are actually visible */}
      <div className="border rounded-xl p-4">
        <div className="text-xs uppercase text-gray-400 mb-3">Sentiment & Safety Metrics</div>
        <div className="metrics-row">
          <div className="metric-box"><div className="metric-val">{result.gain_sentiment.toFixed(3)}</div><div className="metric-lbl">Gain Sentiment</div></div>
          <div className="metric-box"><div className="metric-val">{result.loss_sentiment.toFixed(3)}</div><div className="metric-lbl">Loss Sentiment</div></div>
          <div className="metric-box"><div className="metric-val">{result.fomo_score}</div><div className="metric-lbl">FOMO Score</div></div>
        </div>
        <div className="metrics-row" style={{ marginTop: 10 }}>
          <div className="metric-box">
            <div className="metric-val">{result.sentiment_change > 0 ? `+${result.sentiment_change.toFixed(3)}` : result.sentiment_change.toFixed(3)}</div>
            <div className="metric-lbl">Sentiment Change</div>
          </div>
          <div className="metric-box" style={{ flex: 2 }}>
            <div className="metric-val" style={{ fontSize: 14 }}>{result.tone_label}</div>
            <div className="metric-lbl">Tone Safety Check</div>
          </div>
        </div>
      </div>

      <div className="border rounded-xl p-4 text-sm text-gray-600">
        <div className="text-xs uppercase text-gray-400 mb-1">Did the feeling survive the rewrite?</div>
        {result.emotion_survived
          ? <span className="text-green-600">✓ Yes — even after reframing around urgency, the copy still comes across as "{result.target_emotion}".</span>
          : <span className="text-red-600">✗ Not quite — the urgency reframing shifted the tone away from "{result.target_emotion}" toward "{result.emotion_after_loss}". Consider using the emotional version instead.</span>}
      </div>

      {result.visual_suggestions && (
        <div className="border rounded-xl p-4 text-sm text-gray-600">
          <div className="text-xs uppercase text-gray-400 mb-1">Visual guidance for ads/social posts</div>
          <div>Color Palette: {result.visual_suggestions.palette}</div>
          <div className="mt-1">Image style: {result.visual_suggestions.image_style}</div>
          <div>Layout Mood: {result.visual_suggestions.layout_mood}</div>
        </div>
      )}

      {showJson && <ResultCode title="Result Code (JSON) — Component 2+4" data={result} />}
    </div>
  );
}
