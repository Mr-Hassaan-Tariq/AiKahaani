'use client';

import { lazy, memo, Suspense, useMemo, useState } from 'react';
import Link from 'next/link';
import ExportScriptModal from '@/(dashboard)/my-scripts/_components/ExportScriptModal';
import { ScriptData } from '@/(dashboard)/my-scripts/_types';
import { Clock, Minus } from 'lucide-react';

import { directFileIcon } from '../../[outlineId]/_components/components';
import { ScriptSectionType } from './types';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

// Lazy load ReactMarkdown for better performance
const ReactMarkdown = lazy(() => import('react-markdown'));

// Constants for content management
const MAX_CONTENT_LENGTH = 200; // Characters
const TRUNCATE_LINES = 10; // Lines to show when truncated

// Component to handle large content with truncation
const ContentRenderer = memo(function ContentRenderer({ content }: { content: string }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const { shouldTruncate, truncatedContent } = useMemo(() => {
    const lines = content.split('\n');
    const shouldTruncate = content.length > MAX_CONTENT_LENGTH || lines.length > TRUNCATE_LINES;

    let truncatedContent = content;
    if (shouldTruncate && !isExpanded) {
      if (content.length > MAX_CONTENT_LENGTH) {
        truncatedContent = content.substring(0, MAX_CONTENT_LENGTH) + '...';
      } else if (lines.length > TRUNCATE_LINES) {
        truncatedContent = lines.slice(0, TRUNCATE_LINES).join('\n') + '\n...';
      }
    }

    return {
      shouldTruncate,
      truncatedContent,
      lineCount: lines.length,
    };
  }, [content, isExpanded]);

  return (
    <div className="relative">
      <div className="prose prose-invert prose-sm max-w-none whitespace-pre-line [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
        <Suspense fallback={<div className="animate-pulse text-white/50">Loading content...</div>}>
          <ReactMarkdown>{isExpanded ? content : truncatedContent}</ReactMarkdown>
        </Suspense>
      </div>

      {shouldTruncate && (
        <div className="mt-3 flex items-center justify-between border-t border-white/10 pt-3">
          <span className="text-xs text-white/50">
            {/* {lineCount} lines • {content.length} characters */}
          </span>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs font-medium text-white/50 transition-colors hover:text-white"
          >
            {isExpanded ? 'Show Less' : 'Show More'}
          </button>
        </div>
      )}
    </div>
  );
});

export default function ScriptComponent({
  sections,
  script,
}: {
  sections: ScriptSectionType[];
  script: ScriptData;
}) {
  return (
    <>
      <Col className="scrollbar h-full w-full space-y-3">
        {sections.map((e) => (
          <Card
            key={e.title}
            className="border border-white/20 bg-white/10 p-6 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10"
          >
            <div className="font-figtree text-base text-white">
              <span className="flex items-center gap-2 font-semibold text-white/90 transition-colors duration-200 group-hover:text-white">
                <Clock />
                {e.timeRange && e.timeRange}
                <Minus className="inline-block" />
                {e.title}
              </span>
              <div className="mt-3 text-white/70 transition-colors duration-200 group-hover:text-white/80">
                <ContentRenderer content={e.content} />
              </div>
            </div>
          </Card>
        ))}
      </Col>

      <Row className="ml-auto mt-6 w-full flex-col space-y-3 lg:w-fit lg:flex-row lg:space-y-0">
        <Link href="/my-scripts">
          <Button
            variant="gray"
            className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit"
          >
            Go to Script
          </Button>
        </Link>
        <ExportScriptModal
          trigger={
            <Button className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit">
              {directFileIcon} Download
            </Button>
          }
          script={script}
        />
      </Row>
    </>
  );
}
