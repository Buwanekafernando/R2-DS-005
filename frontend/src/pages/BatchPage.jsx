import { useState } from "react";
import { apiPost } from "../api.js";
import { usePersistedState, clearPersisted } from "../usePersistedState.js";
import { CATEGORIES } from "../constants.js";
import CopyButton from "../components/CopyButton.jsx";

const EMPTY_ROW = () => ({ product_text: "", category: CATEGORIES[0] });
const MAX_PRODUCTS = 10;

export default function BatchPage() {
  const [rows, setRows] = usePersistedState("nm_batch_rows", [EMPTY_ROW(), EMPTY_ROW()]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  const updateRow = (i, key) => (e) => {
    const updated = [...rows];
    updated[i] = { ...updated[i], [key]: e.target.value };
    setRows(updated);
  };

  const addRow = () => {
    if (rows.length >= MAX_PRODUCTS) return;
    setRows([...rows, EMPTY_ROW()]);
  };

  const removeRow = (i) => {
    setRows(rows.filter((_, idx) => idx !== i));
  };

  const clearAll = () => {
    setRows([EMPTY_ROW(), EMPTY_ROW()]);
    setResults(null);
    setError("");
    clearPersisted("nm_batch_rows");
  };

  const run = async () => {
    const validRows = rows.filter((r) => r.product_text.trim());
    if (validRows.length === 0) {
      setError("Add at least one product description.");
      return;
    }
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const data = await apiPost("/component1/batch-analyze", validRows);
      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto px-10 py-8">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div>
          <h1 className="font-display" style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-1px", marginBottom: 6 }}>
            Batch Mode — Multiple Products
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, maxWidth: 600 }}>
            Have a whole catalog to work through? Add up to {MAX_PRODUCTS} products here and get
            each one's Buying Psychology classification and recommended copy in one go — faster
            than doing them one at a time on the Main Application page.
          </p>
        </div>
        <button
          onClick={clearAll}
          style={{ fontSize: 12, color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline", whiteSpace: "nowrap" }}
        >
          Clear all
        </button>
      </div>

      <div style={{
        background: "var(--purple-50)", border: "1px solid var(--purple-100)", borderRadius: "var(--radius-md)",
        padding: "10px 14px", fontSize: 12, color: "var(--purple-800)", marginBottom: 16,
      }}>
        Note: Batch Mode only runs Buying Psychology (classification + copy) for speed — it doesn't
        add urgency or emotional messaging. Use the Main Application page for the full strategy on
        any one product.
      </div>

      <div className="nm-card">
        <div className="nm-card-body space-y-3">
          {rows.map((row, i) => (
            <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <textarea
                  className="nm-textarea"
                  rows={2}
                  placeholder={`Product ${i + 1} description — e.g. "Sony WH-1000XM5 headphones, 30h battery, ANC"`}
                  value={row.product_text}
                  onChange={updateRow(i, "product_text")}
                />
              </div>
              <div style={{ width: 160 }}>
                <select className="nm-select" value={row.category} onChange={updateRow(i, "category")}>
                  {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
              <button
                onClick={() => removeRow(i)}
                disabled={rows.length <= 1}
                style={{ fontSize: 12, color: "var(--coral-600)", background: "none", border: "none", cursor: "pointer", padding: "10px 4px", opacity: rows.length <= 1 ? 0.3 : 1 }}
              >
                ✕
              </button>
            </div>
          ))}

          {rows.length < MAX_PRODUCTS && (
            <button className="nm-btn-ghost" onClick={addRow}>+ Add another product ({rows.length}/{MAX_PRODUCTS})</button>
          )}
        </div>
      </div>

      <button className="nm-btn-primary" disabled={loading} onClick={run}>
        {loading ? "Analyzing all products…" : `Analyze ${rows.filter((r) => r.product_text.trim()).length || ""} Products`}
      </button>
      {loading && (
        <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 8, textAlign: "center" }}>
          This takes about 5–10 seconds per product, run one after another.
        </div>
      )}

      {error && <p className="text-sm mt-3" style={{ color: "var(--coral-600)" }}>{error}</p>}

      {results && (
        <div style={{ marginTop: 24 }} className="space-y-3">
          {results.map((r, i) => (
            <div key={i} className="nm-card" style={{ margin: 0 }}>
              <div className="nm-card-body">
                {r.success ? (
                  <>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span className="nm-badge" style={{
                        background: r.data.classification.cognitive_mode === "System1" ? "var(--amber-50)" : "var(--blue-50)",
                        color: r.data.classification.cognitive_mode === "System1" ? "var(--amber-600)" : "var(--blue-800)",
                        border: `1px solid ${r.data.classification.cognitive_mode === "System1" ? "var(--amber-100)" : "var(--blue-100)"}`,
                      }}>
                        {r.data.classification.cognitive_mode === "System1" ? "Emotional" : "Rational"} · {(r.data.classification.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 6 }}>{r.data.input.product_text}</div>
                    <div className="copy-text">{r.data.agent_output.recommended_copy}</div>
                    <CopyButton text={r.data.agent_output.recommended_copy} />
                  </>
                ) : (
                  <div style={{ color: "var(--coral-600)", fontSize: 13 }}>
                    Couldn't analyze "{r.product?.slice(0, 60)}…": {r.error}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
