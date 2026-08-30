import { useEffect, useState } from "react";
import { API_BASE } from "../api.js";
import { FEATURE_NAMES } from "../constants.js";

const PRIMARY_TABS = [
  { id: "home", label: "Home" },
  { id: "pipeline", label: "Main Application" },
  { id: "batch", label: "Batch Mode" },
  { id: "history", label: "History" },
];
const ADVANCED_TABS = [
  { id: "component1", label: FEATURE_NAMES.component1 },
  { id: "component3", label: FEATURE_NAMES.component3 },
  { id: "component24", label: FEATURE_NAMES.component24 },
];

export default function Nav({ active, onChange }) {
  const [apiOnline, setApiOnline] = useState(null);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/health`)
      .then((r) => r.ok)
      .then((ok) => !cancelled && setApiOnline(ok))
      .catch(() => !cancelled && setApiOnline(false));
    return () => { cancelled = true; };
  }, []);

  const isAdvancedActive = ADVANCED_TABS.some((t) => t.id === active);

  return (
    <div className="nm-nav">
      <div className="nm-logo">
        <span className="nm-logo-dot" />
        NeuroMark AI
        <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
          AI Marketing Toolkit
        </span>
      </div>

      <div className="nm-tabs" style={{ position: "relative" }}>
        {PRIMARY_TABS.map((t) => (
          <button
            key={t.id}
            className={`nm-tab ${active === t.id ? "active" : ""}`}
            onClick={() => onChange(t.id)}
          >
            {t.label}
          </button>
        ))}

        {/* Advanced/testing pages — tucked away, not part of the main flow */}
        <button
          className={`nm-tab ${isAdvancedActive ? "active" : ""}`}
          style={{ fontSize: 12, opacity: 0.75 }}
          onClick={() => setAdvancedOpen((v) => !v)}
        >
          Advanced {advancedOpen ? "▲" : "▾"}
        </button>

        {advancedOpen && (
          <div style={{
            position: "absolute", top: "calc(100% + 6px)", right: 0, zIndex: 50,
            background: "var(--surface)", border: "1px solid var(--border)",
            borderRadius: "var(--radius-md)", boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            padding: 6, minWidth: 220,
          }}>
            <div style={{ fontSize: 10, color: "var(--text-muted)", padding: "6px 10px 4px", textTransform: "uppercase", letterSpacing: ".05em" }}>
              Test one agent at a time
            </div>
            {ADVANCED_TABS.map((t) => (
              <button
                key={t.id}
                className={`nm-tab ${active === t.id ? "active" : ""}`}
                style={{ display: "block", width: "100%", textAlign: "left", fontSize: 13 }}
                onClick={() => { onChange(t.id); setAdvancedOpen(false); }}
              >
                {t.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <span className={`api-pill ${apiOnline ? "online" : "offline"}`}>
        {apiOnline === null ? "Checking API…" : apiOnline ? "API Online" : "API Offline"}
      </span>
    </div>
  );
}
