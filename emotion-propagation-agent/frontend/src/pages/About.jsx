import { GitBranch, Layers, Target } from "lucide-react"

function InfoBlock({ icon: Icon, title, children }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <div className="text-sm font-semibold text-slate-900">{title}</div>
          <div className="mt-2 text-sm leading-6 text-slate-700">{children}</div>
        </div>
      </div>
    </div>
  )
}

export default function About() {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="text-base font-semibold text-slate-900">About This Research Component</div>
        <div className="mt-2 text-sm leading-6 text-slate-700">
          Component 2 implements an Emotion Propagation Agent for AI-generated neuro-marketing content. The system targets a
          desired consumer emotion, generates emotion-aligned marketing copy using structured templates, validates the
          emotional signal with a trained classifier, and collects user study ratings for evaluation.
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <InfoBlock icon={Target} title="Research Objective">
          Investigate how well AI-generated marketing messages can be guided toward a target emotion and how audiences
          perceive emotional alignment and persuasion in generated content.
        </InfoBlock>

        <InfoBlock icon={Layers} title="Theoretical Foundation: Emotional Contagion">
          Emotional contagion explains how emotions can spread between individuals through exposure to emotionally-charged
          cues. In marketing, emotion-aligned content can influence perception, engagement, and purchase intent.
        </InfoBlock>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <InfoBlock icon={GitBranch} title="Dataset Usage">
          GoEmotions (emotion classification), Amazon Product Reviews (product-review emotion analysis), and a custom User
          Study Dataset (evaluation ratings) are used to support training, analysis, and validation.
        </InfoBlock>

        <InfoBlock icon={Layers} title="Architecture & Evaluation">
          <div className="space-y-2">
            <div className="rounded-xl bg-slate-50 px-3 py-2">
              User Input → Emotion Target Selector → Message Generator → Emotion Classifier → Final Output
            </div>
            <div>
              Evaluation metrics: emotion strength, clarity, persuasiveness, trustworthiness, engagement interest, purchase
              interest.
            </div>
          </div>
        </InfoBlock>
      </div>
    </div>
  )
}
