import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("NeuroMark UI crashed:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ maxWidth: 600, margin: "80px auto", padding: 24, fontFamily: "DM Sans, sans-serif" }}>
          <div style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: 22, marginBottom: 10 }}>
            Something went wrong
          </div>
          <p style={{ color: "#6B6860", fontSize: 14, marginBottom: 16, lineHeight: 1.6 }}>
            The page hit an unexpected error while rendering. Your backend request may have
            succeeded — this is a display bug, not necessarily a lost result. Reloading usually
            clears it.
          </p>
          <pre style={{ background: "#1A1916", color: "#E8E6E0", padding: 12, borderRadius: 8, fontSize: 12, overflowX: "auto", marginBottom: 16 }}>
            {this.state.error.message}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{ background: "#1A1916", color: "#fff", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 600, cursor: "pointer" }}
          >
            Reload page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
