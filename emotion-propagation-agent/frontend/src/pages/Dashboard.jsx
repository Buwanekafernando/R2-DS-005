import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, BarChart3, Loader2 } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import {
  getUserStudyResponses,
  getUserStudySummary,
  healthCheck,
} from "../api/emotionApi";

function StatCard({ label, value, sub }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
      {sub ? <div className="mt-1 text-sm text-slate-600">{sub}</div> : null}
    </div>
  );
}

function MiniBarChart({ title, dataKey, data }) {
  if (!data?.length) return null;
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm font-semibold text-slate-900">{title}</div>
      <div className="mt-4" style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <BarChart
            data={data}
            margin={{ top: 8, right: 16, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="target_emotion" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 5]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey={dataKey} fill="#0EA5E9" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 text-xs text-slate-500">
        Averages computed from user study CSV responses.
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [backendOnline, setBackendOnline] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [summary, setSummary] = useState(null);
  const [responses, setResponses] = useState([]);

  useEffect(() => {
    healthCheck()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  useEffect(() => {
    setLoading(true);
    setErrorMsg("");
    Promise.all([getUserStudySummary(), getUserStudyResponses()])
      .then(([s, r]) => {
        setSummary(s);
        setResponses(r.responses || []);
        setBackendOnline(true);
      })
      .catch(() => {
        setBackendOnline(false);
        setErrorMsg(
          "Backend API is not available. Please start Flask server on port 5000.",
        );
      })
      .finally(() => setLoading(false));
  }, []);

  const hasData = Boolean(summary?.total_responses > 0);

  const averagesOverall = useMemo(() => {
    if (!responses?.length)
      return { engagement: null, persuasiveness: null, trustworthiness: null };
    const nums = (key) =>
      responses.map((r) => Number(r[key])).filter((v) => Number.isFinite(v));
    function mean(arr) {
      if (!arr.length) return null;
      return arr.reduce((a, b) => a + b, 0) / arr.length;
    }
    return {
      engagement: mean(nums("engagement_interest")),
      persuasiveness: mean(nums("persuasiveness")),
      trustworthiness: mean(nums("trustworthiness")),
    };
  }, [responses]);

  const chartData = useMemo(() => {
    return (summary?.summary || []).map((row) => ({
      target_emotion: row.target_emotion,
      average_engagement_interest: Number(row.average_engagement_interest),
      average_persuasiveness: Number(row.average_persuasiveness),
      average_trustworthiness: Number(row.average_trustworthiness),
    }));
  }, [summary]);

  return (
    <div className="space-y-6">
      {!backendOnline ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          Backend API is not available. Please start Flask server on port 5000.
        </div>
      ) : null}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <BarChart3 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-base font-semibold text-slate-900">
              User Study Dashboard
            </div>
            <div className="mt-1 text-sm text-slate-600">
              Summarized performance across target emotions and raw response
              table.
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-700 shadow-sm">
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Loading dashboard...
        </div>
      ) : null}

      {errorMsg ? (
        <div className="flex items-start gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          <AlertTriangle className="mt-0.5 h-4 w-4" />
          <div>{errorMsg}</div>
        </div>
      ) : null}

      {!loading && !hasData ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-700 shadow-sm">
          No user study responses yet. Submit responses from the evaluation
          form.
        </div>
      ) : null}

      {hasData ? (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard label="Total Responses" value={summary.total_responses} />
            <StatCard
              label="Best Performing Emotion"
              value={summary.best_emotion || "—"}
            />
            <StatCard
              label="Average Engagement"
              value={
                averagesOverall.engagement
                  ? averagesOverall.engagement.toFixed(2)
                  : "—"
              }
              sub="Overall mean of engagement_interest (1–5)"
            />
            <StatCard
              label="Average Persuasiveness"
              value={
                averagesOverall.persuasiveness
                  ? averagesOverall.persuasiveness.toFixed(2)
                  : "—"
              }
              sub="Overall mean of persuasiveness (1–5)"
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <MiniBarChart
              title="Engagement by Emotion"
              dataKey="average_engagement_interest"
              data={chartData}
            />
            <MiniBarChart
              title="Persuasiveness by Emotion"
              dataKey="average_persuasiveness"
              data={chartData}
            />
            <MiniBarChart
              title="Trustworthiness by Emotion"
              dataKey="average_trustworthiness"
              data={chartData}
            />
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-sm font-semibold text-slate-900">
              User Study Response Table
            </div>
            <div className="mt-4 overflow-auto rounded-2xl border border-slate-200">
              <table className="min-w-[900px] w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs font-semibold text-slate-600">
                  <tr>
                    <th className="px-4 py-3">participant_id</th>
                    <th className="px-4 py-3">product_name</th>
                    <th className="px-4 py-3">target_emotion</th>
                    <th className="px-4 py-3">perceived_emotion</th>
                    <th className="px-4 py-3">emotion_strength</th>
                    <th className="px-4 py-3">message_clarity</th>
                    <th className="px-4 py-3">persuasiveness</th>
                    <th className="px-4 py-3">trustworthiness</th>
                    <th className="px-4 py-3">engagement_interest</th>
                    <th className="px-4 py-3">purchase_interest</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {responses.map((r, idx) => (
                    <tr
                      key={`${r.participant_id}-${idx}`}
                      className="hover:bg-slate-50"
                    >
                      <td className="px-4 py-3">{r.participant_id}</td>
                      <td className="px-4 py-3">{r.product_name}</td>
                      <td className="px-4 py-3">{r.target_emotion}</td>
                      <td className="px-4 py-3">{r.perceived_emotion}</td>
                      <td className="px-4 py-3">{r.emotion_strength}</td>
                      <td className="px-4 py-3">{r.message_clarity}</td>
                      <td className="px-4 py-3">{r.persuasiveness}</td>
                      <td className="px-4 py-3">{r.trustworthiness}</td>
                      <td className="px-4 py-3">{r.engagement_interest}</td>
                      <td className="px-4 py-3">{r.purchase_interest}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-2 text-xs text-slate-500">
              Comments are stored in CSV and can be analyzed offline.
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
