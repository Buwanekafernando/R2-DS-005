// Turns the emotion agent's visual suggestions into something you can see:
// real colour swatches for the palette, plus the photo and layout advice.
const COLOUR_WORDS = {
  "warm yellow": "#F6C343", "soft orange": "#F7A867", "deep blue": "#1E3A8A",
  "light grey": "#D9D9D9", "light gray": "#D9D9D9", "soft green": "#9BCB9B", "light blue": "#A8D4F2",
  red: "#D7263D", orange: "#F28C28", purple: "#7B3FA0", yellow: "#F5C518", blue: "#2F6FDE",
  pink: "#F29CB7", navy: "#1F2A5A", black: "#1A1916", gold: "#C9A227", teal: "#1C9C9C",
  grey: "#9A9A9A", gray: "#9A9A9A", green: "#3BA55C", white: "#FFFFFF", brown: "#8B5E3C",
};

function toSwatches(palette) {
  return String(palette || "")
    .split(",")
    .map((p) => p.trim())
    .filter(Boolean)
    .map((name) => ({ name, hex: COLOUR_WORDS[name.toLowerCase()] }))
    .filter((s) => s.hex);
}

export default function VisualGuide({ suggestions, emotion }) {
  if (!suggestions) return null;
  const swatches = toSwatches(suggestions.palette);

  return (
    <div className="nm-card">
      <div className="nm-card-body">
        <h3 className="result-section-title">Colours that suit {emotion ? `the feeling of ${emotion}` : "this message"}</h3>
        {swatches.length > 0 ? (
          <div className="swatches">
            {swatches.map((s) => (
              <span key={s.name} className="swatch"><i style={{ background: s.hex }} aria-hidden="true" />{s.name}</span>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: 15, marginBottom: 12 }}>{suggestions.palette}</p>
        )}
        <dl style={{ display: "grid", gap: 10 }}>
          {suggestions.image_style && (
            <div>
              <dt style={{ fontWeight: 700, fontSize: 15 }}>Photos to use</dt>
              <dd style={{ fontSize: 15, color: "var(--text-secondary)", margin: 0 }}>{suggestions.image_style}</dd>
            </div>
          )}
          {suggestions.layout_mood && (
            <div>
              <dt style={{ fontWeight: 700, fontSize: 15 }}>Overall look</dt>
              <dd style={{ fontSize: 15, color: "var(--text-secondary)", margin: 0 }}>{suggestions.layout_mood}</dd>
            </div>
          )}
        </dl>
      </div>
    </div>
  );
}
