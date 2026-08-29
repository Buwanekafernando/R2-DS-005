import { useState } from "react";

// Small "?" icon that shows a plain-language explanation on hover/tap,
// right next to the confusing term — so the person doesn't have to leave
// the page and go find the Home page glossary to understand a metric.
export default function Tooltip({ text }) {
  const [open, setOpen] = useState(false);

  return (
    <span
      style={{ position: "relative", display: "inline-block", marginLeft: 5 }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <span
        onClick={() => setOpen((v) => !v)}
        style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: 14, height: 14, borderRadius: "50%",
          background: "var(--border)", color: "var(--text-secondary)",
          fontSize: 10, fontWeight: 700, cursor: "pointer",
          verticalAlign: "middle", lineHeight: 1,
        }}
      >
        ?
      </span>
      {open && (
        <span
          style={{
            position: "absolute", zIndex: 50, bottom: "130%", left: "50%",
            transform: "translateX(-50%)", width: 220,
            background: "var(--text-primary)", color: "var(--surface)",
            fontSize: 11, fontWeight: 400, lineHeight: 1.5,
            padding: "8px 10px", borderRadius: "var(--radius-sm)",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
          }}
        >
          {text}
        </span>
      )}
    </span>
  );
}
