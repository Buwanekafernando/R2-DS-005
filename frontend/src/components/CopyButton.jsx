import { useState } from "react";

// Copies text to the clipboard. Falls back to the older select-and-copy
// method if the Clipboard API is blocked (some browsers / non-https pages).
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch {
      return false;
    }
  }
}

// size="lg" is the big, obvious button used for the main message.
export default function CopyButton({ text, size = "sm", label = "Copy" }) {
  const [state, setState] = useState("idle"); // idle | copied | failed

  const handleCopy = async () => {
    const ok = await copyText(text || "");
    setState(ok ? "copied" : "failed");
    setTimeout(() => setState("idle"), 2200);
  };

  const big = size === "lg";
  const copied = state === "copied";

  return (
    <button
      type="button"
      onClick={handleCopy}
      aria-live="polite"
      className={big ? "nm-btn-primary" : undefined}
      style={big ? {
        width: "auto", padding: "12px 24px",
        background: copied ? "var(--teal-600)" : undefined,
      } : {
        fontSize: 14, fontWeight: 600, padding: "7px 14px", minHeight: 38,
        borderRadius: "var(--radius-sm)",
        border: `1.5px solid ${copied ? "var(--teal-100)" : "var(--border-strong)"}`,
        background: copied ? "var(--teal-50)" : "var(--surface)",
        color: copied ? "var(--teal-600)" : "var(--text-primary)",
        cursor: "pointer", marginTop: 8,
        transition: "background .15s, color .15s",
        fontFamily: "Plus Jakarta Sans, sans-serif",
      }}
    >
      {copied ? "✓ Copied" : state === "failed" ? "Couldn't copy, select the text instead" : label}
    </button>
  );
}
