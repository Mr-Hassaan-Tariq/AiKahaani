'use client';

import Link from 'next/link';
import ExportScriptModal from '@/(dashboard)/my-scripts/_components/ExportScriptModal';

import { directFileIcon } from '../../[outlineId]/_components/components';
import { ScriptSectionType } from './types';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

export default function ScriptComponent({
  sections,
  uuid,
}: {
  sections: ScriptSectionType[];
  uuid: string;
}) {
  return (
    <>
      <Col className="scrollbar h-full w-full space-y-3">
        {sections.map((e) => (
          <Card
            key={e.title}
            className="group cursor-pointer border border-white/20 bg-white/10 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10"
          >
            <div className="p-4">
              <div className="font-figtree text-base text-white">
                <span className="font-semibold text-white/90 transition-colors duration-200 group-hover:text-white">
                  {e.title}
                </span>
                <span className="ml-2 whitespace-pre-line text-white/70 transition-colors duration-200 group-hover:text-white/80">
                  {e.content}
                </span>
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
          script={uuid}
          actions={undefined}
        />
      </Row>
    </>
  );
}
