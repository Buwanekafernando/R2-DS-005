import { useEffect, useMemo, useState } from "react";
import { Send } from "lucide-react";

const emotions = [
  "joy",
  "excitement",
  "trust",
  "confidence",
  "curiosity",
  "optimism",
  "relief",
  "admiration",
  "neutral",
];

const scales = [1, 2, 3, 4, 5];

function fieldLabel(key) {
  const map = {
    emotion_strength: "Emotion Strength",
    message_clarity: "Message Clarity",
    persuasiveness: "Persuasiveness",
    trustworthiness: "Trustworthiness",
    engagement_interest: "Engagement / Interest",
    purchase_interest: "Purchase Interest",
  };
  return map[key] || key;
}

function selectClass() {
  return "w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100";
}

export default function UserStudyForm({
  productName,
  category,
  targetEmotion,
  topEmotion,
  validationSuccess,
  attemptsUsed,
  generatedMessage,
  onSubmit,
  loading,
}) {
  const [participantId, setParticipantId] = useState("");
  const [perceivedEmotion, setPerceivedEmotion] = useState(
    targetEmotion || "neutral",
  );
  const [comments, setComments] = useState("");
  const [ratings, setRatings] = useState({
    emotion_strength: 4,
    message_clarity: 4,
    persuasiveness: 4,
    trustworthiness: 4,
    engagement_interest: 4,
    purchase_interest: 4,
  });

  const canSubmit = useMemo(() => {
    return Boolean(
      participantId.trim() && productName && targetEmotion && generatedMessage,
    );
  }, [participantId, productName, targetEmotion, generatedMessage]);

  useEffect(() => {
    setPerceivedEmotion(targetEmotion || "neutral");
  }, [targetEmotion]);

  function updateRating(key, value) {
    setRatings((prev) => ({ ...prev, [key]: Number(value) }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit || loading) return;
    onSubmit({
      participant_id: participantId.trim(),
      product_name: productName,
      category,
      target_emotion: targetEmotion,
      top_emotion: topEmotion,
      validation_success: validationSuccess,
      attempts_used: attemptsUsed,
      generated_message: generatedMessage,
      perceived_emotion: perceivedEmotion,
      ...ratings,
      comments,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="text-sm font-semibold text-slate-900">
        User Study Evaluation
      </div>
      <div className="mt-1 text-sm text-slate-600">
        Rate the generated message from 1 (low) to 5 (high). Responses are saved
        to CSV.
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-sm font-medium text-slate-800">
            Participant ID
          </label>
          <input
            className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            value={participantId}
            onChange={(e) => setParticipantId(e.target.value)}
            placeholder="e.g., P001"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-slate-800">
            Perceived Emotion
          </label>
          <select
            className={selectClass()}
            value={perceivedEmotion}
            onChange={(e) => setPerceivedEmotion(e.target.value)}
          >
            {emotions.map((e) => (
              <option key={e} value={e}>
                {e}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {Object.keys(ratings).map((key) => (
          <div
            key={key}
            className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
          >
            <div className="text-sm font-semibold text-slate-900">
              {fieldLabel(key)}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {scales.map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => updateRating(key, n)}
                  className={[
                    "h-9 w-9 rounded-xl border text-sm font-semibold shadow-sm transition",
                    ratings[key] === n
                      ? "border-blue-500 bg-blue-600 text-white"
                      : "border-slate-200 bg-white text-slate-800 hover:bg-slate-50",
                  ].join(" ")}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <label className="text-sm font-medium text-slate-800">
          Comments (optional)
        </label>
        <textarea
          className="mt-1 h-24 w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Write any feedback about the message..."
        />
      </div>

      <button
        type="submit"
        disabled={!canSubmit || loading}
        className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:opacity-60"
      >
        <Send className="h-4 w-4" />
        Submit Ratings
      </button>

      {!canSubmit ? (
        <div className="mt-2 text-xs text-slate-500">
          Generate a message first, then enter a Participant ID to submit.
        </div>
      ) : null}
    </form>
  );
}
