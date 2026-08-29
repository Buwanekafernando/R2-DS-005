import { useState } from "react";
import { apiPost } from "../api.js";

// Constants — values match consumer-purchase.csv exactly ──────
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

// FIX 1: Updated to match consumer-purchase.csv exact values
const GENDER_OPTIONS = ["Male", "Female"];

const AGE_OPTIONS = [
  "18 – 24 years", "25 – 34 years",
  "35 – 44 years", "45 – 54 years", "55 and above",
];

const OCCUPATION_OPTIONS = [
  "Student",
  "Private sector employee",
  "Self-employed / Entrepreneur",
  "Government sector employee",
  "Unemployed",
  "Other",
];

const SPENDING_OPTIONS = [
  "Below Rs. 30,000",
  "Rs. 30,001 – Rs. 60,000",
  "Rs. 60,001 – Rs. 100,000",
  "Rs. 100,001 – Rs. 150,000",
  "Above Rs. 150,000",
];

//Culture is now 1-5 Likert scale — label shown, number sent to API
// Grounded in Hofstede's Cultural Dimensions Theory (1980)
const CULTURE_OPTIONS = [
  { label: "1 — Strongly Disagree", value: "1" },
  { label: "2 — Disagree",          value: "2" },
  { label: "3 — Neutral",           value: "3" },
  { label: "4 — Agree",             value: "4" },
  { label: "5 — Strongly Agree",    value: "5" },
];

const EXAMPLES = [
  ["Maliban Chocolate Cream Biscuits crispy sweet snack pack of 3 family size", "Grocery"],
  ["Abans 55 inch 4K Smart LED TV Android WiFi Bluetooth HDR Dolby Audio", "Electronics"],
  ["Samsung Galaxy A55 5G smartphone 128GB 8GB RAM 50MP camera dual SIM Sri Lanka", "Electronics"],
  ["Hameedia Men Formal Shirt slim fit 100 cotton office wear Sri Lankan brand", "Apparel"],
  ["Spa Ceylon Ayurveda Lavender Neem Body Lotion luxury herbal natural moisturizer 200ml", "Beauty"],
];

const MIN_WORDS = 8;

// ── Copy-to-clipboard helper 
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* fallback silent fail */
    }
  };
  return (
    <button
      onClick={handleCopy}
      title="Copy to clipboard"
      style={{
        background: "none", border: "none", cursor: "pointer",
        fontSize: 13, padding: "2px 6px", borderRadius: 4,
        color: copied ? "var(--teal-600)" : "var(--text-muted)",
        transition: "color 0.2s",
      }}
    >
      {copied ? "✓ Copied" : "⎘ Copy"}
    </button>
  );
}

// ── Tooltip helper 
function Tooltip({ text, children }) {
  const [visible, setVisible] = useState(false);
  return (
    <span
      style={{ position: "relative", display: "inline-flex", alignItems: "center", gap: 4 }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span style={{
          position: "absolute", bottom: "calc(100% + 6px)", left: 0,
          background: "var(--text-primary)", color: "#fff",
          fontSize: 11, padding: "6px 10px", borderRadius: 6,
          whiteSpace: "pre-line", zIndex: 100, width: 220,
          boxShadow: "0 4px 12px rgba(0,0,0,0.15)", lineHeight: 1.5,
        }}>
          {text}
        </span>
      )}
    </span>
  );
}

// ── Word count indicator 
function WordCount({ text }) {
  const count = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
  const ok = count >= MIN_WORDS;
  return (
    <div style={{ fontSize: 11, marginTop: 4, marginBottom: 8,
      color: ok ? "var(--teal-600)" : "var(--coral-600)", display: "flex", alignItems: "center", gap: 4 }}>
      {ok ? "✓" : "⚠"} {count} word{count !== 1 ? "s" : ""}
      {!ok && ` — minimum ${MIN_WORDS} words recommended`}
    </div>
  );
}

// ── Plain-English mode explanation
const MODE_EXPLANATIONS = {
  System1: "This product triggers fast, feeling-based buying decisions. Consumers are unlikely to research or compare — they buy because it feels right.",
  System2: "This product triggers slow, research-based buying decisions. Consumers will compare options, read reviews, and gather information before purchasing.",
};


