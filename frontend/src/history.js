const HISTORY_KEY = "nm_strategy_history";
const MAX_HISTORY = 25;

export function getHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveToHistory(result) {
  try {
    const history = getHistory();
    const entry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      savedAt: new Date().toISOString(),
      productName: result.product || "Untitled product",
      result,
    };
    const updated = [entry, ...history].slice(0, MAX_HISTORY);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    return entry;
  } catch {
    return null; // storage full/unavailable — not critical, fail silently
  }
}

export function deleteFromHistory(id) {
  try {
    const updated = getHistory().filter((e) => e.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  } catch {
    // ignore
  }
}

export function clearHistory() {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch {
    // ignore
  }
}
