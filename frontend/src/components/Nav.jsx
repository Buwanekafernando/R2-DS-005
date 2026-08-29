import { useEffect, useState } from "react";
import { API_BASE } from "../api.js";

const PRIMARY_TABS = [
  { id: "home", label: "Home" },
  { id: "pipeline", label: "Main Application" },
];
const ADVANCED_TABS = [
  { id: "component1", label: "Component 1" },
  { id: "component3", label: "Component 3" },
  { id: "component24", label: "Component 2+4" },
];

export default function Nav({ active, onChange }) {
  const [apiOnline, setApiOnline] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/health`)
      .then((r) => r.ok)
      .then((ok) => !cancelled && setApiOnline(ok))
      .catch(() => !cancelled && setApiOnline(false));
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="nm-nav">
      <div className="nm-logo">
        <span className="nm-logo-dot" />
        NeuroMark AI
        <span className="nm-badge" style={{ background: "var(--purple-50)", color: "var(--purple-800)", border: "1px solid var(--purple-100)" }}>
          4-Agent System
        </span>
      </div>

      <div className="nm-tabs">
        {PRIMARY_TABS.map((t) => (
          <button
            key={t.id}
            className={`nm-tab ${active === t.id ? "active" : ""}`}
            onClick={() => onChange(t.id)}
          >
            {t.label}
          </button>
        ))}
        <span style={{ width: 1, background: "var(--border)", margin: "0 8px", alignSelf: "stretch" }} />
        {ADVANCED_TABS.map((t) => (
          <button
            key={t.id}
            className={`nm-tab ${active === t.id ? "active" : ""}`}
            style={{ fontSize: 12, opacity: 0.75 }}
            onClick={() => onChange(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <span className={`api-pill ${apiOnline ? "online" : "offline"}`}>
        {apiOnline === null ? "Checking API…" : apiOnline ? "API Online" : "API Offline"}
      </span>
    </div>
  );
}
