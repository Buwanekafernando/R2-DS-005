import { useEffect, useRef, useState } from "react";
import { apiPost } from "../api.js";
import PageHeader from "../components/PageHeader.jsx";
import ChoiceChips from "../components/ChoiceChips.jsx";
import EmotionPicker from "../components/EmotionPicker.jsx";
import RunProgress from "../components/RunProgress.jsx";
import ResultsView from "../components/ResultsView.jsx";
import Tooltip from "../components/Tooltip.jsx";
import Guide from "../components/Guide.jsx";
import {
  CATEGORIES, CATEGORY_ICONS, categoryLabel, defaultDemographics, defaultEmotionFor,
  EMOTION_INFO, EXAMPLES, validCategory,
  GENDER_OPTIONS, AGE_OPTIONS, DISTRICTS, OCCUPATION_OPTIONS, SPENDING_OPTIONS,
} from "../constants.js";
import { usePersistedState, clearPersisted } from "../usePersistedState.js";
import { saveToHistory } from "../history.js";
import { G } from "../components/Term.jsx";

const DEFAULT_FORM = {
  product_name: "",
  product_text: "",
  category: CATEGORIES[0],
  price: 0,
  target_audience: "",
  features: "",
  target_emotion: defaultEmotionFor(CATEGORIES[0]),
};

// Each step moves one stretch further along the colour spectrum, so the
// card visibly "warms up" as you get closer to your message.
const STEPS = [
  { n: 1, name: "Your product", heading: "Tell us about your product", emoji: "📦", color: "cyan", strip: "#22D3EE" },
  { n: 2, name: "Your customer", heading: "Who buys it?", emoji: "👥", color: "violet", strip: "#8B5CF6" },
  { n: 3, name: "The feeling", heading: "How should your message make people feel?", emoji: "💗", color: "yellow", strip: "#FFD43B" },
];

// Same 1–5 values the model was trained on (Hofstede scale), with words
// people actually use instead of a numbered survey label.
const CULTURE_SCALE = [
  { value: "1", label: "Not at all" },
  { value: "2", label: "A little" },
  { value: "3", label: "Somewhat" },
  { value: "4", label: "Quite a lot" },
  { value: "5", label: "Strongly" },
];

const MIN_WORDS = 8; // below this, Component 1's classification gets unreliable

