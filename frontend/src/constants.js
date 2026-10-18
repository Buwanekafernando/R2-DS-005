export const DISTRICTS = [
  "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo",
  "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy",
  "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale",
  "Matara", "Monaragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa",
  "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya",
];
export const GENDER_OPTIONS = ["Male", "Female"];

// "years" suffix matches consumer-purchase.csv format used to train the demographic model
export const AGE_OPTIONS = [
  "18 – 24 years", "25 – 34 years",
  "35 – 44 years", "45 – 54 years", "55 and above",
];

// Matches employment status values in consumer-purchase.csv
export const OCCUPATION_OPTIONS = [
  "Student",
  "Private sector employee",
  "Self-employed / Entrepreneur",
  "Government sector employee",
  "Unemployed",
  "Other",
];

// Matches income brackets in consumer-purchase.csv
export const SPENDING_OPTIONS = [
  "Below Rs. 30,000",
  "Rs. 30,001 – Rs. 60,000",
  "Rs. 60,001 – Rs. 100,000",
  "Rs. 100,001 – Rs. 150,000",
  "Above Rs. 150,000",
];

// Q6 is a 1–5 Likert scale (Hofstede, 1980) — label shown to user, value sent to API
export const CULTURE_OPTIONS = [
  { label: "1 — Does not influence my purchases", value: "1" },
  { label: "2 — Rarely influences",               value: "2" },
  { label: "3 — Somewhat influences",             value: "3" },
  { label: "4 — Often influences",                value: "4" },
  { label: "5 — Strongly influences my purchases",value: "5" },
];

// The 7 product types used on every page (the same seven the urgency page
// always used). Names match the backend's CATEGORY_EMOTION_MAP keys exactly.
export const CATEGORIES = [
  "Beauty", "Electronics", "Apparel", "Grocery",
  "Baby", "Pet Products", "Sports",
];
// Old saved answers may still hold a type that's no longer offered.
export const validCategory = (c) => (CATEGORIES.includes(c) ? c : CATEGORIES[0]);
export const EMOTIONS = ["joy", "excitement", "trust", "confidence", "curiosity", "relief", "admiration", "neutral"];

// Mirrors the backend's CATEGORY_EMOTION_MAP in src/component2/emotion_agent.py
// exactly — keep these in sync. First entry in each list is the auto-selected
// default for that category.
export const CATEGORY_EMOTION_MAP = {
  "Baby": ["trust", "relief", "joy"],
  "Beauty": ["confidence", "trust", "joy"],
  "Apparel": ["joy", "excitement", "admiration"],
  "Electronics": ["excitement", "joy", "admiration"],
  "Sports": ["excitement", "confidence", "curiosity"],
  "Pet Products": ["joy", "trust"],
  "Grocery": ["trust", "relief", "joy"],
  "Home & Kitchen": ["trust", "relief", "confidence"],
  "Automotive": ["confidence", "excitement", "trust"],
  "Industrial": ["trust", "confidence"],
  "Unknown": ["trust", "joy"],
};

export const defaultEmotionFor = (category) =>
  (CATEGORY_EMOTION_MAP[category] || [])[0] || "";

// Plain-language product names for the four research components — a
// small-business user never needs to know these are "Component 1/2/3/4",
// just what each one actually does for their marketing.
export const FEATURE_NAMES = {
  component1: "Buying Psychology",
  component2: "Emotional Appeal",
  component3: "Urgency & Scarcity",
  component4: "Loss-Framed Messaging",
  component24: "Emotional Appeal & Loss Messaging",
};

export const defaultDemographics = () => ({
  gender: GENDER_OPTIONS[0],
  age_range: AGE_OPTIONS[0],
  district: DISTRICTS[4],            // Colombo
  occupation: OCCUPATION_OPTIONS[0],
  monthly_spending: SPENDING_OPTIONS[1],   // Rs. 30,001–60,000
  culture_influence: CULTURE_OPTIONS[2].value, // "3" = Somewhat
  avg_emotional_appeal: 0.0,
  emotional_reason_count: 0,
  rational_reason_count: 0,
  rational_check_total: 0,
  emotional_check_total: 0,
});

// ─────────────────────────────────────────────────────────────────
// Friendly display helpers (UI only — nothing here is sent to the API)
// ─────────────────────────────────────────────────────────────────

export const CATEGORY_ICONS = {
  "Beauty": "💄", "Electronics": "🎧", "Apparel": "👕", "Grocery": "🛒",
  "Baby": "🍼", "Pet Products": "🐾", "Sports": "⚽", "Home & Kitchen": "🏠",
  "Automotive": "🚗", "Industrial": "🏭", "Unknown": "📦",
};
// "Unknown" is what the model expects; "Something else" is what people understand.
export const categoryLabel = (c) => (c === "Unknown" ? "Something else" : c);

// What each emotion feels like, in everyday words.
export const EMOTION_INFO = {
  joy:        { emoji: "😊", desc: "Happy, warm, feel-good" },
  excitement: { emoji: "🤩", desc: "Energy and can't-wait thrill" },
  trust:      { emoji: "🤝", desc: "Safe, reliable and honest" },
  confidence: { emoji: "💪", desc: "\"I can do this\" — moving forward" },
  curiosity:  { emoji: "🔍", desc: "Intrigued, wants to find out more" },
  relief:     { emoji: "😌", desc: "Calm, the stress goes away" },
  admiration: { emoji: "🌟", desc: "Wow, beautifully made" },
  neutral:    { emoji: "📋", desc: "Plain facts, no strong feeling" },
};
export const emotionEmoji = (e) => EMOTION_INFO[String(e || "").toLowerCase()]?.emoji || "💬";

