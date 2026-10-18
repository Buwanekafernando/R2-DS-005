import { CATEGORY_EMOTION_MAP, EMOTIONS, EMOTION_INFO, categoryLabel, emotionColors } from "../constants.js";

// Big colourful cards instead of a dropdown of single words. Each feeling
// shows its emoji, a plain description, and its own colours (the same
// colours the AI later recommends for that feeling). Feelings that suit
// the chosen product type come first and are tagged "Good fit".
export default function EmotionPicker({ value, onChange, category }) {
  const recommended = CATEGORY_EMOTION_MAP[category] || [];
  const ordered = [...recommended, ...EMOTIONS.filter((e) => !recommended.includes(e))];

  const cards = [
    { value: "", emoji: "✨", name: "Let the AI choose", desc: `Picks a feeling that suits ${categoryLabel(category).toLowerCase()}`, colors: emotionColors("auto") },
    ...ordered.map((e) => ({ value: e, emoji: EMOTION_INFO[e]?.emoji, name: e, desc: EMOTION_INFO[e]?.desc, colors: emotionColors(e) })),
  ];

  const onKeyDown = (e, i) => {
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (!step) return;
    e.preventDefault();
    const j = (i + step + cards.length) % cards.length;
    onChange(cards[j].value);
    e.currentTarget.parentElement?.children[j]?.focus();
  };

  return (
    <div className="emotion-grid" role="radiogroup" aria-label="Feeling for your message">
      {cards.map((c, i) => {
        const selected = c.value === value;
        const rank = recommended.indexOf(c.value);
        return (
          <button
            key={c.value || "auto"}
            type="button"
            role="radio"
            aria-checked={selected}
            tabIndex={selected || (!cards.some((x) => x.value === value) && i === 0) ? 0 : -1}
            className="emotion-card"
            style={{ "--emo-bg": c.colors.bg, "--emo-ring": c.colors.ring, "--emo-text": c.colors.text }}
            onClick={() => onChange(c.value)}
            onKeyDown={(e) => onKeyDown(e, i)}
          >
            <span className="emo" aria-hidden="true">{c.emoji}</span>
            <span className="emo-name" style={c.value ? undefined : { textTransform: "none" }}>{c.name}</span>
            <span className="emo-desc" style={{ display: "block" }}>{c.desc}</span>
            {selected ? (
              <span className="emo-check" aria-hidden="true">✓</span>
            ) : rank >= 0 ? (
              <span className="emo-tag">Good fit</span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
