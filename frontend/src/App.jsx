import Integrate from "./Integrate.jsx";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-lg font-semibold">NeuroMark — Integrated System</h1>
        <p className="text-xs text-slate-500">Emotion Propagation + Loss Framing</p>
      </header>
      <Integrate />
    </div>
  );
}
