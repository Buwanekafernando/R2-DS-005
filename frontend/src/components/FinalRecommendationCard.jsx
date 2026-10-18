import CopyButton from "./CopyButton.jsx";
import { emotionEmoji } from "../constants.js";
import { Term } from "./Term.jsx";

// The single deliverable: one blended message from all four agents.
//
// If the backend also re-checked this final message (detected_emotion,
// sentiment, fomo_score, tone_label on final_recommendation), those checks
// are shown in plain words with the exact numbers underneath. If an older
// backend doesn't send them, those rows simply don't appear.
export default function FinalRecommendationCard({ rec, productName, celebrate = false }) {
  if (!rec?.recommendation) return null;

  const hasEmotionCheck = !!rec.detected_emotion;
  const hasToneCheck = rec.tone_label != null || rec.sentiment != null;
  const target = rec.target_emotion;

  const whatsapp = `https://wa.me/?text=${encodeURIComponent(rec.recommendation)}`;

  return (
    <section className="result-hero" aria-labelledby="final-title">
      <div className="result-hero-top">
        <h2 id="final-title" className="result-hero-kicker">
          <span aria-hidden="true">✨</span> Your message is ready{productName ? ` for ${productName}` : ""}
        </h2>
        {rec.best_for && (
          <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
            Best for: {rec.best_for}
          </span>
        )}
      </div>

      <p className="result-message">{rec.recommendation}</p>

      <div className="result-actions">
        <CopyButton text={rec.recommendation} size="lg" label="Copy message" />
        <a className="btn-whatsapp" href={whatsapp} target="_blank" rel="noopener noreferrer">
          <span aria-hidden="true">💬</span> Share on WhatsApp
        </a>
      </div>

      {(hasEmotionCheck || hasToneCheck) && (
        <div className="result-section">
          <h3 className="result-section-title">Checks on this message</h3>
          <div className="check-row">
            {hasEmotionCheck && <EmotionCheck rec={rec} target={target} />}
            {hasToneCheck && <ToneCheck rec={rec} />}
            {rec.fomo_score != null && <UrgencyCheck count={rec.fomo_score} />}
          </div>
        </div>
      )}

      {rec.rationale && (
        <div className="result-section">
          <h3 className="result-section-title">Why this works</h3>
          <p style={{ fontSize: 16, color: "var(--text-secondary)", lineHeight: 1.65, maxWidth: "70ch" }}>{rec.rationale}</p>
        </div>
      )}
    </section>
  );
}

function EmotionCheck({ rec, target }) {
  const pct = Math.round((Number(rec.emotion_score) || 0) * 100);
  if (rec.emotion_matched) {
    return (
      <div className="check-pill tone-good">
        <span className="check-icon" aria-hidden="true">{emotionEmoji(target)}</span>
        <span>
          <Term>Feeling check</Term>: comes across as <b style={{ textTransform: "capitalize" }}>{target}</b>
          <small>Our emotion AI (<Term>RoBERTa</Term>) is {pct}% sure</small>
        </span>
      </div>
    );
  }
  return (
    <div className="check-pill tone-info">
      <span className="check-icon" aria-hidden="true">{emotionEmoji(rec.detected_emotion)}</span>
      <span>
        <Term>Feeling check</Term>: aimed for <b>{target}</b>, reads mostly as <b>{rec.detected_emotion}</b> ({pct}%)
        <small>Normal for a blended message, because it also adds urgency and facts.</small>
      </span>
    </div>
  );
}

function ToneCheck({ rec }) {
  const label = String(rec.tone_label || "").toLowerCase();
  const score = rec.sentiment != null ? Number(rec.sentiment) : null;
  const tooNegative = label.includes("negative") || label.includes("adjust");
  const positive = label.includes("positive");
  return (
    <div className={`check-pill ${tooNegative ? "tone-bad" : "tone-good"}`}>
      <span className="check-icon" aria-hidden="true">{tooNegative ? "⚠️" : "🙂"}</span>
      <span>
        <Term>Tone</Term>: {tooNegative ? "too negative, soften it before posting" : positive ? "friendly and positive" : "balanced, safe to use"}
        {score != null && <small><Term>Sentiment</Term> {score.toFixed(2)} on a scale from −1 to +1</small>}
      </span>
    </div>
  );
}

function UrgencyCheck({ count }) {
  const n = Number(count) || 0;
  const strong = n >= 3;
  return (
    <div className={`check-pill ${strong ? "tone-ok" : "tone-good"}`}>
      <span className="check-icon" aria-hidden="true">⏳</span>
      <span>
        {n === 0 ? "No pressure words" : strong ? <>Strong <Term>urgency</Term></> : <>Light <Term>urgency</Term></>}
        <small>
          {n === 0 ? "No \"don't miss out\" phrases" : `${n} "don't miss out" phrase${n === 1 ? "" : "s"}`}
          {strong ? ", best for short promotions" : ""}
        </small>
      </span>
    </div>
  );
}
