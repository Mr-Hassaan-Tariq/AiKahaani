'use client';

import Link from 'next/link';
import ExportScriptModal from '@/(dashboard)/my-scripts/_components/ExportScriptModal';
import ReactMarkdown from 'react-markdown';

import { directFileIcon } from '../../[outlineId]/_components/components';
import { ScriptSectionType } from './types';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

export default function ScriptComponent({
  sections,
  script,
}: {
  sections: ScriptSectionType[];
  script: any;
}) {
  return (
    <>
      <Col className="scrollbar h-full w-full space-y-3">
        {sections.map((e) => (
          <Card
            key={e.title}
            className="cursor-pointer border border-white/20 bg-white/10 p-0 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10"
          >
            <div className="p-0">
              <div className="font-figtree text-base text-white">
                <span className="font-semibold text-white/90 transition-colors duration-200 group-hover:text-white">
                  {e.title}
                </span>
                <div className="ml-0 text-white/70 transition-colors duration-200 group-hover:text-white/80">
                  <div className="prose prose-invert prose-sm max-w-none whitespace-pre-line [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                    <ReactMarkdown>{e.content}</ReactMarkdown>
                  </div>
                </div>
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
