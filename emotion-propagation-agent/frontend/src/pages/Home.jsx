import { Link } from "react-router-dom"
import { BarChart3, CheckCircle2, FlaskConical, Sparkles, Wand2 } from "lucide-react"

function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex items-start gap-3">
        <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <div className="text-sm font-semibold text-slate-900">{title}</div>
          <div className="mt-1 text-sm text-slate-600">{description}</div>
        </div>
      </div>
    </div>
  )
}

export default function Home() {
  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br from-blue-50 via-white to-teal-50 p-8 shadow-sm">
        <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-gradient-to-br from-purple-300/40 to-blue-300/40 blur-2xl" />
        <div className="absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-gradient-to-br from-teal-300/30 to-blue-300/30 blur-2xl" />

        <div className="relative max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/70 px-3 py-1 text-xs font-semibold text-slate-700">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            Component 2 • Emotion Propagation Agent
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
            Emotion Propagation Agent
          </h1>
          <p className="mt-3 text-base text-slate-600">
            AI-powered emotional marketing strategy generation for neuro-marketing research: target an emotion, generate aligned content, validate it with a trained classifier, and collect user study ratings.
          </p>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link
              to="/generate"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:opacity-95"
            >
              <Wand2 className="h-4 w-4" />
              Generate Marketing Message
            </Link>
            <Link
              to="/validate"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 shadow-sm transition hover:bg-slate-50"
            >
              <FlaskConical className="h-4 w-4 text-indigo-600" />
              Validate Emotion
            </Link>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <div className="text-sm font-semibold text-slate-900">Research Features</div>
            <div className="mt-1 text-sm text-slate-600">End-to-end flow for message generation, validation, and evaluation.</div>
          </div>
          <Link to="/dashboard" className="hidden text-sm font-semibold text-indigo-700 hover:text-indigo-800 sm:inline-flex">
            View Dashboard →
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <FeatureCard
            icon={CheckCircle2}
            title="Emotion Target Selection"
            description="Select a target emotion (e.g., trust, excitement) with category-informed defaults."
          />
          <FeatureCard
            icon={Wand2}
            title="Marketing Message Generation"
            description="Generate professional, template-based marketing copy aligned to the selected emotion."
          />
          <FeatureCard
            icon={FlaskConical}
            title="Emotion Validation"
            description="Validate the generated text using your trained TF-IDF + Logistic Regression classifier."
          />
          <FeatureCard
            icon={BarChart3}
            title="User Study Evaluation"
            description="Collect participant ratings and analyze performance across target emotions."
          />
        </div>
      </section>
    </div>
  )
}
