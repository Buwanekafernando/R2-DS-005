import { useEffect, useRef, useState } from "react";
import { API_BASE } from "../api.js";
import { AGENTS } from "../constants.js";

const PRIMARY_TABS = [
  { id: "home", label: "Home" },
  { id: "pipeline", label: "Create a message" },
  { id: "batch", label: "Many products" },
  { id: "history", label: "History" },
];

// Single-agent pages: for testing one AI helper on its own (and for the
// viva panel), kept out of the main flow so beginners aren't distracted.
const ADVANCED_TABS = [
  { id: "component1", agent: AGENTS.decide, label: "How they decide" },
  { id: "component3", agent: AGENTS.urgency, label: "Why act now" },
  { id: "component24", agent: AGENTS.feeling, label: "What they feel & would miss" },
];

export default function Nav({ active, onChange, bigText, onToggleBigText, theme, onToggleTheme }) {
  const [apiOnline, setApiOnline] = useState(null);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const menuRef = useRef(null);

  // Check the backend now, then every 20s, so the pill turns green on its
  // own once the server has finished loading its models.
  useEffect(() => {
    let cancelled = false;
    const check = () =>
      fetch(`${API_BASE}/health`)
        .then((r) => !cancelled && setApiOnline(r.ok))
        .catch(() => !cancelled && setApiOnline(false));
    check();
    const id = setInterval(check, 20000);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  // Close the "AI steps" menu on outside click or Escape
  useEffect(() => {
    if (!advancedOpen) return;
    const onClick = (e) => { if (e.target.closest && e.target.closest("[data-menu-zone]")) return; setAdvancedOpen(false); };
    const onKey = (e) => { if (e.key === "Escape") setAdvancedOpen(false); };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("mousedown", onClick); document.removeEventListener("keydown", onKey); };
  }, [advancedOpen]);

  const isAdvancedActive = ADVANCED_TABS.some((t) => t.id === active);

  return (
    <>
    <nav className="nm-nav" aria-label="Main">
      <button className="nm-logo" onClick={() => onChange("home")} aria-label="NeuroMark AI home">
        <span className="brand-mark" aria-hidden="true">N</span>
        NeuroMark AI
      </button>

      <div className="nm-tabs">
        {PRIMARY_TABS.map((t) => (
          <button
            key={t.id}
            className={`nm-tab ${active === t.id ? "active" : ""}`}
            aria-current={active === t.id ? "page" : undefined}
            onClick={() => onChange(t.id)}
          >
            {t.label}
          </button>
        ))}

        <div ref={menuRef} data-menu-zone style={{ position: "relative" }}>
          <button
            className={`nm-tab ${isAdvancedActive ? "active" : ""}`}
            aria-expanded={advancedOpen}
            aria-haspopup="true"
            onClick={() => setAdvancedOpen((v) => !v)}
          >
            One AI step {advancedOpen ? "▴" : "▾"}
          </button>

          {advancedOpen && (
            <div role="menu" className="nm-menu">
              <div style={{ fontSize: 14, color: "var(--text-secondary)", padding: "6px 10px 8px" }}>
                Try one AI helper on its own
              </div>
              {ADVANCED_TABS.map((t) => (
                <button
                  key={t.id}
                  role="menuitem"
                  className={`nm-tab ${active === t.id ? "active" : ""}`}
                  style={{ display: "flex", width: "100%", textAlign: "left", gap: 10, alignItems: "flex-start", borderRadius: 12, padding: "10px 12px" }}
                  onClick={() => { onChange(t.id); setAdvancedOpen(false); }}
                >
                  <span aria-hidden="true" style={{ fontSize: 18 }}>{t.agent.emoji}</span>
                  <span>
                    <span style={{ display: "block", fontWeight: 600 }}>{t.label}</span>
                    <span style={{ display: "block", fontSize: 13, opacity: 0.8 }}>{t.agent.feature}</span>
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="nav-tools">
        <button
          className="icon-btn theme-switch"
          onClick={onToggleTheme}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          <span className="glyph" aria-hidden="true">{theme === "dark" ? "☀️" : "🌙"}</span>
          <span className="long-label">{theme === "dark" ? "Light" : "Dark"}</span>
        </button>
        <button
          className="text-size-btn"
          aria-pressed={bigText}
          aria-label="Bigger text"
          onClick={onToggleBigText}
          title="Make all text on the page bigger"
        >
          <span aria-hidden="true">A</span><span aria-hidden="true" style={{ fontSize: "1.2em" }}>A</span>
          <span className="long-label" aria-hidden="true"> Bigger text</span>
        </button>
        <span
          className={`api-pill ${apiOnline === null ? "checking" : apiOnline ? "online" : "offline"}`}
          title={apiOnline === false ? "The AI server isn't responding. Start the backend, then wait a moment." : "The AI server is running"}
          role="status"
        >
          <span className="long-label">{apiOnline === null ? "Checking…" : apiOnline ? "System ready" : "System offline"}</span>
          <span className="short-label">{apiOnline === null ? "…" : apiOnline ? "Ready" : "Offline"}</span>
        </span>
      </div>
    </nav>

      <div className="nm-bottom" role="navigation" aria-label="Quick menu">
        {[
          { id: "home", g: "🏠", l: "Home" },
          { id: "pipeline", g: "✨", l: "Create" },
          { id: "batch", g: "📚", l: "Many" },
          { id: "history", g: "🕘", l: "History" },
        ].map((b) => (
          <button key={b.id} className={active === b.id ? "active" : ""} aria-current={active === b.id ? "page" : undefined} onClick={() => onChange(b.id)}>
            <span className="g" aria-hidden="true">{b.g}</span>{b.l}
          </button>
        ))}
        <button data-menu-zone className={isAdvancedActive ? "active" : ""} aria-expanded={advancedOpen} aria-haspopup="true" onClick={() => setAdvancedOpen((v) => !v)}>
          <span className="g" aria-hidden="true">🧪</span>One step
        </button>
      </div>
      {advancedOpen && (
        <div className="nm-menu nm-menu-phone" role="menu" data-menu-zone>
          <div style={{ fontSize: 14, color: "var(--text-secondary)", padding: "6px 10px 8px" }}>Try one AI helper on its own</div>
          {ADVANCED_TABS.map((t) => (
            <button key={t.id} role="menuitem" className={`nm-tab ${active === t.id ? "active" : ""}`}
              style={{ display: "flex", width: "100%", textAlign: "left", gap: 10, alignItems: "flex-start", borderRadius: 12, padding: "10px 12px" }}
              onClick={() => { onChange(t.id); setAdvancedOpen(false); }}>
              <span aria-hidden="true" style={{ fontSize: 18 }}>{t.agent.emoji}</span>
              <span><span style={{ display: "block", fontWeight: 600 }}>{t.label}</span><span style={{ display: "block", fontSize: 13, opacity: 0.85 }}>{t.agent.feature}</span></span>
            </button>
          ))}
        </div>
      )}
    </>
  );
}
