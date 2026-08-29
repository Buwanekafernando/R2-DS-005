import { useEffect, useState } from "react";
import { apiPost } from "../api.js";
import Component3Result from "../components/Component3Result.jsx";
import { usePersistedState, clearPersisted } from "../usePersistedState.js";

const FIXED_CATEGORIES = ["Apparel", "Baby", "Beauty", "Electronics", "Grocery", "Pet Products", "Sports"];

const DEFAULT_FORM = {
  productName: "Luxury Handbag",
  description: "Authentic leather, handcrafted for a professional look.",
  price: 99.0,
  category: FIXED_CATEGORIES[0],
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
    <div className="max-w-[1280px] mx-auto px-10 py-8 grid grid-cols-1 lg:grid-cols-[1.1fr_1.7fr] gap-8">
      {/* ── Left: input ── */}
      <div>
        <div className="nm-card">
          <div className="nm-card-header">
            <span className="nm-card-title">Product Details</span>
            <button
              onClick={clearForm}
              style={{ fontSize: 11, color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}
            >
              Clear form
            </button>
          </div>
          <div className="nm-card-body">
            <span className="field-label">Product Name</span>
            <input className="nm-input" value={form.productName} onChange={update("productName")} />

            <span className="field-label">Category</span>
            <select className="nm-select" value={form.category} onChange={update("category")}>
              {FIXED_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>

            <span className="field-label">Product Description / Base Copy</span>
            <textarea className="nm-textarea" rows={3} value={form.description} onChange={update("description")} />
            {baseCopy && (
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                Pre-filled from your Buying Psychology result — edit freely.
              </div>
            )}

            <span className="field-label">Price</span>
            <input className="nm-input" type="number" min="0" step="0.01" value={form.price} onChange={update("price")} />
          </div>
        </div>

        <button className="nm-btn-primary" disabled={loading || !form.productName.trim() || !form.description.trim()} onClick={activate}>
          {loading ? "Activating Agent…" : "Activate Scarcity Agent"}
        </button>
      </div>

      {/* ── Right: results ── */}
      <div>
        {error && <p className="text-sm mb-3" style={{ color: "var(--coral-600)" }}>{error}</p>}

        {!results && !loading && (
          <div className="nm-card">
            <div className="nm-card-body">
              <div className="empty-state">
                <div className="empty-title">Waiting for Research Input</div>
                <div className="empty-desc">Enter product details and activate the agent to see scarcity-optimized strategies.</div>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="nm-card">
            <div className="nm-card-body">
              <div className="empty-state">
                <div style={{
                  width: 40, height: 40, borderRadius: "50%",
                  border: "3px solid var(--border)",
                  borderTop: "3px solid var(--coral-400)",
                  animation: "spin 1s linear infinite",
                  margin: "0 auto 16px",
                }} />
                <div className="empty-title" style={{ fontSize: 14 }}>Checking urgency fit…</div>
                <div className="empty-desc">Scoring how well scarcity messaging suits this product. Usually takes about 5–10 seconds.</div>
              </div>
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
  );
}
