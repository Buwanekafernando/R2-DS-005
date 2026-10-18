import { useEffect, useState } from "react";
import { apiPost } from "../api.js";
import Component3Result from "../components/Component3Result.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { usePersistedState, clearPersisted } from "../usePersistedState.js";
import { AGENTS, CATEGORIES } from "../constants.js";
import { G } from "../components/Term.jsx";

// Same 7 product types as every other page (see CATEGORIES in constants.js).
const FIXED_CATEGORIES = CATEGORIES;

const DEFAULT_FORM = {
  productName: "Luxury Handbag",
  description: "Authentic leather, handcrafted for a professional look.",
  price: 99.0,
  category: "Apparel",
};

export default function Component3Page({ baseCopy, sourceProductName }) {
  const [form, setForm] = usePersistedState("nm_component3_form", DEFAULT_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  // If Component 1 has produced a recommended_copy, offer it as the base copy
  useEffect(() => {
    if (baseCopy) {
      setForm((f) => ({
        ...f,
        description: baseCopy,
        productName: sourceProductName || f.productName,
      }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseCopy, sourceProductName]);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const clearForm = () => {
    setForm(DEFAULT_FORM);
    setResults(null);
    setError("");
    clearPersisted("nm_component3_form");
  };

  const activate = async () => {
    if (!form.productName.trim() || !form.description.trim()) return;
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const painData = await apiPost("/component3/extract-pain-points", { text: form.description });
      const painPoints = painData.pain_points || [];

      const data = await apiPost("/component3/analyze", {
        product_name: form.productName,
        base_copy: form.description,
        price: Number(form.price) || 0,
        category: form.category,
        pain_points: painPoints,
      });
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page page-wide">
      <PageHeader
        title={`${AGENTS.urgency.emoji} Why act now`}
        intro={`Try the urgency helper on its own (${AGENTS.urgency.component}: ${AGENTS.urgency.research}). It writes low, medium and high urgency versions of your message, picks the one that fits, and checks it still feels believable.`}
      />

      <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_1.7fr] gap-8">
        <div>
          <div className="nm-card">
            <div className="nm-card-header">
              <h2 className="nm-card-title">Your product</h2>
              <button className="link-btn" onClick={clearForm}>Clear</button>
            </div>
            <div className="nm-card-body">
              <label className="field-label" htmlFor="c3-name">Product name</label>
              <input id="c3-name" className="nm-input" value={form.productName} onChange={update("productName")} />

              <label className="field-label" htmlFor="c3-cat">Product type</label>
              <select id="c3-cat" className="nm-select" value={form.category} onChange={update("category")}>
                {FIXED_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>

              <label className="field-label" htmlFor="c3-desc">Your message or product description</label>
              <p className="field-help">
                {baseCopy
                  ? "Filled in from your \"How they decide\" result. Change it if you like."
                  : "Tip: try \"How they decide\" first and its message is filled in here for you."}
              </p>
              <textarea id="c3-desc" className="nm-textarea" rows={4} value={form.description} onChange={update("description")} />

              <label className="field-label" htmlFor="c3-price">Price</label>
              <div className="input-prefix">
                <span aria-hidden="true">Rs.</span>
                <input id="c3-price" className="nm-input" type="number" inputMode="decimal" min="0" step="0.01" value={form.price} onChange={update("price")} />
              </div>
            </div>
          </div>

          <button className="nm-btn-primary" disabled={loading || !form.productName.trim() || !form.description.trim()} onClick={activate}>
            {loading ? "Adding urgency…" : "Add urgency to my message"}
          </button>
        </div>

        <div>
          {error && <div className="error-box" role="alert" style={{ marginTop: 0, marginBottom: 12 }}>{error}</div>}

          {!results && !loading && (
            <div className="nm-card">
              <div className="nm-card-body empty-state">
                <div className="empty-icon" style={{ background: "var(--orange-50)", border: "1px solid var(--orange-100)" }} aria-hidden="true">{AGENTS.urgency.emoji}</div>
                <div className="empty-title">Your urgency options will appear here</div>
                <div className="empty-desc"><G>Fill in your product, then press "Add urgency to my message".</G></div>
              </div>
            </div>
          )}

          {loading && (
            <div className="nm-card" aria-live="polite">
              <div className="nm-card-body empty-state">
                <div className="spinner" />
                <div className="empty-title">Checking how much urgency fits…</div>
                <div className="empty-desc"><G>Writing three versions and scoring which suits this product. About 5 to 10 seconds.</G></div>
              </div>
            </div>
          )}

          {results && (
            <Component3Result
              data={{
                suitability_score: results.suitability_score,
                recommended_intensity: results.recommendation.recommended_intensity,
                intensity_score: results.recommendation.intensity_score,
                reason: results.recommendation.reason,
                trust_status: results.trust.status,
                trust_score: results.trust.score,
                all_copies: results.all_copies,
              }}
              rawData={results}
            />
          )}
        </div>
      </div>
    </div>
  );
}
