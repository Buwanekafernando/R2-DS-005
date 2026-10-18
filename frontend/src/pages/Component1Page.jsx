import { useState } from "react";
import { apiPost } from "../api.js";
import Component1Result from "../components/Component1Result.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Tooltip from "../components/Tooltip.jsx";
import {
  CATEGORIES, categoryLabel, DISTRICTS, GENDER_OPTIONS, AGE_OPTIONS,
  OCCUPATION_OPTIONS, SPENDING_OPTIONS, CULTURE_OPTIONS, AGENTS,
} from "../constants.js";
import { G } from "../components/Term.jsx";

const EXAMPLES = [
  ["Maliban Chocolate Cream Biscuits crispy sweet snack pack of 3 family size", "Grocery"],
  ["Abans 55 inch 4K Smart LED TV Android WiFi Bluetooth HDR Dolby Audio", "Electronics"],
  ["Samsung Galaxy A55 5G smartphone 128GB 8GB RAM 50MP camera dual SIM Sri Lanka", "Electronics"],
  ["Hameedia Men Formal Shirt slim fit 100 cotton office wear Sri Lankan brand", "Apparel"],
  ["Spa Ceylon Ayurveda Lavender Neem Body Lotion luxury herbal natural moisturizer 200ml", "Beauty"],
];

// Minimum word count for reliable classification
const MIN_WORDS = 8;

