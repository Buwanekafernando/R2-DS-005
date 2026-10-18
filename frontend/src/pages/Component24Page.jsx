import { useState, useEffect } from "react";
import { apiPost } from "../api.js";
import Component24Result from "../components/Component24Result.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EmotionPicker from "../components/EmotionPicker.jsx";
import { CATEGORIES, CATEGORY_EMOTION_MAP, categoryLabel, defaultEmotionFor, AGENTS } from "../constants.js";
import { G } from "../components/Term.jsx";

export default function Component24Page({ baseCopy, sourceProductName }) {
  const [form, setForm] = useState({
    product_name: "",
    category: "Electronics",
    target_audience: "",
    features: "",
    target_emotion: "excitement",
  });
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);           // single run
  const [variations, setVariations] = useState([]);     // one per suitable feeling

  // Pre-fill product name from Component 1 if available
  useEffect(() => {
    if (sourceProductName) setForm((f) => ({ ...f, product_name: sourceProductName }));
  }, [sourceProductName]);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });
  const recommended = CATEGORY_EMOTION_MAP[form.category] || [];

  // One pipeline call for a given emotion. An empty emotion means "let the
  // backend choose", which it does from the product type.
  const callPipeline = (emotion) =>
    apiPost("/component24/pipeline", { ...form, target_emotion: emotion || null, base_copy: baseCopy || undefined });

  const runPipeline = async () => {
    if (!form.product_name.trim()) { setError("Add a product name first."); return; }
    setLoading(true); setLoadingMsg("Writing your message and checking the feeling…"); setError(""); setResult(null); setVariations([]);
    try {
      setResult(await callPipeline(form.target_emotion));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // One version per suitable feeling for this product type
  const generateVariations = async () => {
    if (!form.product_name.trim()) { setError("Add a product name first."); return; }
    if (recommended.length === 0) { setError("There are no suggested feelings for this product type."); return; }

    setLoading(true); setError(""); setResult(null); setVariations([]);
    try {
      const results = [];
      // One at a time (not all at once) to stay under the Groq rate limit
      for (let i = 0; i < recommended.length; i++) {
        setLoadingMsg(`Writing version ${i + 1} of ${recommended.length} (${recommended[i]})…`);
        results.push(await callPipeline(recommended[i]));
      }
      setVariations(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <PageHeader
        title={`${AGENTS.feeling.emoji} What they feel and would miss`}
        intro={`Try the emotion helpers on their own (${AGENTS.feeling.component}: ${AGENTS.feeling.research}, and ${AGENTS.missout.component}: ${AGENTS.missout.research}). You get a message with one clear feeling, checked by our emotion AI, plus a "don't miss out" version.`}
      />

      {baseCopy && (
        <div className="check-pill tone-info" style={{ display: "block", marginBottom: 16 }}>
          Starting from your "How they decide" message: <em>"{baseCopy.slice(0, 120)}{baseCopy.length > 120 ? "…" : ""}"</em>
        </div>
      )}

      <div className="nm-card">
        <div className="nm-card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-4">
            <div>
              <label className="field-label" htmlFor="c24-name">Product name</label>
              <input id="c24-name" className="nm-input" value={form.product_name} onChange={update("product_name")} placeholder="e.g. Sony WH-1000XM5" />
            </div>
            <div>
              <label className="field-label" htmlFor="c24-cat">Product type</label>
              <select
                id="c24-cat"
                className="nm-select"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value, target_emotion: defaultEmotionFor(e.target.value) })}
              >
                {CATEGORIES.map((c) => <option key={c} value={c}>{categoryLabel(c)}</option>)}
              </select>
            </div>
            <div>
              <label className="field-label" htmlFor="c24-aud">Who usually buys it? <span className="field-optional">optional</span></label>
              <input id="c24-aud" className="nm-input" value={form.target_audience} onChange={update("target_audience")} placeholder="e.g. commuters, remote workers" />
            </div>
            <div>
              <label className="field-label" htmlFor="c24-feat">What makes it special? <span className="field-optional">optional</span></label>
              <input id="c24-feat" className="nm-input" value={form.features} onChange={update("features")} placeholder="e.g. noise cancelling, 30-hour battery" />
            </div>
          </div>

          <span className="field-label" style={{ marginTop: 24 }}>Which feeling should it carry?</span>
          <EmotionPicker value={form.target_emotion} category={form.category} onChange={(v) => setForm({ ...form, target_emotion: v })} />

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 22 }}>
            <button onClick={runPipeline} disabled={loading} className="nm-btn-primary" style={{ flex: "1 1 240px" }}>
              Create message
            </button>
            <button onClick={generateVariations} disabled={loading || recommended.length === 0} className="nm-btn-secondary" style={{ flex: "1 1 240px" }}>
              Compare {recommended.length} suitable feelings
            </button>
          </div>
        </div>
      </div>

      {error && <div className="error-box" role="alert">{error}</div>}

      {loading && (
        <div className="nm-card" aria-live="polite">
          <div className="nm-card-body empty-state">
            <div className="spinner" />
            <div className="empty-title">{loadingMsg}</div>
            <div className="empty-desc"><G>Our emotion AI checks each message and rewrites it if the feeling is off, with up to 3 tries.</G></div>
          </div>
        </div>
      )}

      {result && <div style={{ marginTop: 24 }}><Component24Result result={result} /></div>}

      {variations.length > 0 && (
        <div style={{ marginTop: 24, display: "grid", gap: 28 }}>
          {variations.map((v, i) => (
            <section key={i} aria-label={`Version ${i + 1}`}>
              <h2 className="section-heading" style={{ marginTop: 0, textTransform: "none" }}>
                Version {i + 1}: {v.target_emotion}
              </h2>
              <Component24Result result={v} />
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
