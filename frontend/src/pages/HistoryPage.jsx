import { useEffect, useMemo, useRef, useState } from "react";
import { getHistory, deleteFromHistory, clearHistory } from "../history.js";
import PageHeader from "../components/PageHeader.jsx";
import ResultsView from "../components/ResultsView.jsx";
import { emotionEmoji, emotionColors, CATEGORY_ICONS, categoryLabel } from "../constants.js";
import { G } from "../components/Term.jsx";

function friendlyDate(iso) {
  const d = new Date(iso);
  const now = new Date();
  const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  const sameDay = (a, b) => a.toDateString() === b.toDateString();
  const yesterday = new Date(now); yesterday.setDate(now.getDate() - 1);
  if (sameDay(d, now)) return `Today, ${time}`;
  if (sameDay(d, yesterday)) return `Yesterday, ${time}`;
  return `${d.toLocaleDateString([], { day: "numeric", month: "short", year: "numeric" })}, ${time}`;
}

export default function HistoryPage({ onCreate }) {
  const [history, setHistory] = useState([]);
  const [openId, setOpenId] = useState(null);
  const [query, setQuery] = useState("");
  const topRef = useRef(null);

  useEffect(() => { setHistory(getHistory()); }, []);
  useEffect(() => { window.scrollTo({ top: 0 }); topRef.current?.focus({ preventScroll: true }); }, [openId]);

  const remove = (entry) => {
    if (!window.confirm(`Delete the saved message for "${entry.productName}"? This can't be undone.`)) return;
    deleteFromHistory(entry.id);
    setHistory(getHistory());
    if (openId === entry.id) setOpenId(null);
  };

  const removeAll = () => {
    if (!window.confirm("Delete all saved messages on this device? This can't be undone.")) return;
    clearHistory();
    setHistory([]);
    setOpenId(null);
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? history.filter((h) => h.productName.toLowerCase().includes(q)) : history;
  }, [history, query]);

  const opened = history.find((h) => h.id === openId);

  if (opened) {
    return (
      <div className="page" style={{ maxWidth: 920 }}>
        <button className="nm-btn-secondary" style={{ width: "auto", marginBottom: 18 }} onClick={() => setOpenId(null)}>
          ← Back to History
        </button>
        <p ref={topRef} tabIndex={-1} style={{ fontSize: 15, color: "var(--text-secondary)", marginBottom: 12, outline: "none" }}>
          Saved {friendlyDate(opened.savedAt)}
        </p>
        <ResultsView result={opened.result} />
      </div>
    );
  }

  return (
    <div className="page">
      <PageHeader
        title="Your saved messages"
        intro="Every message you create is saved here automatically, up to the latest 25. They're stored only in this browser on this device."
        aside={history.length > 0 && <button className="link-btn danger" onClick={removeAll}>Delete all</button>}
      />
      <span ref={topRef} tabIndex={-1} />

      {history.length === 0 && (
        <div className="nm-card">
          <div className="nm-card-body empty-state">
            <div className="empty-icon" style={{ background: "var(--violet-50)", border: "1px solid var(--violet-100)" }} aria-hidden="true">🗂️</div>
            <div className="empty-title">Nothing saved yet</div>
            <div className="empty-desc" style={{ marginBottom: 18 }}><G>Messages you create will appear here, so you can copy them again later.</G></div>
            <button className="nm-btn-primary" style={{ width: "auto", padding: "12px 26px" }} onClick={onCreate}>Create a message</button>
          </div>
        </div>
      )}

      {history.length > 3 && (
        <div style={{ marginBottom: 14, maxWidth: 420 }}>
          <label className="field-label" htmlFor="h-search">Search by product name</label>
          <input id="h-search" className="nm-input" type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g. lipstick" />
        </div>
      )}

      {history.length > 0 && filtered.length === 0 && (
        <p style={{ fontSize: 16, color: "var(--text-secondary)" }}>No saved messages match "{query}".</p>
      )}

      <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 10 }}>
        {filtered.map((entry) => {
          const r = entry.result || {};
          const emotion = r.final_recommendation?.target_emotion || r.component24?.target_emotion;
          const category = r.component1_full?.input?.category;
          const preview = r.final_recommendation?.recommendation || r.component24?.emotion_copy || r.component3?.final_copy || "";
          return (
            <li key={entry.id} className="nm-card" style={{ margin: 0 }}>
              <div className="nm-card-body" style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                <div style={{ flex: "1 1 360px", minWidth: 0 }}>
                  <h2 style={{ fontWeight: 700, fontSize: 18, marginBottom: 4 }}>{entry.productName}</h2>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", fontSize: 14, color: "var(--text-secondary)", marginBottom: 6 }}>
                    <span>{friendlyDate(entry.savedAt)}</span>
                    {category && (
                      <span className="nm-badge" style={{ background: "var(--surface-alt)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                        {CATEGORY_ICONS[category] || ""} {categoryLabel(category)}
                      </span>
                    )}
                    {emotion && (
                      <span className="nm-badge" style={{ background: emotionColors(emotion).bg, border: `1px solid ${emotionColors(emotion).ring}`, color: emotionColors(emotion).text, textTransform: "capitalize" }}>
                        {emotionEmoji(emotion)} {emotion}
                      </span>
                    )}
                  </div>
                  {preview && (
                    <p style={{ fontSize: 15, color: "var(--text-secondary)", lineHeight: 1.5, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                      {preview}
                    </p>
                  )}
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <button className="nm-btn-primary" style={{ width: "auto", padding: "10px 22px", minHeight: 46 }} onClick={() => setOpenId(entry.id)}>
                    Open
                  </button>
                  <button className="link-btn danger" onClick={() => remove(entry)} aria-label={`Delete ${entry.productName}`}>
                    Delete
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
