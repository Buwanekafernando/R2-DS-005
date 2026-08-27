import { useState, useEffect } from "react";
import { apiPost } from "../api.js";

const CATEGORIES = ["Baby", "Beauty", "Apparel", "Electronics", "Sports", "Pet", "Groceries"];
const EMOTIONS = ["joy", "excitement", "trust", "confidence", "curiosity", "relief", "admiration", "neutral"];

// Literature-backed recommended emotions per category.
const recommendedEmotionByCategory = {
  Baby: ["trust", "relief", "joy"],
  Beauty: ["confidence", "trust", "joy"],
  Apparel: ["joy", "excitement"],
  Electronics: ["excitement", "joy"],
  Sports: ["excitement", "confidence", "trust"],
  Pet: ["joy", "trust"],
  Groceries: ["trust", "relief", "joy"],
};

// First recommended emotion = the auto-selected default for a category.
const defaultEmotionFor = (category) =>
  (recommendedEmotionByCategory[category] || [])[0] || "";

function Field({ label, value }) {
  return (
    <div className="border rounded-lg px-3 py-2">
      <div className="text-xs uppercase text-gray-400">{label}</div>
      <div className="text-sm font-medium">{value}</div>
    </div>
  );
}

// Compact result card, reused for single run and each variation.
function ResultCard({ result }) {
  return (
    <div className="space-y-4">
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
          <div>Color Palette: {result.visual_suggestions.palette}</div>
          <div className="mt-1">Image style: {result.visual_suggestions.image_style}</div>
          <div>Layout Mood: {result.visual_suggestions.layout_mood}</div>
        </div>
      )}
    </div>
  );
}

export default function Component24Page({ baseCopy, sourceProductName }) {
  const [form, setForm] = useState({
    product_name: "",
    category: "Electronics",
    target_audience: "",
    features: "",
    target_emotion: "excitement",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);           // single run
  const [variations, setVariations] = useState([]);     // multi run

  // Pre-fill product name from Component 1 if available
  useEffect(() => {
    if (sourceProductName) setForm((f) => ({ ...f, product_name: sourceProductName }));
  }, [sourceProductName]);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  // recommended emotions for the currently selected category
  const recommended = recommendedEmotionByCategory[form.category] || [];

  // one pipeline call for a given emotion
  const callPipeline = async (emotion) => {
    return apiPost("/component24/pipeline", { ...form, target_emotion: emotion, base_copy: baseCopy || undefined });
  };

  const runPipeline = async () => {
    if (!form.product_name.trim()) { setError("Please enter a product name."); return; }
    setLoading(true); setError(""); setResult(null); setVariations([]);
    try {
      setResult(await callPipeline(form.target_emotion));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Generate one variation per recommended emotion for this category.
  const generateVariations = async () => {
    if (!form.product_name.trim()) { setError("Please enter a product name."); return; }
    const emotions = recommendedEmotionByCategory[form.category] || [];
    if (emotions.length === 0) { setError("No recommended emotions for this category."); return; }

    setLoading(true); setError(""); setResult(null); setVariations([]);
    try {
      const results = [];
      // sequential (not Promise.all) to stay under the Groq rate limit
      for (const emotion of emotions) {
        results.push(await callPipeline(emotion));
      }
      setVariations(results);
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

      {baseCopy && (
        <div className="border rounded-lg px-4 py-3 mb-4 text-sm" style={{ background: "var(--purple-50)", borderColor: "var(--purple-100)", color: "var(--purple-800)" }}>
          Using Component 1's recommended copy as the base for emotional infusion: <em>"{baseCopy.slice(0, 100)}{baseCopy.length > 100 ? "…" : ""}"</em>
        </div>
      )}

      {/* ---- Input ---- */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-2">
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
              setForm({ ...form, category, target_emotion: defaultEmotionFor(category) });
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

          {/* ---- Recommendation chips ---- */}
          {recommended.length > 0 && (
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <span className="text-xs text-gray-500">Recommended for {form.category}:</span>
              {recommended.map((emo) => (
                <button
                  key={emo}
                  type="button"
                  onClick={() => setForm({ ...form, target_emotion: emo })}
                  className={`text-xs rounded-full px-3 py-1 border transition ${
                    form.target_emotion === emo
                      ? "bg-black text-white border-black"
                      : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
                  }`}
                >
                  {emo}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-1">Key features</label>
          <textarea className="w-full border rounded-lg px-3 py-2" rows={2} value={form.features}
            onChange={update("features")} placeholder="e.g. active noise cancellation, 30h battery" />
        </div>
      </div>

      <div className="flex flex-wrap gap-3 mt-4">
        <button onClick={runPipeline} disabled={loading}
          className="bg-black text-white rounded-lg px-5 py-2 disabled:opacity-50">
          {loading ? "Running…" : "Generate"}
        </button>
        <button onClick={generateVariations} disabled={loading}
          className="border border-black rounded-lg px-5 py-2 disabled:opacity-50">
          {loading ? "Generating…" : `Generate variations (${recommended.length})`}
        </button>
      </div>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      {/* ---- Single result ---- */}
      {result && <div className="mt-8"><ResultCard result={result} /></div>}

      {/* ---- Variations (one per recommended emotion) ---- */}
      {variations.length > 0 && (
        <div className="mt-8 space-y-8">
          {variations.map((v, i) => (
            <div key={i}>
              <div className="text-sm font-semibold mb-2">
                Variation {i + 1} — target: {v.target_emotion}
              </div>
              <ResultCard result={v} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}