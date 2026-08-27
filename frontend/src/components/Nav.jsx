import { useEffect, useState } from "react";
import { API_BASE } from "../api.js";

const TABS = [
  { id: "component1", label: "Component 1 · Dual-System" },
  { id: "component3", label: "Component 3 · Scarcity" },
  { id: "component24", label: "Component 2+4 · Emotion + Loss" },
  { id: "pipeline", label: "Full Pipeline" },
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
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`nm-tab ${active === t.id ? "active" : ""}`}
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
