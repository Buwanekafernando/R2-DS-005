import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";

import {
  generateMessage,
  generateVariations,
  healthCheck,
  submitUserStudy,
} from "../api/emotionApi";
import EmotionPredictionChart from "../components/EmotionPredictionChart";
import GeneratedMessageCard from "../components/GeneratedMessageCard";
import ProductForm from "../components/ProductForm";
import UserStudyForm from "../components/UserStudyForm";

function parseFeatures(text) {
  return String(text || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

const recommendedEmotionByCategory = {
  general: ["joy", "trust", "excitement"],
  fashion: ["confidence", "excitement", "admiration"],
  beauty: ["confidence", "joy", "admiration"],
  education: ["optimism", "confidence", "curiosity"],
  technology: ["excitement", "trust", "curiosity"],
  healthcare: ["trust", "relief", "confidence"],
  fitness: ["excitement", "confidence", "optimism"],
  food: ["joy", "relief", "trust"],
  travel: ["excitement", "joy", "curiosity"],
  finance: ["trust", "confidence", "relief"],
  insurance: ["trust", "relief", "confidence"],
};

function getRecommendedEmotion(category) {
  const key = String(category || "general").toLowerCase();
  const list =
    recommendedEmotionByCategory[key] || recommendedEmotionByCategory.general;
  return list[0] || "joy";
}

export default function Generate() {
  const [backendOnline, setBackendOnline] = useState(true);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [emotionTouched, setEmotionTouched] = useState(false);

  const [form, setForm] = useState({
    product_name: "",
    product_category: "general",
    target_audience: "",
    key_features: "",
    target_emotion: "joy",
  });

  const [result, setResult] = useState(null);
  const [variations, setVariations] = useState([]);

  useEffect(() => {
    healthCheck()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  useEffect(() => {
    if (emotionTouched) return;
    const recommended = getRecommendedEmotion(form.product_category);
    if (form.target_emotion === recommended) return;
    setForm((prev) => ({ ...prev, target_emotion: recommended }));
  }, [form.product_category, form.target_emotion, emotionTouched]);

  const payload = useMemo(() => {
    return {
      product_name: form.product_name.trim(),
      product_category: form.product_category,
      target_audience: form.target_audience.trim(),
      key_features: parseFeatures(form.key_features),
      target_emotion: form.target_emotion,
    };
  }, [form]);

  function clearMessages() {
    setSuccessMsg("");
    setErrorMsg("");
  }

  async function handleGenerate() {
    clearMessages();
    setLoading(true);
    setVariations([]);
    try {
      const data = await generateMessage(payload);
      setResult(data);
      setBackendOnline(true);
      setSuccessMsg("Marketing message generated successfully.");
    } catch (err) {
      setBackendOnline(false);
      setErrorMsg(
        "Backend API is not available. Please start Flask server on port 5000.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateVariations() {
    clearMessages();
    setLoading(true);
    setResult(null);
    try {
      const data = await generateVariations({
        product_name: payload.product_name,
        product_category: payload.product_category,
        target_audience: payload.target_audience,
        key_features: payload.key_features,
        target_emotions: ["joy", "excitement", "trust", "confidence"],
      });
      setVariations(data.variations || []);
      setBackendOnline(true);
      setSuccessMsg("Variations generated successfully.");
    } catch (err) {
      setBackendOnline(false);
      setErrorMsg(
        "Backend API is not available. Please start Flask server on port 5000.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleClearForm() {
    setForm({
      product_name: "",
      product_category: "general",
      target_audience: "",
      key_features: "",
      target_emotion: "joy",
    });
    setEmotionTouched(false);
    setResult(null);
    setVariations([]);
    clearMessages();
  }

  async function handleSubmitUserStudy(studyPayload) {
    clearMessages();
    setLoading(true);
    try {
      await submitUserStudy(studyPayload);
      setBackendOnline(true);
      setSuccessMsg("User study response saved successfully.");
    } catch (err) {
      setBackendOnline(false);
      setErrorMsg(
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

      {successMsg ? (
        <div className="flex items-start gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          <CheckCircle2 className="mt-0.5 h-4 w-4" />
          <div>{successMsg}</div>
        </div>
      ) : null}

      {errorMsg ? (
        <div className="flex items-start gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          <AlertTriangle className="mt-0.5 h-4 w-4" />
          <div>{errorMsg}</div>
        </div>
      ) : null}

      <ProductForm
        form={form}
        setForm={setForm}
        onGenerate={handleGenerate}
        onGenerateVariations={handleGenerateVariations}
        onClear={handleClearForm}
        loading={loading}
        onEmotionTouched={() => setEmotionTouched(true)}
      />

      {loading ? (
        <div className="flex items-center justify-center rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-700 shadow-sm">
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Processing...
        </div>
      ) : null}

      {result ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-6">
            <GeneratedMessageCard result={result} />
            
          </div>
          <div className="space-y-6">
            <EmotionPredictionChart
              predictions={result.emotion_predictions || []}
            />
          </div>
        </div>
      ) : null}

      {variations?.length ? (
        <div className="space-y-4">
          <div className="text-base font-semibold text-slate-900">
            Generated Variations
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {variations.map((v) => (
              <div
                key={v.target_emotion}
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div className="text-sm font-semibold text-slate-900">
                  Target: {v.target_emotion}
                </div>
                <div className="mt-1 text-xs text-slate-500">
                  Tone: {v.tone || "—"}
                </div>
                {v.warning ? (
                  <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                    {v.warning}
                  </div>
                ) : null}
                <div className="mt-3 whitespace-pre-wrap rounded-2xl bg-slate-50 p-4 text-sm text-slate-900">
                  {v.generated_message}
                </div>
                <div className="mt-3 text-sm font-semibold text-slate-900">
                  CTA:{" "}
                  <span className="font-medium text-slate-700">
                    {v.cta || "—"}
                  </span>
                </div>
                <div className="mt-4">
                  <EmotionPredictionChart
                    predictions={v.emotion_predictions || []}
                    height={220}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
