import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, FlaskConical, Loader2 } from "lucide-react";

import { healthCheck, predictEmotion } from "../api/emotionApi";
import EmotionPredictionChart from "../components/EmotionPredictionChart";

export default function Validate() {
  const [backendOnline, setBackendOnline] = useState(true);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [modelWarning, setModelWarning] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    healthCheck()
      .then((data) => {
        setBackendOnline(true);
        setModelWarning(data.model_warning || "");
      })
      .catch(() => setBackendOnline(false));
  }, []);

  const mainEmotion = useMemo(() => {
    return result?.top_emotion || null;
  }, [result]);

  async function handleAnalyze() {
    setErrorMsg("");
    setLoading(true);
    setResult(null);
    try {
      const data = await predictEmotion(text);
      setResult(data);
      setBackendOnline(true);
      setModelWarning(data.warning || modelWarning);
    } catch (err) {
      setBackendOnline(!err?.response);
      setErrorMsg(
        err?.response?.data?.error ||
          "Backend API is not available. Please start Flask server on port 5000.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {!backendOnline ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          Backend API is not available. Please start Flask server on port 5000.
        </div>
      ) : null}

      {modelWarning ? (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {modelWarning}
        </div>
      ) : null}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <FlaskConical className="h-5 w-5" />
          </div>
          <div>
            <div className="text-base font-semibold text-slate-900">
              Emotion Validation
            </div>
            <div className="mt-1 text-sm text-slate-600">
              Analyze any marketing message and view the top predicted emotions.
            </div>
          </div>
        </div>

        <div className="mt-5">
          <label className="text-sm font-medium text-slate-800">
            Marketing Text
          </label>
          <textarea
            className="mt-1 h-36 w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or type your marketing content here..."
          />
        </div>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:opacity-95 disabled:opacity-60"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Analyze Emotion
          </button>
          <button
            type="button"
            onClick={() => {
              setText("");
              setResult(null);
              setErrorMsg("");
            }}
            className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 shadow-sm transition hover:bg-slate-50"
          >
            Clear
          </button>
        </div>

        {errorMsg ? (
          <div className="mt-4 flex items-start gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            <AlertTriangle className="mt-0.5 h-4 w-4" />
            <div>{errorMsg}</div>
          </div>
        ) : null}
      </div>

      {result ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <EmotionPredictionChart predictions={result.predictions || []} />
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-semibold text-slate-900">
              Main Detected Emotion
            </div>
            <div className="mt-2 text-2xl font-semibold text-slate-900">
              {mainEmotion || "—"}
            </div>
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              <div className="text-sm font-semibold text-slate-900">
                Research Note
              </div>
              <div className="mt-2 leading-6">
                The RoBERTa validator scores the message across the project
                emotion labels and returns the top detected emotion. In the full
                generation loop, this result is compared with the selected
                target emotion to decide whether the content should be accepted
                or regenerated.
              </div>
            </div>
            {result.warning ? (
              <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                {result.warning}
              </div>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
