import { useState } from "react";

// Collapsed by default — a business user never has to see this unless they
// choose to. Developers/panel reviewers can expand it to see the exact
// model output backing the plain-language cards above it.
export default function ResultCode({ title = "Result Code (JSON)", data }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="nm-card">
      <div className="nm-card-header" style={{ cursor: "pointer" }} onClick={() => setOpen(!open)}>
        <span className="nm-card-title">{title}</span>
        <span className="nm-badge" style={{ background: "var(--bg)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
          {open ? "Hide raw output ▲" : "Show raw output ▼"}
        </span>
      </div>
      {open && (
        <div className="nm-card-body">
          <pre className="nm-json">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
