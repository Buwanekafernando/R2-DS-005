import { useState } from "react";

export default function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <button
      onClick={handleCopy}
      style={{
        fontSize: 11, padding: "3px 10px",
        borderRadius: "var(--radius-sm)",
        border: "1px solid var(--border)",
        background: copied ? "var(--teal-50)" : "var(--surface)",
        color: copied ? "var(--teal-600)" : "var(--text-secondary)",
        cursor: "pointer", marginTop: 8,
        transition: "all .15s",
        fontFamily: "DM Sans, sans-serif",
      }}
    >
      {copied ? "✓ Copied!" : "Copy"}
    </button>
  );
}
