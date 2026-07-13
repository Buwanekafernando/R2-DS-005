export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-2 px-4 py-6 text-sm text-slate-600 md:flex-row md:items-center md:justify-between">
        <div>Emotion Propagation Agent • Neuro-Marketing Research Prototype</div>
        <div className="text-slate-500">Flask API: http://localhost:5000 • React UI: http://localhost:5173</div>
      </div>
    </footer>
  )
}
