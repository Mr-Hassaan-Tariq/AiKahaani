'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy } from 'lucide-react';

type UserTitle = {
  uuid: string;
  user: number;
  prompt: string;
  titles: string[];
  tones: string[];
  user_title?: string;
  script?: number | null;
  created: string;
};

type TitleCardProps = {
  titleRecord: UserTitle;
  index: number;
  onCopy: (text: string) => void;
};

export default function TitleCard({ titleRecord, index, onCopy }: TitleCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const displayTitle = titleRecord.user_title || titleRecord.prompt || `Title Set ${index + 1}`;

  return (
    <div className="group rounded-2xl border border-[#2b2b2b] bg-[#161616] p-5 shadow-sm transition-colors hover:border-[#20BF0E]/40">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between text-left"
      >
        <div className="flex-1 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <div className="text-base font-semibold text-white">{displayTitle}</div>
            <span className="rounded-full bg-purple-500/20 px-2.5 py-0.5 text-xs font-medium text-purple-300">
              {titleRecord.titles?.length || 0} titles
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs text-[#AAACA6]">
            <span>{new Date(titleRecord.created).toLocaleDateString()}</span>
            {titleRecord.tones && titleRecord.tones.length > 0 && (
              <span className="flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-[#20BF0E]" />
                {titleRecord.tones.join(', ')}
              </span>
            )}
          </div>
        </div>
        <div className="ml-4 flex items-center gap-2">
          <div className="rounded-lg bg-[#1E1E1E] p-2 transition-colors group-hover:bg-[#20BF0E]/10">
            {isExpanded ? (
              <ChevronUp className="h-4 w-4 text-[#20BF0E]" />
            ) : (
              <ChevronDown className="h-4 w-4 text-[#AAACA6]" />
            )}
          </div>
        </div>
      </button>

      {isExpanded && (
        <div className="mt-5 space-y-4 border-t border-[#2b2b2b] pt-5 duration-200 animate-in fade-in slide-in-from-top-2">
          {titleRecord.prompt && (
            <div className="rounded-lg border border-[#2b2b2b] bg-[#1E1E1E] p-4">
              <div className="mb-2 text-xs font-medium uppercase tracking-wide text-[#AAACA6]">
                Prompt
              </div>
              <div className="text-sm leading-relaxed text-white">{titleRecord.prompt}</div>
            </div>
          )}

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-xs font-medium uppercase tracking-wide text-[#AAACA6]">
                Generated Titles
              </div>
              <div className="text-xs text-[#AAACA6]">{titleRecord.titles?.length || 0} total</div>
            </div>
            <div className="space-y-2">
              {(titleRecord.titles || []).map((title, idx) => (
                <div
                  key={`${titleRecord.uuid}-${title}-${idx}`}
                  className="group/title flex items-start gap-3 rounded-lg border border-[#2b2b2b] bg-[#1E1E1E] p-4 transition-all hover:border-[#20BF0E]/40"
                >
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#20BF0E]/20 text-xs font-semibold text-[#20BF0E]">
                    {idx + 1}
                  </div>
                  <div className="flex-1 text-sm leading-relaxed text-white">{title}</div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onCopy(title);
                    }}
                    className="flex shrink-0 items-center gap-1.5 rounded-lg border border-[#2b2b2b] bg-[#1E1E1E] px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-[#20BF0E]/10"
                  >
                    <Copy className="h-3.5 w-3.5 text-[#20BF0E]" />
                    Copy
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
