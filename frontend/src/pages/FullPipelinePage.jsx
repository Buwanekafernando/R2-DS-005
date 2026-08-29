import { useState } from "react";
import { apiPost } from "../api.js";
import CopyButton from "../components/CopyButton.jsx";
import ResultCode from "../components/ResultCode.jsx";
import Component1Result from "../components/Component1Result.jsx";
import Component3Result from "../components/Component3Result.jsx";
import Component24Result from "../components/Component24Result.jsx";
import FinalRecommendationCard from "../components/FinalRecommendationCard.jsx";
import {
  CATEGORIES, EMOTIONS, defaultDemographics, defaultEmotionFor, CATEGORY_EMOTION_MAP,
  GENDER_OPTIONS, AGE_OPTIONS, DISTRICTS, OCCUPATION_OPTIONS, SPENDING_OPTIONS, CULTURE_OPTIONS,
} from "../constants.js";
import { usePersistedState, clearPersisted } from "../usePersistedState.js";
import { saveToHistory } from "../history.js";
import { downloadStrategy } from "../exportStrategy.js";

const STAGES = [
  { id: "c1", n: "1", label: "Buying\nPsychology" },
  { id: "c3", n: "2", label: "Urgency &\nScarcity" },
  { id: "c2", n: "3", label: "Emotional\nAppeal" },
  { id: "c4", n: "4", label: "Loss-Framed\nMessaging" },
];

const DEFAULT_FORM = {
  product_name: "",
  product_text: "",
  category: CATEGORIES[0],
  price: 0,
  target_audience: "",
  features: "",
  target_emotion: "",
};

