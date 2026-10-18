import { useCallback, useEffect, useId, useRef, useState } from "react";

// Small “?” button that explains something right next to it. Works with a
// mouse (hover), a finger (tap) and a keyboard (Tab, then Enter). Esc or
// tapping elsewhere closes it. Shares its look with <Term>.
export default function Tooltip({ text, label = "What does this mean?" }) {
  const id = useId();
  const ref = useRef(null);
  const [open, setOpen] = useState(false);
  const [place, setPlace] = useState({ shift: 0, below: false });

  const measure = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const half = 150, center = r.left + r.width / 2, margin = 12;
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

  return (
    <span
      ref={ref}
      className="tip-wrap"
      onMouseEnter={() => { measure(); setOpen(true); }}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        className="tip-btn"
        aria-label={label}
        aria-expanded={open}
        aria-describedby={open ? id : undefined}
        onFocus={() => { measure(); setOpen(true); }}
        onBlur={() => setOpen(false)}
        onClick={() => { measure(); setOpen((v) => !v); }}
      >
        ?
      </button>
      {open && (
        <span id={id} role="tooltip" className={`tip-bubble show ${place.below ? "below" : ""}`} style={{ "--tip-shift": `${place.shift}px` }}>
          {text}
        </span>
      )}
    </span>
  );
}