export default function Component1Page({ onResult }) {
  const [productText, setProductText] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [demo, setDemo] = useState({
    gender: GENDER_OPTIONS[0],
    age_range: AGE_OPTIONS[0],
    district: DISTRICTS[4],                     // Colombo
    occupation: OCCUPATION_OPTIONS[0],
    monthly_spending: SPENDING_OPTIONS[1],      // Rs. 30,001–60,000
    culture_influence: CULTURE_OPTIONS[2].value, // "3" = Somewhat
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const wordCount = productText.trim() ? productText.trim().split(/\s+/).length : 0;
  const wordCountOk = wordCount >= MIN_WORDS;

  const runAnalysis = async (text = productText, cat = category) => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        product_text: text,
        category: cat,
        demographics: {
          ...demo,
          // Product-level scores default to neutral.
          // RoBERTa handles product signals; demographic model handles profile.
          avg_emotional_appeal: 0.0,
          emotional_reason_count: 0,
          rational_reason_count: 0,
          rational_check_total: 0,
          emotional_check_total: 0,
        },
      };
      const data = await apiPost("/component1/analyze", payload);
      setResult(data);
      onResult?.(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const useExample = (text, cat) => {
    setProductText(text);
    setCategory(cat);
    runAnalysis(text, cat);
  };

  const select = (key, options, label) => (
    <div style={{ marginTop: 14 }}>
      <label className="field-label" htmlFor={`c1-${key}`}>{label}</label>
      <select id={`c1-${key}`} className="nm-select" value={demo[key]} onChange={(e) => setDemo({ ...demo, [key]: e.target.value })}>
        {options.map((o) => typeof o === "string"
          ? <option key={o}>{o}</option>
          : <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );

  return (
    <div className="page page-wide">
      <PageHeader
        title={`${AGENTS.decide.emoji} How your customers decide`}
        intro={`Try the first AI helper on its own (${AGENTS.decide.component}: ${AGENTS.decide.research}). It works out whether people buy your product on feeling or after comparing, and writes copy to match.`}
      />

      <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_1.7fr] gap-8">
        {/* Left: input */}
        <div>
          <div className="nm-card">
            <div className="nm-card-header"><h2 className="nm-card-title">Your product</h2></div>
            <div className="nm-card-body">
              <label className="field-label" htmlFor="c1-desc">Describe your product</label>
              <textarea
                id="c1-desc"
                className="nm-textarea"
                rows={4}
                placeholder="e.g. Hemas Baby Care Coconut Oil, 100% pure and gentle, trusted by Sri Lankan mothers for over 30 years, 200ml."
                value={productText}
                onChange={(e) => setProductText(e.target.value)}
              />
              {wordCount > 0 && (
                <p className="hint" style={{ color: wordCountOk ? "var(--teal-600)" : "var(--orange-600)" }}>
                  <span className="hint-dot" style={{ background: wordCountOk ? "var(--teal-400)" : "var(--orange-400)" }} aria-hidden="true" />
                  {wordCountOk ? `${wordCount} words. That's enough detail.` : `${wordCount} words. Add a few more (at least ${MIN_WORDS}) for an accurate result.`}
                </p>
              )}

              <label className="field-label" htmlFor="c1-cat">Product type</label>
              <select id="c1-cat" className="nm-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                {CATEGORIES.map((c) => <option key={c} value={c}>{categoryLabel(c)}</option>)}
              </select>
            </div>
          </div>

          <div className="nm-card">
            <div className="nm-card-header">
              <h2 className="nm-card-title">A typical customer</h2>
            </div>
            <div className="nm-card-body">
              <p className="field-help" style={{ marginBottom: 0 }}><G>Picture one typical buyer. A rough guess is fine.</G></p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4">
                {select("gender", GENDER_OPTIONS, "Gender")}
                {select("age_range", AGE_OPTIONS, "Age")}
                {select("district", DISTRICTS, "Where they live")}
                {select("occupation", OCCUPATION_OPTIONS, "What they do")}
              </div>
              {select("monthly_spending", SPENDING_OPTIONS, "Monthly spending")}
              <div style={{ marginTop: 14 }}>
                <label className="field-label" htmlFor="c1-culture_influence">
                  How much do traditions and culture shape what they buy?
                  <Tooltip text="Based on Hofstede's cultural dimensions (1980). 1 = does not influence their purchases at all, 5 = strongly influences every purchase." />
                </label>
                <select id="c1-culture_influence" className="nm-select" value={demo.culture_influence} onChange={(e) => setDemo({ ...demo, culture_influence: e.target.value })}>
                  {CULTURE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>
            </div>
          </div>

          <button className="nm-btn-primary" disabled={!productText.trim() || loading} onClick={() => runAnalysis()}>
            {loading ? "Working it out…" : "Find out how customers decide"}
          </button>

          <div className="nm-card" style={{ marginTop: 16 }}>
            <div className="nm-card-header"><h2 className="nm-card-title">Or try an example</h2></div>
            <div className="nm-card-body" style={{ display: "grid", gap: 8 }}>
              {EXAMPLES.map(([text, cat]) => (
                <button key={text} className="nm-btn-ghost" onClick={() => useExample(text, cat)} disabled={loading}>
                  {text.length > 64 ? `${text.slice(0, 64)}…` : text}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: results */}
        <div>
          {error && <div className="error-box" role="alert" style={{ marginTop: 0, marginBottom: 12 }}>{error}</div>}

          {!result && !loading && (
            <div className="nm-card">
              <div className="nm-card-body empty-state">
                <div className="empty-icon" style={{ background: "var(--cyan-50)", border: "1px solid var(--cyan-100)" }} aria-hidden="true">{AGENTS.decide.emoji}</div>
                <div className="empty-title">Your result will appear here</div>
                <div className="empty-desc">
                  <G>Describe your product, picture a typical customer, then press
                  "Find out how customers decide". Or pick an example.</G>
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div className="nm-card" aria-live="polite">
              <div className="nm-card-body empty-state">
                <div className="spinner" />
                <div className="empty-title">Working out how customers decide…</div>
                <div className="empty-desc"><G>Reading your description and writing two versions of your copy. About 10 to 15 seconds.</G></div>
              </div>
            </div>
          )}

          {result && !loading && <Component1Result result={result} productText={productText} category={category} />}
        </div>
      </div>
    </div>
  );
}