export default function Component1Page({ onResult }) {
  const [productText, setProductText] = useState("");
  const [category, setCategory]       = useState(CATEGORIES[0]);

  // FIX 3: Default values updated to match new dataset format
  const [demo, setDemo] = useState({
    gender:            GENDER_OPTIONS[0],      // "Male"
    age_range:         AGE_OPTIONS[0],         // "18 – 24 years"
    district:          DISTRICTS[4],           // "Colombo"
    occupation:        OCCUPATION_OPTIONS[0],  // "Student"
    monthly_spending:  SPENDING_OPTIONS[2],    // "Rs. 60,001 – Rs. 100,000"
    culture_influence: CULTURE_OPTIONS[2].value, // "3" (Neutral)
  });

  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");
  const [result,  setResult]  = useState(null);

  const wordCount = productText.trim() === "" ? 0
    : productText.trim().split(/\s+/).length;
  const canSubmit = productText.trim() && wordCount >= MIN_WORDS && !loading;

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
          avg_emotional_appeal:    0.0,
          emotional_reason_count:  0,
          rational_reason_count:   0,
          rational_check_total:    0,
          emotional_check_total:   0,
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

      {/* LEFT PANEL — Input */}
      <div>

        {/* Product Input card */}
        <div className="nm-card">
          <div className="nm-card-header">
            <span className="nm-card-title">Product Input</span>
          </div>
          <div className="nm-card-body">
            <span className="field-label">Product Description</span>

            {/* FIX 4: Word count indicator */}
            <textarea
              className="nm-textarea"
              rows={4}
              placeholder={"Enter product name and key features...\n\ne.g. Hemas Baby Care Coconut Oil, 100% pure and gentle,\ntrusted by Sri Lankan mothers for over 30 years, 200ml."}
              value={productText}
              onChange={(e) => setProductText(e.target.value)}
            />
            <WordCount text={productText} />

            <span className="field-label">Product Category</span>
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
              style={{ background:"var(--teal-50)", color:"var(--teal-600)", border:"1px solid var(--teal-100)" }}
            >
              Required
            </span>
          </div>
          <div className="nm-card-body">
            <div style={{ background:"var(--purple-50)", border:"1px solid var(--purple-100)", borderRadius:"var(--radius-md)", padding:"14px 16px" }}>

              {/* FIX 5: Visual grouping — Who you are */}
              <div style={{ fontFamily:"Syne,sans-serif", fontSize:11, fontWeight:700, color:"var(--purple-800)", marginBottom:10, textTransform:"uppercase", letterSpacing:".08em" }}>
                Who you are
              </div>
              <div className="grid grid-cols-2 gap-x-4">
                <div>
                  <span className="field-label">Gender</span>
                  <select className="nm-select" value={demo.gender}
                    onChange={(e) => setDemo({ ...demo, gender: e.target.value })}>
                    {GENDER_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>

                  <span className="field-label">Age Range</span>
                  <select className="nm-select" value={demo.age_range}
                    onChange={(e) => setDemo({ ...demo, age_range: e.target.value })}>
                    {AGE_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <span className="field-label">Occupation</span>
                  <select className="nm-select" value={demo.occupation}
                    onChange={(e) => setDemo({ ...demo, occupation: e.target.value })}>
                    {OCCUPATION_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>

                  <span className="field-label">District</span>
                  <select className="nm-select" value={demo.district}
                    onChange={(e) => setDemo({ ...demo, district: e.target.value })}>
                    {DISTRICTS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
              </div>

              {/* FIX 5 continued: Your context group */}
              <div style={{ fontFamily:"Syne,sans-serif", fontSize:11, fontWeight:700, color:"var(--purple-800)", margin:"14px 0 10px", textTransform:"uppercase", letterSpacing:".08em" }}>
                Your context
              </div>
              <div className="grid grid-cols-2 gap-x-4">
                <div>
                  <span className="field-label">Monthly Spending</span>
                  <select className="nm-select" value={demo.monthly_spending}
                    onChange={(e) => setDemo({ ...demo, monthly_spending: e.target.value })}>
                    {SPENDING_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  {/* FIX 6: Cultural influence tooltip */}
                  <Tooltip text={"Based on Hofstede's Cultural Dimensions Theory (1980).\n\nHow much do your cultural background and family traditions influence your purchase decisions?\n\n1 = Does not influence at all\n5 = Strongly influences every purchase"}>
                    <span className="field-label" style={{ cursor:"help", borderBottom:"1px dashed var(--text-muted)" }}>
                      Cultural Influence ⓘ
                    </span>
                  </Tooltip>
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
        </div>

        <button
          className="nm-btn-primary"
          disabled={!canSubmit}
          onClick={() => runAnalysis()}
        >
          {loading ? "Analyzing…" : "Analyze & Generate Strategy ↗"}
        </button>

        {/* Word count warning below button when too short */}
        {productText.trim() && wordCount < MIN_WORDS && (
          <p style={{ fontSize:11, color:"var(--coral-600)", marginTop:6, textAlign:"center" }}>
            Add more product details for a more accurate classification.
          </p>
        )}

        {/* Example Products */}
        <div className="nm-card" style={{ marginTop:16 }}>
          <div className="nm-card-header">
            <span className="nm-card-title">Example Products</span>
          </div>
          <div className="nm-card-body space-y-2">
            {EXAMPLES.map(([text, cat]) => (
              <button
                key={text}
                className="nm-btn-ghost"
                onClick={() => useExample(text, cat)}
              >
                → {text.slice(0, 52)}…
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* RIGHT PANEL — Results*/}
      <div>
        {error && (
          <div style={{ background:"var(--coral-50)", border:"1px solid var(--coral-100)",
            borderRadius:"var(--radius-md)", padding:"12px 16px",
            color:"var(--coral-600)", fontSize:13, marginBottom:12 }}>
            {error}
          </div>
        )}

        {loading && (
          <div className="nm-card">
            <div className="nm-card-body" style={{ textAlign:"center", padding:"40px 20px" }}>
              <div style={{ fontSize:13, color:"var(--text-muted)" }}>
                Classifying cognitive mode and generating copy…
              </div>
            </div>
          </div>
        )}

        {!result && !loading && (
          <div className="nm-card">
            <div className="nm-card-body">
              <div className="empty-state">
                <div className="empty-title">Ready to Analyze</div>
                <div className="empty-desc">
                  Enter a product description, fill in the consumer profile, and click Analyze to classify cognitive mode and generate personalised marketing copy.
                </div>
              </div>
            </div>
          </div>
        )}

        {result && !loading && <ResultView result={result} />}
      </div>
    </div>
  );
}


//Result View Component 
function ResultView({ result }) {
  const clf      = result.classification;
  const gen      = result.generated_copy;
  const rec      = result.recommendation;
  const agentOut = result.agent_output;

  const isS1    = clf.cognitive_mode === "System1";
  const bg      = isS1 ? "var(--amber-50)"  : "var(--blue-50)";
  const bdr     = isS1 ? "var(--amber-100)" : "var(--blue-100)";
  const txt     = isS1 ? "var(--amber-600)" : "var(--blue-800)";
  const bar     = isS1 ? "var(--amber-400)" : "var(--blue-600)";
  const icon    = isS1 ? "⚡" : "🔍";
  const label   = isS1 ? "System 1 — Emotional / Impulsive" : "System 2 — Rational / Deliberative";

  const strategy  = rec.strategy;
  const isEmoRec  = strategy === "emotional";

  // FIX 7: Plain-English explanation for the classification
  const modeExplanation = MODE_EXPLANATIONS[clf.cognitive_mode];

  return (
    <>
      {/* Classification Result card */}
      <div className="nm-card" style={{ animation:"fadeUp .4s ease" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">Classification Result</span>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <span className="nm-badge" style={{ background:"var(--purple-50)", color:"var(--purple-800)", border:"1px solid var(--purple-100)" }}>
              Product + Demographic
            </span>
            <span className="nm-badge" style={{ background:"var(--teal-50)", color:"var(--teal-600)", border:"1px solid var(--teal-100)" }}>
              RoBERTa + Demo
            </span>
          </div>
        </div>
        <div className="nm-card-body">
          <div className="clf-badge" style={{ background:bg, borderColor:bdr }}>
            <div className="clf-mode" style={{ color:txt }}>{icon} {label}</div>

            {/* FIX 8: Plain-English explanation directly inside the badge */}
            <div style={{ fontSize:12, color:txt, marginBottom:8, lineHeight:1.5, opacity:0.85 }}>
              {modeExplanation}
            </div>

            <div style={{ fontSize:11, color:txt, marginBottom:4 }}>Confidence</div>
            <div className="clf-bar-wrap">
              <div className="clf-bar" style={{ width:`${clf.confidence * 100}%`, background:bar }} />
            </div>
            <div className="clf-probs" style={{ color:txt }}>
              <span><strong>{(clf.confidence * 100).toFixed(1)}%</strong></span>
              <span>S1: {clf.s1_probability.toFixed(3)}</span>
              <span>S2: {clf.s2_probability.toFixed(3)}</span>
            </div>
          </div>
          <div style={{ fontSize:12, color:"var(--text-muted)", fontStyle:"italic", marginTop:8 }}>
            {clf.reasoning}
          </div>
        </div>
      </div>

      {/* Generated Marketing Copy card */}
      <div className="nm-card" style={{ animation:"fadeUp .4s ease .1s both" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">Generated Marketing Copy</span>
        </div>
        <div className="nm-card-body">
          <div className="copy-grid">

            {/* Emotional copy */}
            <div
              className="copy-card"
              style={{
                background: "var(--amber-50)",
                border: isEmoRec ? "2px solid var(--amber-400)" : "1px solid var(--amber-100)",
              }}
            >
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:6 }}>
                <div className="copy-label" style={{ color:"var(--amber-600)", margin:0 }}>
                  ⚡ Emotional {isEmoRec && "· Recommended"}
                </div>
                {/* FIX 9: Copy-to-clipboard button */}
                <CopyButton text={gen.emotional.text} />
              </div>
              <div className="copy-text" style={{ color:"#3d2200" }}>{gen.emotional.text}</div>
              <div className="copy-meta" style={{ color:"var(--amber-600)" }}>
                Sentiment: {gen.emotional.quality.sentiment_compound.toFixed(2)}
                &nbsp;·&nbsp;
                Alignment: {(gen.emotional.quality.mode_alignment * 100).toFixed(0)}%
              </div>
            </div>

            {/* Rational copy */}
            <div
              className="copy-card"
              style={{
                background: "var(--blue-50)",
                border: !isEmoRec ? "2px solid var(--blue-600)" : "1px solid var(--blue-100)",
              }}
            >
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:6 }}>
                <div className="copy-label" style={{ color:"var(--blue-800)", margin:0 }}>
                  🔍 Rational {!isEmoRec && "· Recommended"}
                </div>
                {/* FIX 9: Copy-to-clipboard button */}
                <CopyButton text={gen.rational.text} />
              </div>
              <div className="copy-text" style={{ color:"#0a2d52" }}>{gen.rational.text}</div>
              <div className="copy-meta" style={{ color:"var(--blue-800)" }}>
                Sentiment: {gen.rational.quality.sentiment_compound.toFixed(2)}
                &nbsp;·&nbsp;
                Alignment: {(gen.rational.quality.mode_alignment * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          {/* Strategy recommendation */}
          <div
            className="strategy-box"
            style={{
              background:   isEmoRec ? "var(--amber-50)"  : "var(--blue-50)",
              borderColor:  isEmoRec ? "var(--amber-100)" : "var(--blue-100)",
            }}
          >
            <div>
              <div className="strategy-box-label" style={{ color: isEmoRec ? "var(--amber-600)" : "var(--blue-800)" }}>
                Recommended Strategy
              </div>
              <div className="strategy-box-text" style={{ color: isEmoRec ? "var(--amber-600)" : "var(--blue-800)" }}>
                {rec.explanation}
              </div>
            </div>
          </div>

          {/* Metrics row */}
          <div className="metrics-row">
            <div className="metric-box">
              <div className="metric-val">{(clf.confidence * 100).toFixed(0)}%</div>
              <div className="metric-lbl">Confidence</div>
            </div>
            <div className="metric-box">
              <div className="metric-val">{(gen.emotional.quality.mode_alignment * 100).toFixed(0)}%</div>
              <div className="metric-lbl">Emo. Alignment</div>
            </div>
            <div className="metric-box">
              <div className="metric-val">{(gen.rational.quality.mode_alignment * 100).toFixed(0)}%</div>
              <div className="metric-lbl">Rat. Alignment</div>
            </div>
          </div>
        </div>
      </div>

      {/* Output for Components 2, 3, 4 */}
      <div className="nm-card" style={{ animation:"fadeUp .4s ease .2s both" }}>
        <div className="nm-card-header">
          <span className="nm-card-title">🔗 Output for Components 2, 3, 4</span>
          <CopyButton text={JSON.stringify({
            cognitive_mode:   agentOut.cognitive_mode,
            confidence:       agentOut.confidence,
            strategy:         agentOut.strategy,
            recommended_copy: agentOut.recommended_copy,
          }, null, 2)} />
        </div>
        <div className="nm-card-body">
          <pre className="nm-json">{JSON.stringify({
            cognitive_mode:   agentOut.cognitive_mode,
            confidence:       agentOut.confidence,
            strategy:         agentOut.strategy,
            recommended_copy: agentOut.recommended_copy,
          }, null, 2)}</pre>
        </div>
      </div>
    </>
  );
}
