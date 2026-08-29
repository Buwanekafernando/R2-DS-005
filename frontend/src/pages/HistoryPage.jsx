import { useEffect, useState } from "react";
import { getHistory, deleteFromHistory, clearHistory } from "../history.js";
import { downloadStrategy } from "../exportStrategy.js";
import Component1Result from "../components/Component1Result.jsx";
import Component3Result from "../components/Component3Result.jsx";
import Component24Result from "../components/Component24Result.jsx";
import FinalRecommendationCard from "../components/FinalRecommendationCard.jsx";

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  const remove = (id) => {
    deleteFromHistory(id);
    setHistory(getHistory());
    if (openId === id) setOpenId(null);
  };

  const removeAll = () => {
    clearHistory();
    setHistory([]);
    setOpenId(null);
  };

  const opened = history.find((h) => h.id === openId);

  return (
    <div className="max-w-[1000px] mx-auto px-10 py-8">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
        <div>
          <h1 className="font-display" style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-1px", marginBottom: 6 }}>
            Your Strategy History
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, maxWidth: 560 }}>
            Every strategy you generate on the Main Application page is saved here automatically
            (up to the most recent 25), so you can come back to it later. This is stored only on
            this device/browser — clearing your browser data will remove it.
          </p>
        </div>
        {history.length > 0 && (
          <button
            onClick={removeAll}
            style={{ fontSize: 12, color: "var(--coral-600)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline", whiteSpace: "nowrap" }}
          >
            Clear all history
          </button>
        )}
      </div>

      {history.length === 0 && (
        <div className="nm-card">
          <div className="nm-card-body">
            <div className="empty-state">
              <div className="empty-title">No saved strategies yet</div>
              <div className="empty-desc">Generate a strategy on the Main Application page and it'll show up here.</div>
            </div>
          </div>
        </div>
      )}

      {history.length > 0 && !opened && (
        <div className="space-y-2">
          {history.map((entry) => (
            <div key={entry.id} className="nm-card" style={{ margin: 0 }}>
              <div className="nm-card-body" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 20px" }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14 }}>{entry.productName}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{new Date(entry.savedAt).toLocaleString()}</div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button className="nm-btn-ghost" style={{ width: "auto", padding: "8px 14px" }} onClick={() => setOpenId(entry.id)}>View</button>
                  <button
                    onClick={() => remove(entry.id)}
                    style={{ fontSize: 12, color: "var(--coral-600)", background: "none", border: "none", cursor: "pointer" }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {opened && (
        <div>
          <button className="nm-btn-secondary" style={{ width: "auto", padding: "8px 16px", marginBottom: 16 }} onClick={() => setOpenId(null)}>
            ← Back to history
          </button>
          <div className="nm-card">
            <div className="nm-card-header">
              <span className="nm-card-title">{opened.productName}</span>
              <button className="nm-btn-secondary" style={{ width: "auto", padding: "6px 14px", fontSize: 12 }} onClick={() => downloadStrategy(opened.result)}>
                ⬇ Download as text
              </button>
            </div>
          </div>
          {opened.result.component1_full && <Component1Result result={opened.result.component1_full} showJson={false} />}
          {opened.result.component3 && <Component3Result data={opened.result.component3} rawData={opened.result.component3} showJson={false} />}
          {opened.result.component24 && <Component24Result result={opened.result.component24} showJson={false} />}
          {opened.result.final_recommendation && <FinalRecommendationCard rec={opened.result.final_recommendation} />}
        </div>
      )}
    </div>
  );
}
