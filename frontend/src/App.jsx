import { useEffect, useState } from "react";
import Nav from "./components/Nav.jsx";
import ErrorBoundary from "./ErrorBoundary.jsx";
import HomePage from "./pages/HomePage.jsx";
import Component1Page from "./pages/Component1Page.jsx";
import Component3Page from "./pages/Component3Page.jsx";
import Component24Page from "./pages/Component24Page.jsx";
import FullPipelinePage from "./pages/FullPipelinePage.jsx";
import BatchPage from "./pages/BatchPage.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import { usePersistedState } from "./usePersistedState.js";
import { useTheme } from "./useTheme.js";

export default function App() {
  const [tab, setTab] = useState("home");
  const [theme, toggleTheme] = useTheme();

  // "Bigger text" — scales the whole interface for people who find the
  // default size hard to read. Remembered on this browser.
  const [bigText, setBigText] = usePersistedState("nm_big_text", false);

  // When someone clicks "Try an example" on the Home page, the Create page
  // opens with that example already filled in.
  const [pendingExample, setPendingExample] = useState(null);

  // Component 1's last result is shared across pages so Components 2/3/4
  // can build on its recommended_copy, matching the backend orchestrator.
  const [c1Result, setC1Result] = useState(null);
  const baseCopy = c1Result?.agent_output?.recommended_copy || null;

  const go = (id) => setTab(id);
  useEffect(() => { window.scrollTo(0, 0); }, [tab]);

  return (
    <div className="app-shell" style={{ zoom: bigText ? 1.15 : 1 }}>
      <a
        href="#main"
        className="sr-only focus:not-sr-only"
        style={{ position: "absolute", left: 8, top: 8, zIndex: 100, background: "var(--surface)", padding: "8px 12px", borderRadius: 8 }}
      >
        Skip to main content
      </a>
      <Nav active={tab} onChange={go} bigText={bigText} onToggleBigText={() => setBigText((v) => !v)} theme={theme} onToggleTheme={toggleTheme} />

      <main id="main">
        <ErrorBoundary key={tab}>
          {tab === "home" && (
            <HomePage
              onGetStarted={() => go("pipeline")}
              onTryExample={(id) => { setPendingExample(id); go("pipeline"); }}
            />
          )}
          {tab === "pipeline" && (
            <FullPipelinePage startExample={pendingExample} onExampleUsed={() => setPendingExample(null)} />
          )}
          {tab === "batch" && <BatchPage />}
          {tab === "history" && <HistoryPage onCreate={() => go("pipeline")} />}
          {tab === "component1" && <Component1Page onResult={setC1Result} />}
          {tab === "component3" && <Component3Page baseCopy={baseCopy} />}
          {tab === "component24" && <Component24Page baseCopy={baseCopy} />}
        </ErrorBoundary>
      </main>
    </div>
  );
}
