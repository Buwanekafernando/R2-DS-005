import { useMemo } from "react";
import { RotateCcw, Sparkles, Wand2 } from "lucide-react";

const productCategories = [
  "Baby",
  "Beauty",
  "Apparel",
  "Electronics",
  "Sports",
  "Pet",
  "Groceries",
];

const targetEmotions = [
  "joy",
  "excitement",
  "trust",
  "confidence",
  "curiosity",
  "optimism",
  "relief",
  "admiration",
  "neutral",
];

function inputClassName(hasError) {
  return [
    "w-full rounded-xl border bg-white px-3 py-2 text-sm shadow-sm outline-none transition",
    hasError
      ? "border-rose-300 focus:border-rose-400 focus:ring-2 focus:ring-rose-200"
      : "border-slate-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
  ].join(" ");
}

export default function ProductForm({
  form,
  setForm,
  onGenerate,
  onGenerateVariations,
  onClear,
  loading,
  onEmotionTouched,
}) {
  const errors = useMemo(() => {
    const next = {};
    if (!form.product_name?.trim()) next.product_name = "Required";
    if (!(form.category || form.product_category)?.trim())
      next.category = "Required";
    if (!form.target_audience?.trim()) next.target_audience = "Required";
    if (!(form.features || form.key_features)?.trim()) next.features = "Required";
    if (!form.target_emotion?.trim()) next.target_emotion = "Required";
    return next;
  }, [form]);

  function updateField(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (Object.keys(errors).length) return;
    onGenerate();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-semibold text-slate-900">
            Product Details
          </div>
          <div className="mt-1 text-sm text-slate-600">
            Enter product information, choose an emotion, and generate
            emotion-aligned content.
          </div>
        </div>
        <button
          type="button"
          onClick={onClear}
          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60"
          disabled={loading}
        >
          <RotateCcw className="h-4 w-4" />
          Clear
        </button>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="md:col-span-1">
          <label className="text-sm font-medium text-slate-800">
            Product Name
          </label>
          <input
            className={inputClassName(Boolean(errors.product_name))}
            value={form.product_name}
            onChange={(e) => updateField("product_name", e.target.value)}
            placeholder="e.g., SmartLearn AI"
          />
          {errors.product_name ? (
            <div className="mt-1 text-xs text-rose-600">
              {errors.product_name}
            </div>
          ) : null}
        </div>

        <div className="md:col-span-1">
          <label className="text-sm font-medium text-slate-800">
            Product Category
          </label>
          <select
            className={inputClassName(Boolean(errors.category))}
            value={form.category ?? form.product_category ?? ""}
            onChange={(e) => updateField("category", e.target.value)}
          >
            {productCategories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          {errors.category ? (
            <div className="mt-1 text-xs text-rose-600">{errors.category}</div>
          ) : null}
        </div>

        <div className="md:col-span-2">
          <label className="text-sm font-medium text-slate-800">
            Target Audience
          </label>
          <input
            className={inputClassName(Boolean(errors.target_audience))}
            value={form.target_audience}
            onChange={(e) => updateField("target_audience", e.target.value)}
            placeholder="e.g., young parents"
          />
          {errors.target_audience ? (
            <div className="mt-1 text-xs text-rose-600">
              {errors.target_audience}
            </div>
          ) : null}
        </div>

        <div className="md:col-span-2">
          <label className="text-sm font-medium text-slate-800">
            Features
          </label>
          <input
            className={inputClassName(Boolean(errors.features))}
            value={form.features ?? form.key_features ?? ""}
            onChange={(e) => updateField("features", e.target.value)}
            placeholder="e.g., bright skin, smooth texture, daily skincare support"
          />
          {errors.features ? (
            <div className="mt-1 text-xs text-rose-600">{errors.features}</div>
          ) : null}
        </div>

        <div className="md:col-span-2">
          <label className="text-sm font-medium text-slate-800">
            Target Emotion
          </label>
          <select
            className={inputClassName(Boolean(errors.target_emotion))}
            value={form.target_emotion}
            onChange={(e) => {
              onEmotionTouched?.();
              updateField("target_emotion", e.target.value);
            }}
          >
            {targetEmotions.map((e) => (
              <option key={e} value={e}>
                {e}
              </option>
            ))}
          </select>
          {errors.target_emotion ? (
            <div className="mt-1 text-xs text-rose-600">
              {errors.target_emotion}
            </div>
          ) : null}
        </div>
      </div>

      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-95 disabled:opacity-60"
        >
          <Sparkles className="h-4 w-4" />
          Generate Message
        </button>

        <button
          type="button"
          disabled={loading || Object.keys(errors).length > 0}
          onClick={onGenerateVariations}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50 disabled:opacity-60"
        >
          <Wand2 className="h-4 w-4" />
          Generate Multiple Variations
        </button>
      </div>
    </form>
  );
}

export { productCategories, targetEmotions };
