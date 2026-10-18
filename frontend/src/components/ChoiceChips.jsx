// A row of tappable pills that behaves like a set of radio buttons.
// Easier than a dropdown: every option is visible at once, targets are
// large, and it works the same with mouse, touch and keyboard.
export default function ChoiceChips({ options, value, onChange, label, labelledBy }) {
  const items = options.map((o) => (typeof o === "string" ? { value: o, label: o } : o));

  const onKeyDown = (e, i) => {
    const next = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
    if (!next) return;
    e.preventDefault();
    const j = (i + next + items.length) % items.length;
    onChange(items[j].value);
    const group = e.currentTarget.parentElement;
    group?.children[j]?.focus();
  };

  return (
    <div className="chip-row" role="radiogroup" aria-label={label} aria-labelledby={labelledBy}>
      {items.map((o, i) => {
        const selected = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={selected}
            tabIndex={selected || (!items.some((x) => x.value === value) && i === 0) ? 0 : -1}
            className="choice-chip"
            onClick={() => onChange(o.value)}
            onKeyDown={(e) => onKeyDown(e, i)}
          >
            {o.emoji && <span className="chip-emoji" aria-hidden="true">{o.emoji}</span>}
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
