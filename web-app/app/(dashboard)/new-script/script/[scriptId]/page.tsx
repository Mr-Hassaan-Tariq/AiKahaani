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

  const allContent = sections?.map((e: any) => `${e.title}\n\n${e.content}`).join('\n\n');

  return (
    <Col className="w-full items-center gap-8 text-center">
      {/* Title */}
      <H3 className="text-center text-white">
        {data?.title ? `Full Script: ${data.title}` : 'Full Script'}
      </H3>

      {/* Copy Button below title */}
      <div className="flex justify-center">
        <CopyAllButton text={allContent} />
      </div>

      {/* Script Content */}
      {isError ? (
        <div className="text-white">{error.message?.toString()}</div>
      ) : (
        <ScriptComponent sections={sections} script={data as ScriptData} />
      )}
    </Col>
  );
}
