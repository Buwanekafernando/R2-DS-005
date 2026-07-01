import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts"

function formatScore(value) {
  const v = Number(value)
  if (Number.isNaN(v)) return ""
  return v.toFixed(2)
}

export default function EmotionPredictionChart({ predictions, height = 260 }) {
  const data = (predictions || []).map((p) => ({
    emotion: p.emotion,
    score: Number(p.score),
  }))

  if (!data.length) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="text-sm font-semibold text-slate-900">Emotion Predictions</div>
        <div className="mt-1 text-sm text-slate-600">No predictions available.</div>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm font-semibold text-slate-900">Emotion Predictions</div>
      <div className="mt-4" style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="emotion" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v) => formatScore(v)} />
            <Bar dataKey="score" fill="#6366F1" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 text-xs text-slate-500">Scores reflect the model's confidence (0–1).</div>
    </div>
  )
}
