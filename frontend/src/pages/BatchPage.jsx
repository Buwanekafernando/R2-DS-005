import { useEffect, useState } from "react";
import { apiPost } from "../api.js";
import { usePersistedState, clearPersisted } from "../usePersistedState.js";
import { CATEGORIES, categoryLabel, validCategory } from "../constants.js";
import CopyButton from "../components/CopyButton.jsx";
import PageHeader from "../components/PageHeader.jsx";

const EMPTY_ROW = () => ({ product_text: "", category: CATEGORIES[0] });
const MAX_PRODUCTS = 10;

export default function BatchPage() {
  const [rows, setRows] = usePersistedState("nm_batch_rows", [EMPTY_ROW(), EMPTY_ROW()]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  // Rows saved by an older version may use a product type that's no longer offered
  useEffect(() => {
    if (rows.some((r) => validCategory(r.category) !== r.category)) {
      setRows(rows.map((r) => ({ ...r, category: validCategory(r.category) })));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filled = rows.filter((r) => r.product_text.trim()).length;

  const updateRow = (i, key) => (e) => {
    const updated = [...rows];
    updated[i] = { ...updated[i], [key]: e.target.value };
    setRows(updated);
  };

  const addRow = () => { if (rows.length < MAX_PRODUCTS) setRows([...rows, EMPTY_ROW()]); };
  const removeRow = (i) => setRows(rows.filter((_, idx) => idx !== i));

  const clearAll = () => {
    setRows([EMPTY_ROW(), EMPTY_ROW()]);
    setResults(null);
    setError("");
    clearPersisted("nm_batch_rows");
  };

  const run = async () => {
    const validRows = rows.filter((r) => r.product_text.trim());
    if (validRows.length === 0) {
      setError("Describe at least one product first.");
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
    <div className="page">
      <PageHeader
        title="Many products at once"
        intro={`Add up to ${MAX_PRODUCTS} products and get a quick message for each one. This uses only the first AI helper (how customers decide), so it's faster but simpler than the full message.`}
        aside={<button className="link-btn" onClick={clearAll}>Clear all</button>}
      />

      <div className="nm-card">
        <div className="nm-card-body" style={{ display: "grid", gap: 18 }}>
          {rows.map((row, i) => (
            <div key={i} role="group" aria-label={`Product ${i + 1}`}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <span className="field-label" style={{ margin: 0 }}>Product {i + 1}</span>
                {rows.length > 1 && (
                  <button type="button" className="link-btn danger" onClick={() => removeRow(i)} aria-label={`Remove product ${i + 1}`}>
                    Remove
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-[1fr_220px] gap-3">
                <textarea
                  className="nm-textarea"
                  rows={2}
                  aria-label={`Product ${i + 1} description`}
                  placeholder="Name and a short description, e.g. Sony WH-1000XM5 headphones, 30-hour battery, noise cancelling"
                  value={row.product_text}
                  onChange={updateRow(i, "product_text")}
                />
                <select className="nm-select" aria-label={`Product ${i + 1} type`} value={row.category} onChange={updateRow(i, "category")}>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{categoryLabel(c)}</option>)}
                </select>
              </div>
            </div>
          ))}

          {rows.length < MAX_PRODUCTS && (
            <button className="nm-btn-ghost" onClick={addRow} style={{ textAlign: "center" }}>
              + Add another product ({rows.length} of {MAX_PRODUCTS})
            </button>
          )}
        </div>
      </div>

      <button className="nm-btn-primary" disabled={loading} onClick={run}>
        {loading ? "Writing messages…" : filled > 0 ? `Write messages for ${filled} product${filled === 1 ? "" : "s"}` : "Write messages"}
      </button>
      {loading && (
        <p style={{ fontSize: 15, color: "var(--text-secondary)", marginTop: 10, textAlign: "center" }} aria-live="polite">
          Working through them one by one. Allow about 5 to 10 seconds per product.
        </p>
      )}

      {error && <div className="error-box" role="alert">{error}</div>}

      {results && (
        <section style={{ marginTop: 28 }} aria-label="Results">
          <h2 className="section-heading" style={{ marginTop: 0 }}>Your messages</h2>
          <div style={{ display: "grid", gap: 12 }}>
            {results.map((r, i) => {
              if (!r.success) {
                return (
                  <div key={i} className="error-box" style={{ marginTop: 0 }}>
                    Couldn't write a message for "{r.product?.slice(0, 60)}…". {r.error}
                  </div>
                );
              }
              const feeling = r.data.classification.cognitive_mode === "System1";
              return (
                <article key={i} className="nm-card" style={{ margin: 0, borderLeft: `6px solid var(--${feeling ? "orange" : "cyan"}-400)` }}>
                  <div className="nm-card-body">
                    <p style={{ fontSize: 14, color: "var(--text-secondary)", marginBottom: 8 }}>{r.data.input.product_text}</p>
                    <span className="nm-badge" style={{
                      background: feeling ? "var(--orange-50)" : "var(--cyan-50)",
                      color: feeling ? "var(--orange-600)" : "var(--cyan-800)",
                      border: `1px solid ${feeling ? "var(--orange-100)" : "var(--cyan-100)"}`,
                      marginBottom: 10,
                    }}>
                      {feeling ? "Bought on feeling" : "Bought after comparing"} ({(r.data.classification.confidence * 100).toFixed(0)}% sure)
                    </span>
                    <p className="copy-text" style={{ fontSize: 16 }}>{r.data.agent_output.recommended_copy}</p>
                    <CopyButton text={r.data.agent_output.recommended_copy} />
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
