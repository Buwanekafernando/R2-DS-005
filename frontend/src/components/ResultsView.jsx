import { useState } from "react";
import FinalRecommendationCard from "./FinalRecommendationCard.jsx";
import StrategySummaryCard from "./StrategySummaryCard.jsx";
import MoreVersionsCard from "./MoreVersionsCard.jsx";
import VisualGuide from "./VisualGuide.jsx";
import Component1Result from "./Component1Result.jsx";
import Component3Result from "./Component3Result.jsx";
import Component24Result from "./Component24Result.jsx";
import ResultCode from "./ResultCode.jsx";
import { AGENTS, agentColors } from "../constants.js";
import { downloadStrategy } from "../exportStrategy.js";
import { G } from "./Term.jsx";

// One results layout, shared by the Create page and History, so a saved
// strategy looks exactly like it did when it was first made.
//
// Order: the answer first (one message to copy), then the reasons in plain
// words, then other versions, then picture ideas. Each agent's full working
// sits behind "How we built this" for anyone who wants the detail.
export default function ResultsView({ result, productText, category, onEdit, onStartOver, celebrate = false }) {
  const [showWorking, setShowWorking] = useState(false);
  const rec = result.final_recommendation;
  const c24 = result.component24;
  const visuals = rec?.visual_suggestions || c24?.visual_suggestions;
  const emotion = rec?.target_emotion || c24?.target_emotion;
  const input = result.component1_full?.input || {};

  return (
    <div>
      <div className="results-layout">
      <div className="results-main">
      <FinalRecommendationCard rec={rec} productName={result.product} celebrate={celebrate} />

      {!rec?.recommendation && (
        <div className="check-pill tone-info" style={{ display: "block", marginBottom: 16 }}>
          This saved result was made before the combined message existed. Use one of the versions below.
        </div>
      )}

      <div className="notice" role="note">
        <div className="notice-text">
          <b>Check before you post.</b> This was written by AI, so make sure any facts, numbers or
          claims match your real product.
          <div style={{ color: "var(--teal-600)", marginTop: 4 }}>✓ Saved to your History automatically.</div>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button className="nm-btn-secondary" style={{ width: "auto" }} onClick={() => downloadStrategy(result)}>
            Download everything
          </button>
          {onEdit && <button className="nm-btn-secondary" style={{ width: "auto" }} onClick={onEdit}>Change answers</button>}
          {onStartOver && <button className="nm-btn-secondary" style={{ width: "auto" }} onClick={onStartOver}>New message</button>}
        </div>
      </div>

      <h2 className="section-heading"><span className="dot" aria-hidden="true" />Other versions you can use</h2>
      <p className="section-sub"><G>The final message above blends these. Each one also works on its own.</G></p>
      <MoreVersionsCard result={result} />
      </div>

      <aside className="results-side" aria-label="What we found">
      <h2 className="section-heading"><span className="dot" aria-hidden="true" />At a glance</h2>
      <p className="section-sub"><G>What the four AI helpers found out about your product.</G></p>
      <StrategySummaryCard result={result} />

      {visuals && (
        <>
          <h2 className="section-heading"><span className="dot" aria-hidden="true" />Picture and colour ideas</h2>
          <p className="section-sub"><G>For the photo or design that goes with your message.</G></p>
          <VisualGuide suggestions={visuals} emotion={emotion} />
        </>
      )}
      </aside>
      </div>

      <button
        type="button"
        className="built-toggle"
        aria-expanded={showWorking}
        aria-controls="how-built"
        onClick={() => setShowWorking((v) => !v)}
      >
        <span>
          <span className="built-toggle-title">How we built this</span>
          <span className="built-toggle-sub" style={{ display: "block" }}>
            See each AI helper's full results, scores and the raw data.
          </span>
        </span>
        <span className="built-toggle-cta">{showWorking ? "Hide details ▴" : "Show details ▾"}</span>
      </button>

      {showWorking && (
        <div id="how-built" style={{ marginTop: 16 }}>
          <div className="agent-chain" aria-label="Order the AI helpers ran in">
            {[AGENTS.decide, AGENTS.urgency, AGENTS.feeling, AGENTS.missout].map((a, i) => (
              <span key={a.research} style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                {i > 0 && <span aria-hidden="true">→</span>}
                <span className="agent" style={{ background: agentColors(a.color).bg, borderColor: agentColors(a.color).border, color: agentColors(a.color).ink }}>
                  {a.emoji} {a.feature}
                </span>
              </span>
            ))}
            <span aria-hidden="true">→</span>
            <span className="agent" style={{ background: "var(--purple-50)", borderColor: "var(--purple-100)", color: "var(--purple-800)" }}>✨ Final blend</span>
          </div>

          <AgentHeading agent={AGENTS.decide} />
          {result.component1_full && (
            <Component1Result
              result={result.component1_full}
              showJson={false}
              productText={productText || input.product_text}
              category={category || input.category}
            />
          )}

          <AgentHeading agent={AGENTS.urgency} />
          {result.component3 && <Component3Result data={result.component3} rawData={result.component3} showJson={false} />}

          <AgentHeading agent={AGENTS.feeling} extra={AGENTS.missout} />
          {c24 && <Component24Result result={c24} showJson={false} />}

          <div style={{ marginTop: 16 }}>
            <ResultCode title="Raw data (JSON) for the full result" data={result} />
          </div>
        </div>
      )}
    </div>
  );
}

function AgentHeading({ agent, extra }) {
  return (
    <h3 style={{ display: "flex", alignItems: "center", gap: 10, margin: "26px 0 10px", fontFamily: "Plus Jakarta Sans, sans-serif", fontWeight: 700, fontSize: 19 }}>
      <span aria-hidden="true">{agent.emoji}</span>
      {extra ? `${agent.name} and ${extra.name.toLowerCase()}` : agent.name}
      <span style={{ fontFamily: "Plus Jakarta Sans, sans-serif", fontWeight: 500, fontSize: 14, color: "var(--text-secondary)" }}>
        {extra ? `${agent.component} & ${extra.component.replace("Component ", "")}: ${agent.research} + ${extra.research}` : `${agent.component}: ${agent.research}`}
      </span>
    </h3>
  );
}
