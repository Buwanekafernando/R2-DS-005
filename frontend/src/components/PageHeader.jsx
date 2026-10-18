// Consistent page title + one-line explanation, used on every page so the
// app feels like one product instead of separate tools.
import { G } from "./Term.jsx";

export default function PageHeader({ title, intro, aside, children }) {
  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
      <div style={{ flex: "1 1 420px" }}>
        <h1 className="page-title">{title}</h1>
        {intro && <p className="page-intro"><G>{intro}</G></p>}
        {children}
      </div>
      {aside && <div style={{ flexShrink: 0 }}>{aside}</div>}
    </header>
  );
}