export default function FullPipelinePage({ startExample, onExampleUsed }) {
  // Same storage keys as before, so anything already typed is kept.
  const [form, setForm] = usePersistedState("nm_pipeline_form", DEFAULT_FORM);
  const [demo, setDemo] = usePersistedState("nm_pipeline_demo", defaultDemographics());
  const [wasAutoFilled, setWasAutoFilled] = useState(true);
  const [step, setStep] = useState(1);
  const [maxStep, setMaxStep] = useState(1);
  const [showErrors, setShowErrors] = useState(false);
  const [loadedExample, setLoadedExample] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const headingRef = useRef(null);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });
  const setDemoField = (key) => (value) => setDemo({ ...demo, [key]: value });

  const wordCount = form.product_text.trim() ? form.product_text.trim().split(/\s+/).length : 0;
  const missing = {
    product_name: !form.product_name.trim(),
    product_text: !form.product_text.trim(),
  };

  // Move focus to the new step's heading so screen readers announce it,
  // and scroll back to the top so the person starts reading at the start.
  useEffect(() => {
    window.scrollTo({ top: 0 });
    headingRef.current?.focus({ preventScroll: true });
  }, [step, result]);

  const applyExample = (id) => {
    const ex = EXAMPLES.find((e) => e.id === id);
    if (!ex) return;
    setForm({ ...DEFAULT_FORM, ...ex.form });
    setDemo({ ...defaultDemographics(), ...ex.demo });
    setWasAutoFilled(false);
    setShowErrors(false);
    setLoadedExample(ex);
  };

  // Answers saved by an older version may use a product type that's no
  // longer offered; move them to a valid one so a type is always selected.
  useEffect(() => {
    if (validCategory(form.category) !== form.category) {
      const category = validCategory(form.category);
      setForm({ ...form, category, target_emotion: defaultEmotionFor(category) });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // "Try an example" on the Home page lands here
  useEffect(() => {
    if (startExample) { applyExample(startExample); onExampleUsed?.(); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startExample]);

  const chooseCategory = (category) => {
    // Auto-fill the feeling to match the product type, unless the person
    // has deliberately picked one already — don't overwrite their choice.
    const shouldAutoFill = !form.target_emotion || wasAutoFilled;
    setForm({ ...form, category, target_emotion: shouldAutoFill ? defaultEmotionFor(category) : form.target_emotion });
    if (shouldAutoFill) setWasAutoFilled(true);
  };

  const goTo = (n) => { setStep(n); setMaxStep((m) => Math.max(m, n)); };

  const next = () => {
    if (step === 1 && (missing.product_name || missing.product_text)) {
      setShowErrors(true);
      document.getElementById(missing.product_name ? "f-name" : "f-desc")?.focus();
      return;
    }
    setShowErrors(false);
    goTo(step + 1);
  };

  const clearForm = () => {
    setForm(DEFAULT_FORM);
    setDemo(defaultDemographics());
    setWasAutoFilled(true);
    setResult(null);
    setError("");
    setShowErrors(false);
    setLoadedExample(null);
    setStep(1);
    setMaxStep(1);
    clearPersisted("nm_pipeline_form");
    clearPersisted("nm_pipeline_demo");
  };

  const run = async () => {
    if (missing.product_name || missing.product_text) { setShowErrors(true); goTo(1); return; }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      // Exactly the same request the backend has always received.
      const data = await apiPost("/generate-strategy", {
        ...form,
        price: Number(form.price) || 0,
        target_emotion: form.target_emotion || null,
        demographics: demo,
      });
      setResult(data);
      saveToHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ── While the AI is working ──
  if (loading) {
    return (
      <div className="page">
        <RunProgress emotion={form.target_emotion} productName={form.product_name} />
      </div>
    );
  }

  // ── Results ──
  if (result) {
    return (
      <div className="page">
        <h1 className="sr-only" tabIndex={-1} ref={headingRef}>Your marketing message</h1>
        <ResultsView
          result={result}
          productText={form.product_text}
          category={form.category}
          onEdit={() => { setResult(null); setStep(3); }}
          onStartOver={clearForm}
          celebrate
        />
      </div>
    );
  }

  const current = STEPS[step - 1];

  return (
    <div className="page">
      <PageHeader
        title="Create your marketing message"
        intro="Answer three short sets of questions. Four AI helpers then write one message you can post straight away."
        aside={<button className="link-btn" onClick={clearForm}>Clear all answers</button>}
      />

      {/* Step progress */}
      <ol className="wizard-steps" aria-label="Progress">
        {STEPS.map((s) => {
          const state = s.n < step ? "done" : s.n === step ? "current" : "todo";
          const reachable = s.n <= maxStep && s.n !== step;
          return (
            <li key={s.n}>
              <button
                type="button"
                className={`wizard-step ${state} ${reachable ? "clickable" : ""}`}
                onClick={() => reachable && goTo(s.n)}
                disabled={!reachable}
                aria-current={state === "current" ? "step" : undefined}
                style={{ width: "100%", opacity: 1 }}
              >
                <span className="bar"><i style={{ transform: state === "todo" ? "scaleX(0)" : "scaleX(1)" }} /></span>
                <span className="step-name">
                  <span className="step-num">{state === "done" ? "✓" : s.n}</span>
                  <span className="step-label">{s.name}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>

      <div className="create-layout">
      <div>
      <div className="nm-card wizard-card" style={{ "--step-color": current.strip }}>
        <div className="nm-card-body" style={{ paddingTop: 30 }}>
          <span className="step-kicker" style={{ background: `var(--${current.color}-50)`, color: `var(--${current.color}-${current.color === "yellow" ? "600" : "800"})`, border: `1px solid var(--${current.color}-100)` }}>
            <span aria-hidden="true">{current.emoji}</span> Step {step} of 3
          </span>
          <h2 ref={headingRef} tabIndex={-1} className="step-heading">
            {current.heading}
          </h2>

          {step === 1 && (
            <>
              <div className="example-strip">
                <div className="example-strip-title">
                  {loadedExample ? `✨ Example loaded: ${loadedExample.label}. Change anything you like, then continue.` : "✨ Not sure what to write? Fill it in with an example:"}
                </div>
                <div className="chip-row">
                  {EXAMPLES.map((ex) => (
                    <button key={ex.id} type="button" className={`choice-chip ${loadedExample?.id === ex.id ? "selected" : ""}`} onClick={() => applyExample(ex.id)}>
                      <span className="chip-emoji" aria-hidden="true">{ex.emoji}</span>{ex.label}
                    </button>
                  ))}
                </div>
              </div>

              <label className="field-label" htmlFor="f-name">Product name</label>
              <input
                id="f-name" className="nm-input" value={form.product_name} onChange={update("product_name")}
                placeholder="e.g. Spa Ceylon Red Lipstick"
                aria-invalid={showErrors && missing.product_name}
                aria-describedby={showErrors && missing.product_name ? "e-name" : undefined}
              />
              {showErrors && missing.product_name && <FieldError id="e-name">Add your product's name to continue.</FieldError>}

              <span className="field-label" id="l-cat">What kind of product is it?</span>
              <ChoiceChips
                labelledBy="l-cat"
                value={form.category}
                onChange={chooseCategory}
                options={CATEGORIES.map((c) => ({ value: c, label: categoryLabel(c), emoji: CATEGORY_ICONS[c] }))}
              />

              <label className="field-label" htmlFor="f-desc">Describe your product</label>
              <p className="field-help" id="h-desc"><G>What it is, what it's made of and what makes it good. A sentence or two is enough.</G></p>
              <textarea
                id="f-desc" className="nm-textarea" rows={3} value={form.product_text} onChange={update("product_text")}
                placeholder="e.g. A colour-rich, long-lasting lipstick made with natural plant oils that keep lips soft all day."
                aria-invalid={showErrors && missing.product_text}
                aria-describedby="h-desc d-words"
              />
              <WordHint id="d-words" count={wordCount} />
              {showErrors && missing.product_text && <FieldError id="e-desc">Add a short description to continue.</FieldError>}

              <label className="field-label" htmlFor="f-price">Price</label>
              <p className="field-help" id="h-price"><G>Helps decide how much urgency suits it. Leave it at 0 if you're not sure.</G></p>
              <div className="input-prefix" style={{ maxWidth: 260 }}>
                <span aria-hidden="true">Rs.</span>
                <input id="f-price" className="nm-input" type="number" inputMode="decimal" min="0" step="0.01"
                  value={form.price} onChange={update("price")} aria-describedby="h-price" />
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <label className="field-label" htmlFor="f-aud">Who usually buys it? <span className="field-optional">optional</span></label>
              <p className="field-help" id="h-aud"><G>In your own words.</G></p>
              <input id="f-aud" className="nm-input" value={form.target_audience} onChange={update("target_audience")}
                placeholder="e.g. office workers, new mothers, students" aria-describedby="h-aud" />

              <div style={{ background: "var(--violet-50)", border: "1px solid var(--violet-100)", borderRadius: "var(--radius-md)", padding: "14px 16px", margin: "24px 0 4px", fontSize: 15, color: "var(--violet-800)", display: "flex", gap: 10 }}>
                <span aria-hidden="true" style={{ fontSize: 20 }}>💭</span>
                <span>Now picture one typical customer. These answers help the AI judge whether people buy
                your product on feeling or after comparing. Not sure? Keep the answers already selected.</span>
              </div>

              <span className="field-label" id="l-gender">Gender</span>
              <ChoiceChips labelledBy="l-gender" value={demo.gender} onChange={setDemoField("gender")} options={GENDER_OPTIONS} />

              <span className="field-label" id="l-age">Age</span>
              <ChoiceChips labelledBy="l-age" value={demo.age_range} onChange={setDemoField("age_range")}
                options={AGE_OPTIONS.map((a) => ({ value: a, label: a.replace(" years", "") }))} />

              <label className="field-label" htmlFor="f-district">Where they live</label>
              <select id="f-district" className="nm-select" style={{ maxWidth: 320 }} value={demo.district} onChange={(e) => setDemoField("district")(e.target.value)}>
                {DISTRICTS.map((o) => <option key={o}>{o}</option>)}
              </select>

              <span className="field-label" id="l-job">What they do</span>
              <ChoiceChips labelledBy="l-job" value={demo.occupation} onChange={setDemoField("occupation")} options={OCCUPATION_OPTIONS} />

              <span className="field-label" id="l-spend">How much they spend in a month</span>
              <ChoiceChips labelledBy="l-spend" value={demo.monthly_spending} onChange={setDemoField("monthly_spending")} options={SPENDING_OPTIONS} />

              <span className="field-label" id="l-culture">
                How much do family traditions and culture shape what they buy?
                <Tooltip text="Some shoppers follow family and cultural values closely when they buy; others don't. Based on a well-known research scale (Hofstede, 1980). 1 = not at all, 5 = strongly." />
              </span>
              <div className="scale" role="radiogroup" aria-labelledby="l-culture">
                {CULTURE_SCALE.map((o) => (
                  <button key={o.value} type="button" role="radio" aria-checked={demo.culture_influence === o.value}
                    onClick={() => setDemoField("culture_influence")(o.value)}>
                    <b>{o.value}</b>{o.label}
                  </button>
                ))}
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <p className="field-help" style={{ fontSize: 15, marginTop: -8, marginBottom: 14 }}>
                The feelings that suit {categoryLabel(form.category).toLowerCase()} are shown first.
              </p>
              <EmotionPicker
                value={form.target_emotion}
                category={form.category}
                onChange={(v) => { setForm({ ...form, target_emotion: v }); setWasAutoFilled(false); }}
              />

              <label className="field-label" htmlFor="f-feat" style={{ marginTop: 24 }}>
                What makes it special? <span className="field-optional">optional</span>
              </label>
              <p className="field-help" id="h-feat"><G>Two or three key features, separated by commas.</G></p>
              <input id="f-feat" className="nm-input" value={form.features} onChange={update("features")}
                placeholder="e.g. natural red shade, keeps lips soft" aria-describedby="h-feat" />

              <div className="review-box">
                <div style={{ fontWeight: 800, marginBottom: 6, color: "var(--violet-800)" }}>🚀 Ready to create</div>
                <dl>
                  <ReviewRow k="Product" v={form.product_name || "Not added yet"} />
                  <ReviewRow k="Type" v={`${CATEGORY_ICONS[form.category] || ""} ${categoryLabel(form.category)}`} />
                  {Number(form.price) > 0 && <ReviewRow k="Price" v={`Rs. ${Number(form.price).toLocaleString()}`} />}
                  <ReviewRow k="Customer" v={`${demo.gender}, ${demo.age_range.replace(" years", "")}, ${demo.district}`} />
                  <ReviewRow k="Feeling" v={form.target_emotion ? `${EMOTION_INFO[form.target_emotion]?.emoji} ${form.target_emotion}` : "✨ AI will choose"} />
                </dl>
              </div>
            </>
          )}

          {error && step === 3 && (
            <div className="error-box" role="alert">
              <span>{error}</span>
              <button className="nm-btn-secondary" style={{ width: "auto" }} onClick={run}>Try again</button>
            </div>
          )}

          <div className="wizard-nav">
            {step > 1 && (
              <button type="button" className="nm-btn-secondary" onClick={() => goTo(step - 1)}>Back</button>
            )}
            {step < 3 ? (
              <button type="button" className="nm-btn-primary" onClick={next}>
                Continue to {STEPS[step].name.toLowerCase()}
              </button>
            ) : (
              <button type="button" className="nm-btn-primary" onClick={run}>
                ✨ Create my message
              </button>
            )}
          </div>
        </div>
      </div>

      <p style={{ fontSize: 14, color: "var(--text-secondary)", textAlign: "center" }}>
        Your answers are saved on this device, so you won't lose them if the page reloads.
      </p>
      </div>
      <Guide step={step} />
      </div>
    </div>
  );
}

function FieldError({ id, children }) {
  return (
    <p id={id} role="alert" style={{ color: "var(--coral-600)", fontSize: 14, fontWeight: 600, marginTop: 6 }}>
      {children}
    </p>
  );
}

function WordHint({ id, count }) {
  if (count === 0) return <p id={id} className="sr-only">No description yet</p>;
  const ok = count >= MIN_WORDS;
  return (
    <p id={id} className="hint" style={{ color: ok ? "var(--teal-600)" : "var(--orange-600)" }}>
      <span className="hint-dot" style={{ background: ok ? "var(--teal-400)" : "var(--orange-400)" }} aria-hidden="true" />
      {ok
        ? `${count} words. That's enough detail.`
        : `${count} word${count === 1 ? "" : "s"}. Add a few more (at least ${MIN_WORDS}) so the AI understands your product.`}
    </p>
  );
}

function ReviewRow({ k, v }) {
  return (
    <div className="review-row">
      <dt>{k}</dt>
      <dd style={{ textTransform: k === "Feeling" ? "capitalize" : undefined }}>{v}</dd>
    </div>
  );
}
