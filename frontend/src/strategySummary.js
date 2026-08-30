// Builds a decision-oriented strategy summary directly from the measured
// scores each agent already produced — no extra AI call needed, so this
// stays grounded in what was actually measured (trust score, suitability
// score, whether the target emotion was matched, the tone safety check)
// rather than a fresh AI guess layered on top of the other four.
export function buildStrategySummary(result) {
  const c1 = result.component1_full?.classification;
  const c3 = result.component3;
  const c24 = result.component24;

  // 1. How the customer thinks about this product
  const isEmotionalBuyer = c1?.cognitive_mode === "System1";
  const confidencePct = c1 ? Math.round(c1.confidence * 100) : null;
  const customerMindset = {
    verdict: !c1 ? "Not analyzed" : isEmotionalBuyer ? "Emotional, impulse-driven buyer" : "Rational, research-driven buyer",
    detail: !c1 ? "" : isEmotionalBuyer
      ? `${confidencePct}% confidence customers decide on feeling and instinct rather than comparing specs — lead with sensory, emotional language over technical detail.`
      : `${confidencePct}% confidence customers research and compare before buying — lead with clear facts, numbers, and proof over emotional appeals.`,
  };

  // 2. Does this product need Urgency & Scarcity messaging
  const trustSafe = c3 && !c3.trust_status?.toLowerCase().includes("warning");
  const urgency = {
    verdict: !c3 ? "Not analyzed" : trustSafe
      ? `Yes — ${c3.recommended_intensity} intensity fits well`
      : `Use carefully — ${c3.recommended_intensity} intensity risks feeling pushy`,
    detail: !c3 ? "" : trustSafe
      ? `This product suits urgency messaging (${Math.round(c3.suitability_score * 100)}% fit) without hurting customer trust.`
      : `Scarcity language triggered a trust warning here — dial back the intensity, or reserve it for genuine limited-time offers rather than everyday listings.`,
  };

  // 3. Does this product benefit from Emotional Appeal
  const emotional = {
    verdict: !c24 ? "Not analyzed" : c24.emotion_matched
      ? `Yes — lead with "${c24.target_emotion}"`
      : `Partially — aimed for "${c24.target_emotion}", closest achieved was "${c24.emotion_detected}"`,
    detail: !c24 ? "" : c24.emotion_matched
      ? `The AI successfully wrote copy that genuinely reads as ${c24.target_emotion} — safe to use as your primary emotional angle across ads and listings.`
      : `The AI couldn't fully lock in "${c24.target_emotion}" after 3 attempts — the copy still works, but treat the emotional angle as a starting point worth refining rather than a finished asset.`,
  };

  // 4. Is Loss-Framed Messaging appropriate here
  const toneOk = c24 && !c24.tone_label?.toLowerCase().includes("too negative");
  const lossFraming = {
    verdict: !c24 ? "Not analyzed" : toneOk ? "Safe to use" : "Use sparingly",
    detail: !c24 ? "" : toneOk
      ? "The loss-framed version stayed positive enough for everyday use — fine for regular campaigns, not just emergencies."
      : "The loss-framed version leans quite negative — save it for genuine limited-time promotions rather than everyday ads, so it doesn't come across as a guilt trip.",
  };

  // Overall one-line recommended mix
  const mixParts = [];
  if (c1) mixParts.push(isEmotionalBuyer ? "lead with emotional, sensory copy" : "lead with clear, fact-based copy");
  if (c3) mixParts.push(trustSafe ? `add ${c3.recommended_intensity}-level urgency` : "keep urgency light and occasional");
  if (c24) mixParts.push(toneOk ? "loss-framing is fine for regular use" : "save loss-framing for real limited-time promotions only");
  const overallMix = mixParts.length ? mixParts.join("; ") + "." : "Not enough data to summarize.";

  return { customerMindset, urgency, emotional, lossFraming, overallMix };
}
