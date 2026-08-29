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

export const CATEGORIES = [
  "Beauty", "Electronics", "Apparel", "Grocery",
  "Baby", "Pet Products", "Sports", "Home & Kitchen",
  "Automotive", "Industrial", "Unknown",
];
export const EMOTIONS = ["joy", "excitement", "trust", "confidence", "curiosity", "relief", "admiration", "neutral"];

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
