import { useState } from "react";
import { apiPost } from "../api.js";
import ResultCode from "../components/ResultCode.jsx";
import CopyButton from "../components/CopyButton.jsx";
import Component1Result from "../components/Component1Result.jsx";

// ── Option constants — updated to match consumer-purchase.csv values ──
const CATEGORIES = [
  "Beauty", "Electronics", "Apparel", "Grocery",
  "Baby", "Pet Products", "Sports", "Home & Kitchen",
  "Automotive", "Industrial", "Unknown",
];

const DISTRICTS = [
  "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo",
  "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy",
  "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale",
  "Matara", "Monaragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa",
  "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya",
];

const GENDER_OPTIONS = ["Male", "Female"];

// Updated: "years" suffix matches consumer-purchase.csv format
// Both old and new formats accepted by agent.py encoder
const AGE_OPTIONS = [
  "18 – 24 years", "25 – 34 years",
  "35 – 44 years", "45 – 54 years", "55 and above",
];

// Updated: matches new employment status values in consumer-purchase.csv
const OCCUPATION_OPTIONS = [
  "Student",
  "Private sector employee",
  "Self-employed / Entrepreneur",
  "Government sector employee",
  "Unemployed",
  "Other",
];

// Updated: new income brackets from consumer-purchase.csv
const SPENDING_OPTIONS = [
  "Below Rs. 30,000",
  "Rs. 30,001 – Rs. 60,000",
  "Rs. 60,001 – Rs. 100,000",
  "Rs. 100,001 – Rs. 150,000",
  "Above Rs. 150,000",
];