// The four AI helpers. Each keeps one colour everywhere in the app so
// people learn to recognise them; `research` is the name used in the
// thesis/viva, `name` is what a shop owner understands.
export const AGENTS = {
  decide:  { emoji: "🧠", color: "cyan",   name: "How they decide",  research: "Dual-System Reasoning", component: "Component 1", feature: "Buying Psychology" },
  feeling: { emoji: "💗", color: "yellow",   name: "What they feel",   research: "Emotion Propagation",   component: "Component 2", feature: "Emotional Appeal" },
  urgency: { emoji: "⏳", color: "orange",  name: "Why act now",      research: "Scarcity Optimization", component: "Component 3", feature: "Urgency & Scarcity" },
  missout: { emoji: "🔁", color: "violet", name: "What they'd miss", research: "Loss Framing",          component: "Component 4", feature: "Loss-Framed Messaging" },
};

// CSS colour values for one helper: light tint, border, bright and readable text.
export const agentVars = (color) => ({
  "--h-bg": `var(--${color}-50)`,
  "--h-border": `var(--${color}-100)`,
  "--h-solid": `var(--${color}-400)`,
  "--h-ink": `var(--${color}-${color === "cyan" || color === "violet" ? "800" : "600"})`,
});

export const agentColors = (color) => ({
  bg: `var(--${color}-50)`,
  border: `var(--${color}-100)`,
  solid: `var(--${color}-400)`,
  ink: `var(--${color}-${color === "cyan" || color === "violet" ? "800" : "600"})`,
});

// Each feeling's colours, taken from the backend's own emotion → colour map
// (VISUAL_SUGGESTIONS in emotion_agent.py), so the picker previews the
// palette the AI will later recommend for that feeling.
// Backgrounds and text are mixed from the ring colour and the current theme
// (color-mix), so every card stays readable in both light and dark mode.
const emo = (ring) => ({
  bg: `color-mix(in srgb, ${ring} 14%, var(--surface))`,
  ring,
  text: `color-mix(in srgb, ${ring} 42%, var(--text-primary))`,
});
export const EMOTION_COLORS = {
  auto:       { bg: "color-mix(in srgb, #8B5CF6 14%, var(--surface))", ring: "#8B5CF6", text: "color-mix(in srgb, #8B5CF6 42%, var(--text-primary))" },
  joy:        emo("#E8A800"),
  excitement: emo("#F4511E"),
  trust:      emo("#2F6FDE"),
  confidence: emo("#7C3AED"),
  curiosity:  emo("#13A396"),
  relief:     emo("#3FA35F"),
  admiration: emo("#C99A1B"),
  neutral:    emo("#8A8A99"),
};
export const emotionColors = (e) => EMOTION_COLORS[String(e || "").toLowerCase()] || EMOTION_COLORS.auto;

// Ready-made examples so a first-time user can see a result in one click.
export const EXAMPLES = [
  {
    id: "lotion",
    label: "Herbal body lotion",
    emoji: "🧴",
    form: {
      product_name: "Spa Ceylon Lavender Neem Body Lotion",
      product_text: "Spa Ceylon Ayurveda Lavender Neem Body Lotion, a luxury herbal moisturiser made with natural ingredients that soothes and softens dry skin, 200ml.",
      category: "Beauty",
      price: 3200,
      target_audience: "Working women who care about natural skincare",
      features: "Ayurvedic herbs, all-day moisture, 200ml",
      target_emotion: "trust",
    },
    demo: { gender: "Female", age_range: "25 – 34 years", district: "Colombo", occupation: "Private sector employee", monthly_spending: "Rs. 60,001 – Rs. 100,000", culture_influence: "3" },
  },
  {
    id: "headphones",
    label: "Noise-cancelling headphones",
    emoji: "🎧",
    form: {
      product_name: "Sony WH-1000XM5 Headphones",
      product_text: "Sony WH-1000XM5 wireless noise-cancelling headphones with industry-leading sound, a 30-hour battery and quick charging for long workdays and travel.",
      category: "Electronics",
      price: 99000,
      target_audience: "Office workers and daily commuters",
      features: "Noise cancelling, 30-hour battery, quick charge",
      target_emotion: "excitement",
    },
    demo: { gender: "Male", age_range: "25 – 34 years", district: "Colombo", occupation: "Private sector employee", monthly_spending: "Rs. 100,001 – Rs. 150,000", culture_influence: "2" },
  },
  {
    id: "biscuits",
    label: "Chocolate biscuits",
    emoji: "🍪",
    form: {
      product_name: "Maliban Chocolate Cream Biscuits",
      product_text: "Maliban Chocolate Cream Biscuits, crispy sweet biscuits with a rich chocolate cream filling, in a family-size pack of three for sharing.",
      category: "Grocery",
      price: 450,
      target_audience: "Families with young children",
      features: "Rich chocolate cream, crispy, family pack",
      target_emotion: "joy",
    },
    demo: { gender: "Female", age_range: "35 – 44 years", district: "Kandy", occupation: "Government sector employee", monthly_spending: "Rs. 30,001 – Rs. 60,000", culture_influence: "4" },
  },
  {
    id: "babyoil",
    label: "Baby coconut oil",
    emoji: "🍼",
    form: {
      product_name: "Hemas Baby Care Coconut Oil",
      product_text: "Hemas Baby Care Coconut Oil, 100% pure and gentle on delicate skin, trusted by Sri Lankan mothers for over 30 years, 200ml bottle.",
      category: "Baby",
      price: 650,
      target_audience: "New and expecting mothers",
      features: "100% pure, gentle, trusted for 30 years",
      target_emotion: "trust",
    },
    demo: { gender: "Female", age_range: "25 – 34 years", district: "Gampaha", occupation: "Self-employed / Entrepreneur", monthly_spending: "Rs. 30,001 – Rs. 60,000", culture_influence: "4" },
  },
];
