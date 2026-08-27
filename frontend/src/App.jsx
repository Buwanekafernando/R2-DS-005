import { useState } from "react";
import Nav from "./components/Nav.jsx";
import Component1Page from "./pages/Component1Page.jsx";
import Component3Page from "./pages/Component3Page.jsx";
import Component24Page from "./pages/Component24Page.jsx";
import FullPipelinePage from "./pages/FullPipelinePage.jsx";

export default function App() {
  const [tab, setTab] = useState("component1");

  // Component 1's last result is shared across pages so Components 2/3/4
  // can build on its recommended_copy, matching the backend orchestrator.
  const [c1Result, setC1Result] = useState(null);
  const baseCopy = c1Result?.agent_output?.recommended_copy || null;
  const sourceProductName = c1Result ? undefined : undefined; // Component 1 has no product_name field itself

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Nav active={tab} onChange={setTab} />

      {tab === "component1" && <Component1Page onResult={setC1Result} />}
      {tab === "component3" && <Component3Page baseCopy={baseCopy} sourceProductName={sourceProductName} />}
      {tab === "component24" && <Component24Page baseCopy={baseCopy} sourceProductName={sourceProductName} />}
      {tab === "pipeline" && <FullPipelinePage />}
    </div>
  );
}
