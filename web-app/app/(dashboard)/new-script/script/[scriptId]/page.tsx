import { ScriptData } from '@/(dashboard)/my-scripts/_types';
import CopyAllButton from '@/(dashboard)/new-script/_components/CopyAllButton';

import { getScript } from './actions';
import ScriptComponent from './ScriptComponent';
import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';

export default async function Page({ params }: { params: Promise<{ scriptId: string }> }) {
  const { scriptId } = await params;
  const { data, isError, error } = await getScript(scriptId);

  const sections =
    data?.sections && data?.sections?.length > 0
      ? data.sections.map((e: any) => ({
          timeRange: `${e.start_time ?? ''}-${e.end_time ?? ''}`,
          title: e.title ?? '',
          content: e.content,
        }))
      : JSON.parse(data?.content || '{}')?.script?.sections?.map((e: any) => ({
          timeRange: `${e.start_time ?? ''}-${e.end_time ?? ''}`,
          title: e.title ?? '',
          content: e.script,
        })) || [];

  const allContent = sections?.map((e: any) => `${e.content}`).join('\n\n');

  return (
    <Col className="gap-8">
      <Col className="w-full">
        <div className="flex w-full items-center justify-between">
          <H3 className="text-white">{data?.title || 'Untitled Script'}</H3>
          <div className="flex justify-end">
            <CopyAllButton text={allContent} />
          </div>
        </div>
      </Col>

      {isError ? (
        <div className="text-white">{error.message?.toString()}</div>
      ) : (
        <ScriptComponent sections={sections} script={data as ScriptData} />
      )}
    </Col>
  );
}
