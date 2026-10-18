import { useCallback, useEffect, useId, useRef, useState } from "react";
import { TERM_REGEX, tipFor } from "../glossary.js";

// A technical word with a plain-language explanation.
// Hover it with a mouse, press Tab to focus it, or tap it on a phone.
// Esc or tapping elsewhere closes it. The bubble keeps itself inside the
// screen, flipping below the word if there is no room above.
export function Term({ children, tip, label }) {
  const text = tip || tipFor(children);
  const id = useId();
  const ref = useRef(null);
  const [open, setOpen] = useState(false);
  const [place, setPlace] = useState({ shift: 0, below: false });

  const measure = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const half = 150;                       // half of the 300px bubble
    const center = r.left + r.width / 2;
    const margin = 12;
    let shift = 0;
    if (center - half < margin) shift = margin - (center - half);
    else if (center + half > window.innerWidth - margin) shift = window.innerWidth - margin - (center + half);
    setPlace({ shift, below: r.top < 150 });
  }, []);

  useEffect(() => {
    if (!open) return;
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    const esc = (e) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", close); document.removeEventListener("keydown", esc); };
  }, [open]);

  if (!text) return <>{children}</>;

  const show = () => { measure(); setOpen(true); };
  return (
    <span
      ref={ref}
      className={`term ${open ? "open" : ""}`}
      tabIndex={0}
      role="button"
      aria-label={label ? `${label}. Explanation available` : undefined}
      aria-describedby={id}
      onMouseEnter={show}
      onMouseLeave={() => setOpen(false)}
      onFocus={show}
      onBlur={() => setOpen(false)}
      onClick={() => (open ? setOpen(false) : show())}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open ? setOpen(false) : show(); } }}
    >
      {children}
      <span
        id={id}
        role="tooltip"
        className={`tip-bubble ${place.below ? "below" : ""}`}
        style={{ "--tip-shift": `${place.shift}px` }}
      >
        {text}
      </span>
    </span>
  );
}

// <G>Plain string</G> — finds every glossary word in the string and turns the
// first occurrence of each into a <Term>. Use it for any text that may hold
// technical words, instead of wrapping each word by hand.
export function G({ children }) {
  if (typeof children !== "string") return <>{children}</>;
  const parts = [];
  const seen = new Set();
  let last = 0;
  let m;
  const re = new RegExp(TERM_REGEX.source, "gi");
  while ((m = re.exec(children))) {
    const key = m[0].toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    if (m.index > last) parts.push(children.slice(last, m.index));
    parts.push(<Term key={`${m.index}-${key}`}>{m[0]}</Term>);
    last = m.index + m[0].length;
  }
  if (!parts.length) return <>{children}</>;
  if (last < children.length) parts.push(children.slice(last));
  return <>{parts}</>;
}
