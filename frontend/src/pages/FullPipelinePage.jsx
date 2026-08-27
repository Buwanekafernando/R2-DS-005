import { useState } from "react";
import { apiPost } from "../api.js";

const CATEGORIES = ["Beauty", "Electronics", "Apparel", "Grocery", "Baby", "Pet Products", "Sports"];
const EMOTIONS = ["joy", "excitement", "trust", "confidence", "curiosity", "relief", "admiration", "neutral"];

const STAGES = [
  { id: "c1", n: "1", label: "Dual-System\nReasoning" },
  { id: "c3", n: "3", label: "Scarcity\nOptimization" },
  { id: "c2", n: "2", label: "Emotion\nPropagation" },
  { id: "c4", n: "4", label: "Loss\nFraming" },
];

export default function FullPipelinePage() {
  const [form, setForm] = useState({
    product_name: "",
    product_text: "",
    category: CATEGORIES[0],
    price: 0,
    target_audience: "",
    features: "",
    target_emotion: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const run = async () => {
    if (!form.product_name.trim() || !form.product_text.trim()) {
      setError("Please enter both a product name and product description.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await apiPost("/generate-strategy", {
        ...form,
        price: Number(form.price) || 0,
        target_emotion: form.target_emotion || null,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto px-10 py-8">
      <h1 className="font-display" style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-1px", marginBottom: 6 }}>
        Full Pipeline — Synthesized Strategy
      </h1>
      <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 20, maxWidth: 640 }}>
        Runs all four agents from one product input: Component 1 classifies the product and writes
        the base copy, Component 3 layers scarcity messaging on top of it, and Component 2 → 4 infuse
        emotion into that same base copy before reframing it around loss aversion.
      </p>

      {/* ── Agent chain ── */}
      <div className="chain-wrap">
        {STAGES.map((s, i) => (
          <div key={s.id} style={{ display: "flex", alignItems: "flex-start", flex: i < STAGES.length - 1 ? 1 : "0 0 auto" }}>
            <div className="chain-node">
              <div className={`chain-circle ${result ? "done" : loading ? "active" : ""}`}>{s.n}</div>
              <div className="chain-label">{s.label.split("\n").map((l, j) => <div key={j}>{l}</div>)}</div>
            </div>
            {i < STAGES.length - 1 && <div className={`chain-line ${result ? "done" : ""}`} />}
          </div>
        ))}
      </div>

      {/* ── Input ── */}
      <div className="nm-card">
        <div className="nm-card-header"><span className="nm-card-title">Product Input</span></div>
        <div className="nm-card-body grid grid-cols-1 md:grid-cols-2 gap-x-4">
          <div>
            <span className="field-label">Product Name</span>
            <input className="nm-input" value={form.product_name} onChange={update("product_name")} placeholder="e.g. Sony WH-1000XM5" />
          </div>
          <div>
            <span className="field-label">Category</span>
            <select className="nm-select" value={form.category} onChange={update("category")}>
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="md:col-span-2">
            <span className="field-label">Product Description</span>
            <textarea className="nm-textarea" rows={3} value={form.product_text} onChange={update("product_text")}
              placeholder="Full product description, as fed to Component 1" />
          </div>
          <div>
            <span className="field-label">Price</span>
            <input className="nm-input" type="number" min="0" step="0.01" value={form.price} onChange={update("price")} />
          </div>
          <div>
            <span className="field-label">Target Emotion (optional — auto-selected from category if left blank)</span>
            <select className="nm-select" value={form.target_emotion} onChange={update("target_emotion")}>
              <option value="">Auto-select</option>
              {EMOTIONS.map((e) => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>
          <div>
            <span className="field-label">Target Audience</span>
            <input className="nm-input" value={form.target_audience} onChange={update("target_audience")} placeholder="e.g. commuters, remote workers" />
          </div>
          <div>
            <span className="field-label">Key Features</span>
            <input className="nm-input" value={form.features} onChange={update("features")} placeholder="e.g. ANC, 30h battery" />
          </div>
        </div>
      </div>

      <button className="nm-btn-primary" disabled={loading} onClick={run}>
        {loading ? "Running all four agents…" : "Generate Full Strategy"}
      </button>

      {error && <p className="text-sm mt-3" style={{ color: "var(--coral-600)" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 28 }}>
          {/* Component 1 */}
          <div className="nm-card" style={{ animation: "fadeUp .4s ease" }}>
            <div className="nm-card-header">
              <span className="nm-card-title">1 · Dual-System Reasoning</span>
              <span className="nm-badge" style={{ background: "var(--blue-50)", color: "var(--blue-800)", border: "1px solid var(--blue-100)" }}>
                {result.component1.cognitive_mode} · {(result.component1.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="nm-card-body">
              <div className="copy-text">{result.component1.recommended_copy}</div>
              <div className="copy-meta" style={{ color: "var(--text-muted)", marginTop: 8 }}>Strategy: {result.component1.strategy}</div>
            </div>
          </div>

          {/* Component 3 */}
          <div className="nm-card" style={{ animation: "fadeUp .4s ease .1s both" }}>
            <div className="nm-card-header">
              <span className="nm-card-title">3 · Scarcity Optimization</span>
              <span className="nm-badge" style={{ background: "var(--amber-50)", color: "var(--amber-600)", border: "1px solid var(--amber-100)" }}>
                {result.component3.recommended_intensity.toUpperCase()} intensity
              </span>
            </div>
            <div className="nm-card-body">
              <div className="copy-text">{result.component3.final_copy}</div>
              <div className="copy-meta" style={{ color: "var(--text-muted)", marginTop: 8 }}>
                {result.component3.reason} · Trust: {result.component3.trust_status} ({(result.component3.trust_score * 100).toFixed(0)}%)
              </div>
              {result.component3.pain_points_detected?.length > 0 && (
                <div style={{ marginTop: 8, fontSize: 12, color: "var(--text-muted)" }}>
                  Pain points used: {result.component3.pain_points_detected.join(", ")}
                </div>
              )}
            </div>
          </div>

          {/* Component 2 + 4 */}
          <div className="nm-card" style={{ animation: "fadeUp .4s ease .2s both" }}>
            <div className="nm-card-header">
              <span className="nm-card-title">2 → 4 · Emotion Propagation + Loss Framing</span>
              <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
                Target: {result.component24.target_emotion}
              </span>
            </div>
            <div className="nm-card-body">
              <div className="copy-grid">
                <div className="copy-card" style={{ background: "var(--teal-50)", border: "1px solid var(--teal-100)" }}>
                  <div className="copy-label" style={{ color: "var(--teal-600)" }}>Gain-Framed (Emotion)</div>
                  <div className="copy-text">{result.component24.emotion_copy}</div>
                  <div className="copy-meta" style={{ color: "var(--teal-600)" }}>
                    Detected: {result.component24.emotion_detected} {result.component24.emotion_matched ? "✓ matched" : "· kept best"}
                  </div>
                </div>
                <div className="copy-card" style={{ background: "var(--coral-50)", border: "1px solid var(--coral-100)" }}>
                  <div className="copy-label" style={{ color: "var(--coral-600)" }}>Loss-Framed</div>
                  <div className="copy-text">{result.component24.loss_message}</div>
                  <div className="copy-meta" style={{ color: "var(--coral-600)" }}>
                    FOMO: {result.component24.fomo_score} · Tone: {result.component24.tone_label}
                  </div>
                </div>
              </div>
              <div className="metrics-row">
                <div className="metric-box"><div className="metric-val">{result.component24.gain_sentiment}</div><div className="metric-lbl">Gain Sentiment</div></div>
                <div className="metric-box"><div className="metric-val">{result.component24.loss_sentiment}</div><div className="metric-lbl">Loss Sentiment</div></div>
                <div className="metric-box"><div className="metric-val">{result.component24.emotion_survived ? "Yes" : "No"}</div><div className="metric-lbl">Emotion Survived</div></div>
              </div>
            </div>
          </div>

          <div className="nm-card" style={{ animation: "fadeUp .4s ease .3s both" }}>
            <div className="nm-card-header"><span className="nm-card-title">Full Synthesized Output (JSON)</span></div>
            <div className="nm-card-body">
              <pre className="nm-json">{JSON.stringify(result, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
