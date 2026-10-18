// Plain-language meanings for every technical word shown in the app.
// Used by <Term> and <G> (components/Term.jsx) to show an explanation when
// someone hovers, focuses (Tab) or taps the word. Each entry: the words that
// trigger it (match, case-insensitive) and a one-or-two-sentence meaning that
// needs no marketing or AI background.
export const GLOSSARY = [
  { match: ["System 1"], tip: "Fast, gut-feeling decisions. Think of grabbing a treat at the till without comparing anything." },
  { match: ["System 2"], tip: "Slow, careful decisions. Think of comparing laptops, reading reviews and checking the price first." },
  { match: ["Dual-System Reasoning"], tip: "A psychology idea: people decide in two ways, quickly by feeling (System 1) or slowly by thinking it through (System 2). We work out which one fits your product." },
  { match: ["cognitive mode"], tip: "Whether your customers mostly decide with their heart (System 1) or their head (System 2)." },
  { match: ["Buying Psychology"], tip: "Why people buy: gut feeling or careful comparison. This helper works that out for your product." },
  { match: ["Emotion Propagation", "Emotional Appeal"], tip: "How a feeling in your wording (trust, joy, excitement) spreads to the reader and nudges them to act." },
  { match: ["Scarcity Optimization", "Urgency & Scarcity"], tip: "Choosing how much “limited stock” or “act now” wording to use, enough to motivate people without feeling pushy." },
  { match: ["Loss Framing", "Loss-Framed", "loss-framed"], tip: "Describing what people lose by waiting (“don’t miss out”) instead of what they gain. It tends to motivate more, so use it gently." },
  { match: ["urgency"], tip: "Wording that encourages people to act soon, such as “today only” or “last few left”." },
  { match: ["scarcity"], tip: "Making it clear supply or time is limited, such as “only 5 left”. People value what is hard to get." },
  { match: ["intensity"], tip: "How strong the pressure is: low is a gentle nudge, medium is a clear push, high is “only 2 left!”." },
  { match: ["trust score", "trust status"], tip: "How believable the urgency wording feels. A low score means it may sound pushy or fake for this kind of product." },
  { match: ["sentiment score", "sentiment"], tip: "How positive or negative the words sound, from −1 (very negative) to +1 (very positive)." },
  { match: ["warmth"], tip: "How friendly and positive the wording sounds. It is the sentiment score in everyday words." },
  { match: ["tone"], tip: "The mood of your wording, for example friendly, serious or pushy." },
  { match: ["FOMO"], tip: "Fear Of Missing Out. The worry that others will get something good while you wait." },
  { match: ["feeling check"], tip: "After writing your message, our emotion AI reads it back to confirm it really sounds like the feeling you picked. If not, it rewrites it (up to 3 tries)." },
  { match: ["RoBERTa"], tip: "An AI model that reads text and tells which feeling it expresses. Ours was trained on thousands of real comments." },
  { match: ["VADER"], tip: "A simple, well-known tool that scores how positive or negative a piece of text sounds." },
  { match: ["Grok", "Groq", "LLM", "language model"], tip: "A large AI language model, the kind of AI that writes text. It drafts your marketing messages." },
  { match: ["confidence score", "confidence percentage"], tip: "How sure the AI is about its own decision. It is not a score for how good your message is." },
  { match: ["mode alignment", "style fit"], tip: "How closely the wording matches the style (emotional or fact-based) it is meant to have." },
  { match: ["suitability score", "suitability"], tip: "How well urgency wording suits this kind of product, as a percentage." },
  { match: ["demographic", "demographics"], tip: "Basic facts about your typical customer, such as age group, area and income. They help the AI judge how they buy." },
  { match: ["cultural influence", "Hofstede"], tip: "How much family, friends and local traditions shape what people buy. Based on a well-known research scale (Hofstede)." },
  { match: ["call to action", "CTA"], tip: "The line that tells people what to do next, such as “Order today” or “Visit our shop”." },
  { match: ["channel", "channels"], tip: "Where you post your message: Instagram, Facebook, WhatsApp, your product listing or email." },
  { match: ["conversion", "conversions"], tip: "When someone takes the action you wanted, such as buying or sending an enquiry." },
  { match: ["engagement"], tip: "How much people react to your post: likes, comments, shares and clicks." },
  { match: ["natural-tone", "natural tone"], tip: "A version rewritten to sound like a real person talking, with plain words and an easy rhythm." },
  { match: ["batch"], tip: "Doing many products in one go, instead of one at a time." },
  { match: ["JSON", "raw data"], tip: "The computer-readable version of the results. It is useful for developers; you can ignore it." },
  { match: ["API", "backend", "server"], tip: "The behind-the-scenes program that runs the AI. It has to be running for messages to be created." },
  { match: ["target emotion", "emotion detected"], tip: "The feeling you want people to have (target), and the feeling our AI actually found in the writing (detected)." },
  { match: ["recommended copy", "copy"], tip: "“Copy” just means the marketing words: the text in your ad, post or listing." },
  { match: ["headline"], tip: "The first, biggest line that makes people stop and read." },
];

// Build one lookup: lower-case phrase -> tip, plus a regex that finds them
// (longest phrases first so “trust score” wins over “trust”).
const LOOKUP = new Map();
GLOSSARY.forEach((g) => g.match.forEach((m) => LOOKUP.set(m.toLowerCase(), g.tip)));
const PHRASES = [...LOOKUP.keys()].sort((a, b) => b.length - a.length);
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
export const TERM_REGEX = new RegExp(`(?<![\\w-])(${PHRASES.map(esc).join("|")})(?![\\w-])`, "gi");
export const tipFor = (word) => LOOKUP.get(String(word).toLowerCase());
