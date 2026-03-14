'use client';

import { lazy, memo, Suspense, useMemo, useState } from 'react';
import { ScriptData } from '@/(dashboard)/my-scripts/_types';
import { Clock, Minus } from 'lucide-react';

import { ScriptSectionType } from './types';

// Lazy load ReactMarkdown for better performance
const ReactMarkdown = lazy(() => import('react-markdown'));

// ── Content renderer with expand/collapse ─────────────────────────────────────
const MAX_CONTENT_LENGTH = 200;
const TRUNCATE_LINES = 10;

const ContentRenderer = memo(function ContentRenderer({ content }: { content: string }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const { shouldTruncate, truncatedContent } = useMemo(() => {
    const lines = content.split('\n');
    const shouldTruncate = content.length > MAX_CONTENT_LENGTH || lines.length > TRUNCATE_LINES;
    let truncatedContent = content;
    if (shouldTruncate && !isExpanded) {
      if (content.length > MAX_CONTENT_LENGTH) {
        truncatedContent = content.substring(0, MAX_CONTENT_LENGTH) + '…';
      } else if (lines.length > TRUNCATE_LINES) {
        truncatedContent = lines.slice(0, TRUNCATE_LINES).join('\n') + '\n…';
      }
    }
    return { shouldTruncate, truncatedContent };
  }, [content, isExpanded]);

  return (
    <div>
      <div className="prose prose-sm max-w-none whitespace-pre-line text-foreground [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
        <Suspense fallback={<div className="h-4 animate-pulse rounded bg-muted" />}>
          <ReactMarkdown>{isExpanded ? content : truncatedContent}</ReactMarkdown>
        </Suspense>
      </div>

      {shouldTruncate && (
        <div className="mt-3 border-t border-border pt-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs font-medium text-primary transition-colors hover:text-primary/80"
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        </div>
      )}
    </div>
  );
});

// ── Main component ────────────────────────────────────────────────────────────

export default function ScriptComponent({
  sections,
}: {
  sections: ScriptSectionType[];
  script: ScriptData;
}) {
  return (
    <div className="flex flex-col gap-6">
      {/* Sections */}
      <div className="flex flex-col gap-3">
        {sections.map((section, i) => (
          <div
            key={`${section.title}-${i}`}
            className="rounded-xl border border-border bg-card p-5"
          >
            {/* Section header */}
            <div className="mb-3 flex items-center gap-2">
              {section.timeRange && section.timeRange !== '-' && (
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3.5 w-3.5" />
                  {section.timeRange}
                  <Minus className="h-3 w-3" />
                </span>
              )}
              <span className="text-sm font-semibold text-foreground">{section.title}</span>
            </div>

            {/* Content */}
            <ContentRenderer content={section.content} />
          </div>
        ))}
      </div>

    </div>
  );
}
