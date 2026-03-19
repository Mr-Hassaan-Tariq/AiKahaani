'use client';

import { lazy, Suspense } from 'react';
import { ScriptData } from '@/(dashboard)/my-scripts/_types';
import { Clock } from 'lucide-react';

import { ScriptSectionType } from './types';

const ReactMarkdown = lazy(() => import('react-markdown'));

export default function ScriptComponent({
  sections,
}: {
  sections: ScriptSectionType[];
  script: ScriptData;
}) {
  return (
    <div className="flex flex-col gap-6">
      {sections.map((section, i) => (
        <div
          key={`${section.title}-${i}`}
          className="flex flex-col gap-4 rounded-xl border border-border bg-card p-4 sm:p-8"
        >
          {/* Time badge */}
          {section.timeRange && section.timeRange !== ' – ' && section.timeRange !== '-' && (
            <div>
              <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-3 py-1.5 text-[13px] font-semibold text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                {section.timeRange}
              </span>
            </div>
          )}

          {/* Section heading */}
          <h3 className="text-xl font-semibold leading-snug text-primary">{section.title}</h3>

          {/* Content */}
          <div className="prose prose-sm max-w-none text-[16px] leading-[1.7] text-foreground [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
            <Suspense fallback={<div className="h-4 animate-pulse rounded bg-muted" />}>
              <ReactMarkdown>{section.content}</ReactMarkdown>
            </Suspense>
          </div>
        </div>
      ))}
    </div>
  );
}
