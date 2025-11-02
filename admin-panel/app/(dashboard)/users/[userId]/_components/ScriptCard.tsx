'use client';

import { Copy, FileText, FileType } from 'lucide-react';

type ScriptGeneration = {
  uuid: string;
  title: string;
  type: 'script' | 'outline';
  status: 'draft' | 'generated' | 'saved';
  status_display: string;
  word_count: number | null;
  estimated_duration: number | null;
  created: string;
  modified: string;
  is_published: boolean | null;
  version: number;
};

type ScriptCardProps = {
  script: ScriptGeneration;
  onCopy: (text: string) => void;
};

export default function ScriptCard({ script, onCopy }: ScriptCardProps) {
  const statusColors = {
    draft: 'bg-gray-500/20 text-gray-300',
    generated: 'bg-green-500/20 text-green-300',
    saved: 'bg-blue-500/20 text-blue-300',
  };

  const typeColors = {
    outline: 'bg-purple-500/20 text-purple-300',
    script: 'bg-orange-500/20 text-orange-300',
  };

  return (
    <div className="group rounded-2xl border border-[#2b2b2b] bg-[#161616] p-5 shadow-sm transition-colors hover:border-[#20BF0E]/40">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            {script.type === 'outline' ? (
              <FileType className="h-5 w-5 text-purple-400" />
            ) : (
              <FileText className="h-5 w-5 text-orange-400" />
            )}
            <div className="text-base font-semibold text-white">{script.title}</div>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${typeColors[script.type]}`}
            >
              {script.type}
            </span>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[script.status] || statusColors.draft}`}
            >
              {script.status_display}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs text-[#AAACA6]">
            {script.word_count && (
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[#20BF0E]" />
                {script.word_count.toLocaleString()} words
              </span>
            )}
            {script.estimated_duration && (
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[#20BF0E]" />
                {Number(script.estimated_duration).toFixed(2)} min
              </span>
            )}
            <span>{new Date(script.created).toLocaleDateString()}</span>
          </div>
        </div>
        <button
          onClick={() => onCopy(script.title)}
          className="flex shrink-0 items-center gap-2 rounded-lg bg-[#1E1E1E] px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-[#20BF0E]/10"
        >
          <Copy className="h-4 w-4 text-[#20BF0E]" />
        </button>
      </div>
    </div>
  );
}
