import { useState } from "react";

const API_BASE = "http://localhost:5000";

const CATEGORIES = ["Baby", "Beauty", "Apparel", "Electronics", "Sports", "Pet", "Groceries"];
const EMOTIONS = ["joy", "excitement", "trust", "confidence", "curiosity", "relief", "admiration", "neutral"];

// Auto-fill emotion from category (mirrors backend CATEGORY_EMOTION_MAP first choice).
const CATEGORY_DEFAULT_EMOTION = {
  Baby: "trust", Beauty: "confidence", Apparel: "joy", Electronics: "excitement",
  Sports: "excitement", Pet: "joy", Groceries: "trust",
};

function Field({ label, value }) {
  return (
    <div className="border rounded-lg px-3 py-2">
      <div className="text-xs uppercase text-gray-400">{label}</div>
      <div className="text-sm font-medium">{value}</div>
    </div>
  );
}

export default function Integrate() {
  const [form, setForm] = useState({
    product_name: "",
    category: "Electronics",
    target_audience: "",
    features: "",
    target_emotion: "excitement",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const runPipeline = async () => {
    if (!form.product_name.trim()) { setError("Please enter a product name."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-1">Emotion + Loss Framing Pipeline</h1>
      <p className="text-sm text-gray-500 mb-6">
        The emotion agent generates the copy, the loss framing agent reframes it (with full
        sentiment / FOMO / tone outputs), then RoBERTa checks the emotion survived.
      </p>

      {/* ---- Input ---- */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1">Product name</label>
          <input className="w-full border rounded-lg px-3 py-2" value={form.product_name}
            onChange={update("product_name")} placeholder="e.g. Sony WH-1000XM5" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Category</label>
          <select className="w-full border rounded-lg px-3 py-2" value={form.category}
            onChange={(e) => {
              const category = e.target.value;
              setForm({ ...form, category, target_emotion: CATEGORY_DEFAULT_EMOTION[category] || "" });
            }}>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Target audience</label>
          <input className="w-full border rounded-lg px-3 py-2" value={form.target_audience}
            onChange={update("target_audience")} placeholder="e.g. commuters, remote workers" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Target emotion</label>
          <select className="w-full border rounded-lg px-3 py-2" value={form.target_emotion}
            onChange={update("target_emotion")}>
            {EMOTIONS.map((e) => <option key={e} value={e}>{e}</option>)}
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-1">Key features</label>
          <textarea className="w-full border rounded-lg px-3 py-2" rows={2} value={form.features}
            onChange={update("features")} placeholder="e.g. active noise cancellation, 30h battery" />
        </div>
      </div>

      <button onClick={runPipeline} disabled={loading}
        className="bg-black text-white rounded-lg px-5 py-2 disabled:opacity-50">
        {loading ? "Running pipeline…" : "Run pipeline"}
      </button>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      {/* ---- Output ---- */}
      {result && (
        <div className="mt-8 space-y-4">
          {/* Stage 1: emotion copy (the gain-framed message) */}
          <div className="border rounded-xl p-4">
            <div className="text-xs uppercase text-gray-400 mb-1">Emotion copy (gain-framed)</div>
            <p className="mb-2">{result.emotion_copy}</p>
            <div className="text-sm text-gray-600">
              Target: <b>{result.target_emotion}</b> · Detected: <b>{result.emotion_detected}</b>{" "}
              {result.emotion_matched
                ? <span className="text-green-600">✓ matched</span>
                : <span className="text-amber-600">kept best</span>}{" "}
              · attempts: {result.attempts_used}/3
            </div>
          </div>

          {/* Stage 2: friend's loss agent — all six outputs */}
          <div className="border rounded-xl p-4">
            <div className="text-xs uppercase text-gray-400 mb-1">Loss-framed message</div>
            <p className="mb-3">{result.loss_message}</p>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Gain Sentiment" value={result.gain_sentiment} />
              <Field label="Loss Sentiment" value={result.loss_sentiment} />
              <Field label="FOMO Score" value={`${result.fomo_score} loss keywords`} />
              <Field label="Sentiment Change"
                value={result.sentiment_change > 0 ? `+${result.sentiment_change}` : result.sentiment_change} />
            </div>
            <div className="mt-3">
              <Field label="Tone Safety Check" value={result.tone_label} />
            </div>
          </div>

          {/* Stage 3: emotion survival */}
          <div className="border rounded-xl p-4">
            <div className="text-xs uppercase text-gray-400 mb-1">Emotion survival check</div>
            <div className="text-sm text-gray-600">
              After loss framing, top emotion is <b>{result.emotion_after_loss}</b>{" "}
              (target score {result.emotion_after_score}).{" "}
              {result.emotion_survived
                ? <span className="text-green-600">✓ emotion survived</span>
                : <span className="text-red-600">✗ emotion shifted</span>}
            </div>
          </div>

          {result.visual_suggestions && (
            <div className="border rounded-xl p-4 text-sm text-gray-600">
              <div className="text-xs uppercase text-gray-400 mb-1">Visual guidance</div>
              <div>Palette: {result.visual_suggestions.palette}</div>
              <div>Mood: {result.visual_suggestions.layout_mood}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
