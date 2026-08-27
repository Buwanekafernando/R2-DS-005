import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../api.js";

const FIXED_CATEGORIES = ["Apparel", "Baby", "Beauty", "Electronics", "Grocery", "Pet Products", "Sports"];

const INTENSITY_BG = { low: "var(--teal-50)", medium: "var(--amber-50)", high: "var(--coral-50)" };
const INTENSITY_BORDER = { low: "var(--teal-100)", medium: "var(--amber-100)", high: "var(--coral-100)" };

export default function Component3Page({ baseCopy, sourceProductName }) {
  const [allProducts, setAllProducts] = useState([]);
  const [category, setCategory] = useState(FIXED_CATEGORIES[0]);
  const [search, setSearch] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);

  const [productName, setProductName] = useState("Luxury Handbag");
  const [description, setDescription] = useState("Authentic leather, handcrafted for a professional look.");
  const [price, setPrice] = useState(99.0);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  useEffect(() => {
    apiGet("/dataset/sample-products").then(setAllProducts).catch(() => {});
  }, []);

  // If Component 1 has produced a recommended_copy, offer it as the base copy
  useEffect(() => {
    if (baseCopy) {
      setDescription(baseCopy);
      if (sourceProductName) setProductName(sourceProductName);
    }
  }, [baseCopy, sourceProductName]);

  const filtered = search
    ? allProducts.filter((p) => p.category === category && p.name.toLowerCase().includes(search.toLowerCase())).slice(0, 10)
    : [];

  const pickProduct = (p) => {
    setSelectedProduct(p);
    setProductName(p.name);
    setCategory(p.category);
    setSearch("");
  };

  const activate = async () => {
    if (!productName.trim() || !description.trim()) return;
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const painData = await apiPost("/component3/extract-pain-points", { text: description });
      const painPoints = selectedProduct?.pain_points?.length ? selectedProduct.pain_points : (painData.pain_points || []);

      const data = await apiPost("/component3/analyze", {
        product_name: productName,
        base_copy: description,
        price: Number(price) || 0,
        category,
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
          <div className="nm-card-header"><span className="nm-card-title">Product Lookup</span></div>
          <div className="nm-card-body">
            <span className="field-label">Select Market Category</span>
            <select className="nm-select" value={category} onChange={(e) => { setCategory(e.target.value); setSelectedProduct(null); }}>
              {FIXED_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>

            <span className="field-label">Search Product</span>
            <input className="nm-input" placeholder="Type to search products…" value={search} onChange={(e) => setSearch(e.target.value)} />

            {filtered.length > 0 && (
              <div className="space-y-2 mt-2">
                {filtered.map((p, i) => (
                  <button key={i} className="nm-btn-ghost" onClick={() => pickProduct(p)}>{p.name}</button>
                ))}
              </div>
            )}
            {selectedProduct && (
              <div style={{ marginTop: 10, fontSize: 12, color: "var(--teal-600)" }}>
                Selected: <strong>{selectedProduct.name}</strong>{" "}
                <button className="underline" style={{ color: "var(--coral-600)" }} onClick={() => setSelectedProduct(null)}>clear</button>
              </div>
            )}
          </div>
        </div>

        <div className="nm-card">
          <div className="nm-card-header"><span className="nm-card-title">Product Details</span></div>
          <div className="nm-card-body">
            <span className="field-label">Product Name</span>
            <input className="nm-input" value={productName} onChange={(e) => setProductName(e.target.value)} />

            <span className="field-label">Product Description / Base Copy</span>
            <textarea className="nm-textarea" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
            {baseCopy && (
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                Pre-filled from Component 1's recommended copy — edit freely.
              </div>
            )}

            <span className="field-label">Price</span>
            <input className="nm-input" type="number" min="0" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} />
          </div>
        </div>

        <button className="nm-btn-primary" disabled={loading || !productName.trim() || !description.trim()} onClick={activate}>
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

        {results && (
          <>
            <div className="nm-card" style={{ animation: "fadeUp .4s ease" }}>
              <div className="nm-card-header"><span className="nm-card-title">Scarcity-Optimized Strategies</span></div>
              <div className="nm-card-body space-y-3">
                {Object.entries(results.all_copies).map(([intensity, copy]) => (
                  <div key={intensity} style={{ background: INTENSITY_BG[intensity], border: `1px solid ${INTENSITY_BORDER[intensity]}`, borderRadius: "var(--radius-md)", padding: 16 }}>
                    <div className="copy-label" style={{ color: "var(--text-primary)" }}>{intensity.toUpperCase()} INTENSITY</div>
                    <div className="copy-text">{copy}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="nm-card" style={{ animation: "fadeUp .4s ease .1s both" }}>
              <div className="nm-card-header"><span className="nm-card-title">AI Recommendation</span></div>
              <div className="nm-card-body">
                <div className="strategy-box" style={{ background: "var(--amber-50)", borderColor: "var(--amber-100)" }}>
                  <div>
                    <div className="strategy-box-label" style={{ color: "var(--amber-600)" }}>
                      Recommended: {results.recommendation.recommended_intensity.toUpperCase()} Intensity
                    </div>
                    <div className="strategy-box-text" style={{ color: "var(--amber-600)" }}>{results.recommendation.reason}</div>
                  </div>
                </div>
                <div className="metrics-row">
                  <div className="metric-box"><div className="metric-val">{(results.trust.score * 100).toFixed(0)}%</div><div className="metric-lbl">Trust Retained</div></div>
                  <div className="metric-box"><div className="metric-val">{results.recommendation.recommended_intensity.toUpperCase()}</div><div className="metric-lbl">Recommended</div></div>
                  <div className="metric-box"><div className="metric-val">{results.trust.status}</div><div className="metric-lbl">Status</div></div>
                </div>
                <div style={{ marginTop: 14 }}>
                  <span className="nm-badge" style={{ background: "var(--amber-50)", color: "var(--amber-600)", border: "1px solid var(--amber-100)", marginRight: 6 }}>SCARCITY PRINCIPLE</span>
                  <span className="nm-badge" style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}>RESEARCH COMPONENT 3</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
