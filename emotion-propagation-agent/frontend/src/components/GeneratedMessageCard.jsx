import { useMemo, useState } from "react"
import { Check, Copy, Palette, Quote, Sparkles } from "lucide-react"

function badgeClass(emotion) {
  const map = {
    joy: "bg-yellow-50 text-yellow-700 border-yellow-200",
    excitement: "bg-rose-50 text-rose-700 border-rose-200",
    trust: "bg-blue-50 text-blue-700 border-blue-200",
    confidence: "bg-indigo-50 text-indigo-700 border-indigo-200",
    curiosity: "bg-teal-50 text-teal-700 border-teal-200",
    optimism: "bg-emerald-50 text-emerald-700 border-emerald-200",
    relief: "bg-lime-50 text-lime-700 border-lime-200",
    admiration: "bg-amber-50 text-amber-700 border-amber-200",
    neutral: "bg-slate-50 text-slate-700 border-slate-200",
  }
  return map[emotion] || map.neutral
}

export default function GeneratedMessageCard({ result }) {
  const [copied, setCopied] = useState(false)

  const message = result?.generated_message || ""
  const emotion = (result?.target_emotion || "neutral").toLowerCase()
  const cta = result?.cta || ""
  const tone = result?.tone || ""
  const visual = result?.visual_suggestions || null
  const warning = result?.warning || null

  const colorsText = useMemo(() => {
    const colors = visual?.color_palette || []
    if (!Array.isArray(colors) || !colors.length) return ""
    return colors.join(", ")
  }, [visual])

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(message)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch {
      setCopied(false)
    }
  }

  if (!result) return null

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
        <div className="flex items-center gap-2">
          <div className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-sm">
            <Quote className="h-4 w-4" />
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-900">Generated Marketing Message</div>
            <div className="mt-0.5 text-xs text-slate-500">Template-based generation + optional model validation.</div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={["inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold", badgeClass(emotion)].join(" ")}>
            <Sparkles className="h-3.5 w-3.5" />
            Target: {emotion}
          </span>
          <button
            type="button"
            onClick={copyToClipboard}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-600" /> : <Copy className="h-4 w-4" />}
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>

      {warning ? (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">{warning}</div>
      ) : null}

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-900">
        <div className="whitespace-pre-wrap text-sm leading-6">{message}</div>
        {cta ? (
          <div className="mt-3 inline-flex rounded-xl bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm">
            CTA: <span className="ml-2 font-medium text-slate-700">{cta}</span>
          </div>
        ) : null}
        {tone ? <div className="mt-2 text-xs text-slate-600">Tone: {tone}</div> : null}
      </div>

      {visual ? (
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <Palette className="h-4 w-4 text-indigo-600" />
              Color Palette
            </div>
            <div className="mt-2 text-sm text-slate-700">{colorsText || "—"}</div>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:col-span-2">
            <div className="text-sm font-semibold text-slate-900">Visual Suggestions</div>
            <div className="mt-2 grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
              <div className="rounded-xl bg-slate-50 px-3 py-2">
                <div className="text-xs font-semibold text-slate-500">Image Style</div>
                <div className="mt-1">{visual.image_style || "—"}</div>
              </div>
              <div className="rounded-xl bg-slate-50 px-3 py-2">
                <div className="text-xs font-semibold text-slate-500">Layout Mood</div>
                <div className="mt-1">{visual.layout_mood || "—"}</div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