export default function FullPipelinePage() {
  const [form, setForm] = usePersistedState("nm_pipeline_form", DEFAULT_FORM);
  const [demo, setDemo] = usePersistedState("nm_pipeline_demo", defaultDemographics());
  const [wasAutoFilled, setWasAutoFilled] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const recommendedEmotions = CATEGORY_EMOTION_MAP[form.category] || [];

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });
  const updateDemo = (key) => (e) => setDemo({ ...demo, [key]: e.target.value });

  const clearForm = () => {
    setForm(DEFAULT_FORM);
    setDemo(defaultDemographics());
    setWasAutoFilled(true);
    setResult(null);
    setError("");
    clearPersisted("nm_pipeline_form");
    clearPersisted("nm_pipeline_demo");
  };

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
        demographics: demo,
      });
      setResult(data);
      saveToHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto px-10 py-8">
      <h1 className="font-display" style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-1px", marginBottom: 6 }}>
        Main Application — Build Your Strategy
      </h1>
      <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 20, maxWidth: 640 }}>
        Fill in your product once, and this hands you two ready-to-use marketing messages: one
        built around urgency, one built around emotion and what the customer stands to lose by not
        buying. Buying Psychology runs first and its copy feeds into both the urgency and emotional
        strategies below.
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
        <div className="nm-card-header">
          <span className="nm-card-title">Product Input</span>
          <button
            onClick={clearForm}
            style={{ fontSize: 11, color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}
          >
            Clear form
          </button>
        </div>
        <div className="nm-card-body grid grid-cols-1 md:grid-cols-2 gap-x-4">
          <div>
            <span className="field-label">Product Name</span>
            <input className="nm-input" value={form.product_name} onChange={update("product_name")} placeholder="e.g. Sony WH-1000XM5" />
          </div>
          <div>
            <span className="field-label">Category</span>
            <select
              className="nm-select"
              value={form.category}
              onChange={(e) => {
                const category = e.target.value;
                // Auto-fill the target emotion to match the new category,
                // but only if the user hasn't manually picked one already —
                // don't clobber an intentional choice.
                const shouldAutoFill = !form.target_emotion || wasAutoFilled;
                setForm({
                  ...form,
                  category,
                  target_emotion: shouldAutoFill ? defaultEmotionFor(category) : form.target_emotion,
                });
                if (shouldAutoFill) setWasAutoFilled(true);
              }}
            >
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="md:col-span-2">
            <span className="field-label">Product Description</span>
            <textarea className="nm-textarea" rows={3} value={form.product_text} onChange={update("product_text")}
              placeholder="Full product description — this is what the AI will analyze" />
          </div>
          <div>
            <span className="field-label">Price</span>
            <input className="nm-input" type="number" min="0" step="0.01" value={form.price} onChange={update("price")} />
          </div>
          <div>
            <span className="field-label">Target Emotion</span>
            <select
              className="nm-select"
              value={form.target_emotion}
              onChange={(e) => { setForm({ ...form, target_emotion: e.target.value }); setWasAutoFilled(false); }}
            >
              <option value="">Auto-select</option>
              {EMOTIONS.map((e) => <option key={e} value={e}>{e}</option>)}
            </select>
            {recommendedEmotions.length > 0 && (
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <span className="text-xs text-gray-500">Recommended for {form.category}:</span>
                {recommendedEmotions.map((emo) => (
                  <button
                    key={emo}
                    type="button"
                    onClick={() => { setForm({ ...form, target_emotion: emo }); setWasAutoFilled(false); }}
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

      {/* ── Customer Details ── */}
      <div className="nm-card">
        <div className="nm-card-header">
          <span className="nm-card-title">Customer Details</span>
          <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
            Who you're selling to
          </span>
        </div>
        <div className="nm-card-body">
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
            This shapes how confident the AI is about how your customer decides to buy — a rough
            profile of a typical customer is enough, it doesn't need to be exact.
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4">
            <div>
              <span className="field-label">Gender</span>
              <select className="nm-select" value={demo.gender} onChange={updateDemo("gender")}>
                {GENDER_OPTIONS.map((o) => <option key={o}>{o}</option>)}
              </select>
              <span className="field-label">Age Range</span>
              <select className="nm-select" value={demo.age_range} onChange={updateDemo("age_range")}>
                {AGE_OPTIONS.map((o) => <option key={o}>{o}</option>)}
              </select>
              <span className="field-label">District</span>
              <select className="nm-select" value={demo.district} onChange={updateDemo("district")}>
                {DISTRICTS.map((o) => <option key={o}>{o}</option>)}
              </select>
            </div>
            <div>
              <span className="field-label">Occupation</span>
              <select className="nm-select" value={demo.occupation} onChange={updateDemo("occupation")}>
                {OCCUPATION_OPTIONS.map((o) => <option key={o}>{o}</option>)}
              </select>
              <span className="field-label">Monthly Spending</span>
              <select className="nm-select" value={demo.monthly_spending} onChange={updateDemo("monthly_spending")}>
                {SPENDING_OPTIONS.map((o) => <option key={o}>{o}</option>)}
              </select>
              <span className="field-label">Cultural Influence</span>
              <select className="nm-select" value={demo.culture_influence} onChange={updateDemo("culture_influence")}>
                {CULTURE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>
        </div>
      </div>

      <button className="nm-btn-primary" disabled={loading} onClick={run}>
        {loading ? "Generating your strategy…" : "Generate Full Strategy"}
      </button>
      {loading && (
        <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 8, textAlign: "center" }}>
          This usually takes 15–30 seconds — four AI steps are running one after another.
        </div>
      )}

      {error && <p className="text-sm mt-3" style={{ color: "var(--coral-600)" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 28 }}>
          {/* ── Plain-language summary — the actual takeaway, up top ── */}
          <div className="nm-card" style={{ animation: "fadeUp .4s ease", background: "var(--text-primary)", border: "none" }}>
            <div className="nm-card-body">
              <div style={{ color: "var(--surface)", fontFamily: "Syne, sans-serif", fontWeight: 700, fontSize: 14, marginBottom: 14 }}>
                Two ready-to-use marketing messages for "{result.product}"
              </div>
              <div className="copy-grid">
                <div className="copy-card" style={{ background: "rgba(255,255,255,0.08)" }}>
                  <div className="copy-label" style={{ color: "var(--amber-100)" }}>Urgency-driven</div>
                  <div className="copy-text" style={{ color: "var(--surface)" }}>{result.component3.final_copy}</div>
                  <CopyButton text={result.component3.final_copy} />
                </div>
                <div className="copy-card" style={{ background: "rgba(255,255,255,0.08)" }}>
                  <div className="copy-label" style={{ color: "var(--coral-100)" }}>Emotion + loss-driven</div>
                  <div className="copy-text" style={{ color: "var(--surface)" }}>{result.component24.loss_message}</div>
                  <CopyButton text={result.component24.loss_message} />
                </div>
              </div>
              <div style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 10 }}>
                Full breakdown of how each was produced is below.
              </div>
            </div>
          </div>

          {/* AI disclaimer + download */}
          <div style={{
            display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10,
            background: "var(--amber-50)", border: "1px solid var(--amber-100)", borderRadius: "var(--radius-md)",
            padding: "12px 16px", marginBottom: 16,
          }}>
            <div style={{ fontSize: 12, color: "var(--amber-600)", maxWidth: 480 }}>
              ⚠️ This copy was written by AI. Please double-check any facts, numbers, or claims
              against your real product before publishing it in an ad or listing.
              <div style={{ marginTop: 4, color: "var(--teal-600)" }}>✓ Automatically saved to your History tab.</div>
            </div>
            <button className="nm-btn-secondary" style={{ width: "auto", padding: "8px 16px", fontSize: 13 }} onClick={() => downloadStrategy(result)}>
              ⬇ Download full strategy
            </button>
          </div>

          {/* Component 1 — full detail, same card as its own page */}
          <Component1Result result={result.component1_full} showJson={false} productText={form.product_text} category={form.category} />

          {/* Component 3 — full detail, same card as its own page */}
          <Component3Result data={result.component3} rawData={result.component3} showJson={false} />

          {/* Component 2 + 4 — full detail, same card as its own page */}
          <Component24Result result={result.component24} showJson={false} />

          {/* Synthesis step — blends all four analyses into one final answer */}
          <FinalRecommendationCard rec={result.final_recommendation} />

          <ResultCode title="Result Code (JSON) — full synthesized output" data={result} />
        </div>
      )}
    </div>
  );
}
