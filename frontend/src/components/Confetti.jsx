import { useEffect, useMemo, useState } from "react";

// A one-second burst of colour when the message is ready — in the four
// helpers' colours. Not shown at all if the person has turned off
// animations on their device.
const COLORS = ["#22D3EE", "#8B5CF6", "#FFD43B", "#FF8A3D", "#10B981"];

export default function Confetti({ pieces = 26 }) {
  const reduced = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const [show, setShow] = useState(!reduced);

  useEffect(() => {
    if (!show) return;
    const id = setTimeout(() => setShow(false), 1500);
    return () => clearTimeout(id);
  }, [show]);

  const bits = useMemo(() => Array.from({ length: pieces }, (_, i) => ({
    left: `${8 + Math.random() * 84}%`,
    dx: `${(Math.random() - 0.5) * 220}px`,
    dy: `${70 + Math.random() * 190}px`,
    rot: `${(Math.random() - 0.5) * 720}deg`,
    color: COLORS[i % COLORS.length],
    delay: `${Math.random() * 0.15}s`,
  })), [pieces]);

  if (!show) return null;
  return (
    <span className="confetti" aria-hidden="true">
      {bits.map((b, i) => (
        <i key={i} style={{ left: b.left, background: b.color, animationDelay: b.delay, "--dx": b.dx, "--dy": b.dy, "--rot": b.rot }} />
      ))}
    </span>
  );
}
