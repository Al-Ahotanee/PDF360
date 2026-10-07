"use client";

import { useState } from "react";
import { AlertCircle } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { apiClient } from "@/lib/api/client";

function useAIAction<TReq extends object>(path: string) {
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function run(body: TReq) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const { data } = await apiClient.post(path, body);
      setResult(data.result ?? JSON.stringify(data));
    } catch (err: any) {
      if (err?.response?.status === 501) {
        setError("AI features aren't configured yet — no provider is set up for this workspace.");
      } else {
        setError("Something went wrong running this AI action.");
      }
    } finally {
      setLoading(false);
    }
  }

  return { run, result, error, loading };
}

function ResultOrError({ result, error }: { result: string | null; error: string | null }) {
  if (error) {
    return (
      <div className="mt-4 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300">
        <AlertCircle size={16} className="mt-0.5 shrink-0" />
        {error}
      </div>
    );
  }
  if (result) {
    return (
      <div className="mt-4 whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-ink dark:border-slate-800 dark:bg-ink/40 dark:text-slate-200">
        {result}
      </div>
    );
  }
  return null;
}

export default function AIToolsPage() {
  const [summarizeFile, setSummarizeFile] = useState("");
  const summarize = useAIAction<{ file_id: string }>("/ai/summarize");

  const [askFile, setAskFile] = useState("");
  const [question, setQuestion] = useState("");
  const ask = useAIAction<{ file_id: string; question: string }>("/ai/ask");

  return (
    <>
      <Topbar title="AI Tools" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Summarize" description="Get a quick summary of a document's contents.">
          <FileSelect value={summarizeFile} onChange={(v) => setSummarizeFile(v as string)} label="File to summarize" />
          <div className="mt-3">
            <PrimaryButton onClick={() => summarize.run({ file_id: summarizeFile })} disabled={!summarizeFile || summarize.loading}>
              {summarize.loading ? "Summarizing…" : "Summarize"}
            </PrimaryButton>
          </div>
          <ResultOrError result={summarize.result} error={summarize.error} />
        </ToolCard>

        <ToolCard title="Ask a question" description="Ask something specific about a document's contents.">
          <FileSelect value={askFile} onChange={(v) => setAskFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Your question</span>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What is the total invoice amount?"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={() => ask.run({ file_id: askFile, question })} disabled={!askFile || !question || ask.loading}>
              {ask.loading ? "Thinking…" : "Ask"}
            </PrimaryButton>
          </div>
          <ResultOrError result={ask.result} error={ask.error} />
        </ToolCard>
      </main>
    </>
  );
}
