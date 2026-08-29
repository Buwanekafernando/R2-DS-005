import { useEffect, useState } from "react";

// Persists form state to localStorage so it survives an accidental page
// refresh. Not used for anything sensitive — just product/form inputs the
// user typed, so they don't lose work.
export function usePersistedState(key, initialValue) {
  const [state, setState] = useState(() => {
    try {
      const saved = localStorage.getItem(key);
      return saved !== null ? JSON.parse(saved) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch {
      // storage full or unavailable — fail silently, not critical
    }
  }, [key, state]);

  return [state, setState];
}

export function clearPersisted(key) {
  try {
    localStorage.removeItem(key);
  } catch {
    // ignore
  }
}