// Updated: Q6 is now a 1–5 Likert scale (Hofstede, 1980)
// label shown to user, value sent to API
const CULTURE_OPTIONS = [
  { label: "1 — Does not influence my purchases", value: "1" },
  { label: "2 — Rarely influences",               value: "2" },
  { label: "3 — Somewhat influences",             value: "3" },
  { label: "4 — Often influences",                value: "4" },
  { label: "5 — Strongly influences my purchases",value: "5" },
];

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
  const [productText, setProductText]   = useState("");
  const [category, setCategory]         = useState(CATEGORIES[0]);
  const [demo, setDemo]                 = useState({
    gender:            GENDER_OPTIONS[0],
    age_range:         AGE_OPTIONS[0],
    district:          DISTRICTS[4],          // Colombo
    occupation:        OCCUPATION_OPTIONS[0],
    monthly_spending:  SPENDING_OPTIONS[1],   // Rs. 30,001–60,000
    culture_influence: CULTURE_OPTIONS[2].value, // "3" = Somewhat
  });
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const [result, setResult]     = useState(null);

  // Word count for validation indicator
  const wordCount    = productText.trim() ? productText.trim().split(/\s+/).length : 0;
  const wordCountOk  = wordCount >= MIN_WORDS;
  const wordCountMsg = wordCount === 0
    ? ""
    : wordCountOk
      ? `${wordCount} words ✓`
      : `${wordCount} words — minimum ${MIN_WORDS} recommended for accurate classification`;

  const runAnalysis = async (text = productText, cat = category) => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        product_text: text,
        category:     cat,
        demographics: {
          ...demo,
          // Product-level scores default to neutral.
          // RoBERTa handles product signals; demographic model handles profile.
          avg_emotional_appeal:   0.0,
          emotional_reason_count: 0,
          rational_reason_count:  0,
          rational_check_total:   0,
          emotional_check_total:  0,
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

  return (
    <div className="max-w-[1280px] mx-auto px-10 py-8 grid grid-cols-1 lg:grid-cols-[1.1fr_1.7fr] gap-8">

      {/* ══════════════════════════════════════════
          LEFT — Input panel
      ══════════════════════════════════════════ */}
      <div>

        {/* Product Input card */}
        <div className="nm-card">
          <div className="nm-card-header">
            <span className="nm-card-title">Product Input</span>
          </div>
          <div className="nm-card-body">
            <span className="field-label">Product Description</span>
            <textarea
              className="nm-textarea"
              rows={4}
              placeholder={"Enter product name and key features...\n\ne.g. Hemas Baby Care Coconut Oil 100% pure and gentle, trusted by Sri Lankan mothers for over 30 years, 200ml."}
              value={productText}
              onChange={(e) => setProductText(e.target.value)}
            />

            {/* Word count indicator — research validity signal */}
            {wordCount > 0 && (
              <div style={{
                fontSize: 11,
                marginTop: 6,
                marginBottom: 4,
                color: wordCountOk ? "var(--teal-600)" : "var(--amber-600)",
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}>
                <span style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: wordCountOk ? "var(--teal-400)" : "var(--amber-400)",
                  display: "inline-block", flexShrink: 0,
                }} />
                {wordCountMsg}
              </div>
            )}

            <span className="field-label" style={{ marginTop: 12, display: "block" }}>Product Category</span>
            <select
              className="nm-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        {/* Consumer Profile card */}
        <div className="nm-card">
          <div className="nm-card-header">
            <span className="nm-card-title">Consumer Profile</span>
            <span
              className="nm-badge"
              style={{ background: "var(--teal-50)", color: "var(--teal-600)", border: "1px solid var(--teal-100)" }}
            >
              Required
            </span>
          </div>
          <div className="nm-card-body">
            <div style={{
              background: "var(--purple-50)", border: "1px solid var(--purple-100)",
              borderRadius: "var(--radius-md)", padding: "14px 16px",
            }}>
              <div style={{
                fontFamily: "Syne, sans-serif", fontSize: 12, fontWeight: 700,
                color: "var(--purple-800)", marginBottom: 12,
                textTransform: "uppercase", letterSpacing: ".05em",
              }}>
                Consumer Details
              </div>

              {/* ── Group A: Who you are ── */}
              <div style={{
                fontSize: 10, fontWeight: 600, color: "var(--text-muted)",
                textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 6,
              }}>
                Who you are
              </div>
              <div className="grid grid-cols-2 gap-x-4" style={{ marginBottom: 12 }}>
                <div>
                  <span className="field-label">Gender</span>
                  <select
                    className="nm-select"
                    value={demo.gender}
                    onChange={(e) => setDemo({ ...demo, gender: e.target.value })}
                  >
                    {GENDER_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <span className="field-label">Age Range</span>
                  <select
                    className="nm-select"
                    value={demo.age_range}
                    onChange={(e) => setDemo({ ...demo, age_range: e.target.value })}
                  >
                    {AGE_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
              </div>

              {/* ── Group B: Where you are ── */}
              <div style={{
                fontSize: 10, fontWeight: 600, color: "var(--text-muted)",
                textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 6,
              }}>
                Where you are
              </div>
              <div style={{ marginBottom: 12 }}>
                <span className="field-label">District</span>
                <select
                  className="nm-select"
                  value={demo.district}
                  onChange={(e) => setDemo({ ...demo, district: e.target.value })}
                >
                  {DISTRICTS.map((o) => <option key={o}>{o}</option>)}
                </select>
              </div>

              {/* ── Group C: Your context ── */}
              <div style={{
                fontSize: 10, fontWeight: 600, color: "var(--text-muted)",
                textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 6,
              }}>
                Your context
              </div>
              <div className="grid grid-cols-2 gap-x-4">
                <div>
                  <span className="field-label">Occupation</span>
                  <select
                    className="nm-select"
                    value={demo.occupation}
                    onChange={(e) => setDemo({ ...demo, occupation: e.target.value })}
                  >
                    {OCCUPATION_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <span className="field-label">Monthly Spending</span>
                  <select
                    className="nm-select"
                    value={demo.monthly_spending}
                    onChange={(e) => setDemo({ ...demo, monthly_spending: e.target.value })}
                  >
                    {SPENDING_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
              </div>

              {/* Cultural influence with tooltip explanation */}
              <div style={{ marginTop: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  <span className="field-label" style={{ margin: 0 }}>Cultural Influence</span>
                  <div style={{ position: "relative", display: "inline-block" }} className="tooltip-wrap">
                    <span style={{
                      width: 16, height: 16, borderRadius: "50%",
                      background: "var(--purple-100)", color: "var(--purple-800)",
                      fontSize: 10, fontWeight: 700, cursor: "help",
                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                    }}>?</span>
                    <div className="tooltip-box" style={{
                      position: "absolute", bottom: "calc(100% + 6px)", left: "50%",
                      transform: "translateX(-50%)", width: 230,
                      background: "var(--text-primary)", color: "#fff",
                      fontSize: 11, lineHeight: 1.5, padding: "8px 10px",
                      borderRadius: "var(--radius-sm)", zIndex: 50,
                      pointerEvents: "none",
                    }}>
                      Based on Hofstede's Cultural Dimensions Theory (1980).
                      How much do your cultural background and family values
                      influence what products you choose to buy?
                      <br /><br />
                      1 = Does not influence at all
                      <br />
                      5 = Strongly influences every purchase
                    </div>
                  </div>
                </div>
                <select
                  className="nm-select"
                  value={demo.culture_influence}
                  onChange={(e) => setDemo({ ...demo, culture_influence: e.target.value })}
                >
                  {CULTURE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        <button
          className="nm-btn-primary"
          disabled={!productText.trim() || loading}
          onClick={() => runAnalysis()}
        >
          {loading ? "Analyzing…" : "Analyze & Generate Strategy ↗"}
        </button>

        {/* Example Products */}
        <div className="nm-card" style={{ marginTop: 16 }}>
          <div className="nm-card-header">
            <span className="nm-card-title">Example Products</span>
          </div>
          <div className="nm-card-body space-y-2">
            {EXAMPLES.map(([text, cat]) => (
              <button key={text} className="nm-btn-ghost" onClick={() => useExample(text, cat)}>
                →  {text.slice(0, 52)}…
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════
          RIGHT — Results panel
      ══════════════════════════════════════════ */}
      <div>
        {error && (
          <div style={{
            background: "var(--coral-50)", border: "1px solid var(--coral-100)",
            borderRadius: "var(--radius-md)", padding: "12px 16px",
            color: "var(--coral-600)", fontSize: 13, marginBottom: 12,
          }}>
            {error}
          </div>
        )}

        {!result && !loading && (
          <div className="nm-card">
            <div className="nm-card-body">
              <div className="empty-state">
                <div className="empty-title">Ready to Analyze</div>
                <div className="empty-desc">
                  Enter a product description, fill in the consumer profile,
                  and click Analyze to identify the best marketing approach and generate
                  psychologically aligned marketing copy.
                </div>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="nm-card">
            <div className="nm-card-body">
              <div className="empty-state">
                <div style={{
                  width: 40, height: 40, borderRadius: "50%",
                  border: "3px solid var(--border)",
                  borderTop: "3px solid var(--coral-400)",
                  animation: "spin 1s linear infinite",
                  margin: "0 auto 16px",
                }} />
                <div className="empty-title" style={{ fontSize: 14 }}>
                  Analyzing your product…
                </div>
                <div className="empty-desc">
                  Our AI is generating your marketing copy.
                  This takes about 10–15 seconds.
                </div>
              </div>
            </div>
          </div>
        )}

        {result && !loading && <ResultView result={result} productText={productText} category={category} />}
      </div>
    </div>
  );
}


// ══════════════════════════════════════════════════════════════
// ResultView — displays classification + copy + output JSON
// ══════════════════════════════════════════════════════════════
function ResultView({ result, productText, category }) {
  return <Component1Result result={result} productText={productText} category={category} />;
}
