import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";

import {
  generateMessage,
  generateVariations,
  healthCheck,
} from "../api/emotionApi";
import EmotionPredictionChart from "../components/EmotionPredictionChart";
import GeneratedMessageCard from "../components/GeneratedMessageCard";
import ProductForm from "../components/ProductForm";

const recommendedEmotionByCategory = {
  Baby: ["trust", "relief", "joy"],
  Beauty: ["confidence", "admiration", "joy"],
  Apparel: ["confidence", "admiration", "excitement"],
  Electronics: ["excitement", "trust", "curiosity"],
  Sports: ["excitement", "confidence", "optimism"],
  Pet: ["joy", "trust", "relief"],
  Groceries: ["trust", "relief", "joy"],
};

function getRecommendedEmotion(category) {
  const list =
    recommendedEmotionByCategory[category] ||
    recommendedEmotionByCategory.Beauty;
  return list[0] || "confidence";
}

function getErrorMessage(err) {
  return (
    err?.response?.data?.error ||
    "Backend API is not available. Please start Flask server on port 5000."
  );
}

export default function Generate() {
  const [backendOnline, setBackendOnline] = useState(true);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [modelWarning, setModelWarning] = useState("");
  const [emotionTouched, setEmotionTouched] = useState(false);

  const [form, setForm] = useState({
    product_name: "",
    category: "Beauty",
    target_audience: "",
    features: "",
    target_emotion: "confidence",
  });

  const [result, setResult] = useState(null);
  const [variations, setVariations] = useState([]);

  useEffect(() => {
    healthCheck()
      .then((data) => {
        setBackendOnline(true);
        setModelWarning(data.model_warning || "");
      })
      .catch(() => setBackendOnline(false));
  }, []);

  useEffect(() => {
    if (emotionTouched) return;
    const recommended = getRecommendedEmotion(form.category);
    if (form.target_emotion === recommended) return;
    setForm((prev) => ({ ...prev, target_emotion: recommended }));
  }, [form.category, form.target_emotion, emotionTouched]);

  const payload = useMemo(
    () => ({
      product_name: form.product_name.trim(),
      category: form.category,
      target_audience: form.target_audience.trim(),
      features: form.features.trim(),
      target_emotion: form.target_emotion,
    }),
    [form],
  );

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
      setModelWarning(data.warning || modelWarning);
      setSuccessMsg("Marketing message generated successfully.");
    } catch (err) {
      setBackendOnline(!err?.response);
      setErrorMsg(getErrorMessage(err));
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
        category: payload.category,
        target_audience: payload.target_audience,
        features: payload.features,
        target_emotions: ["joy", "excitement", "trust", "confidence"],
      });
      setVariations(data.variations || []);
      setBackendOnline(true);
      setSuccessMsg("Variations generated successfully.");
    } catch (err) {
      setBackendOnline(!err?.response);
      setErrorMsg(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  function handleClearForm() {
    setForm({
      product_name: "",
      category: "Beauty",
      target_audience: "",
      features: "",
      target_emotion: "confidence",
    });
    setEmotionTouched(false);
    setResult(null);
    setVariations([]);
    clearMessages();
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
            {variations.map((variation) => (
              <GeneratedMessageCard
                key={`${variation.target_emotion}-${variation.generated_message}`}
                result={{
                  ...variation,
                  product_name: payload.product_name,
                  category: payload.category,
                  target_audience: payload.target_audience,
                  features: payload.features,
                }}
              />
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}