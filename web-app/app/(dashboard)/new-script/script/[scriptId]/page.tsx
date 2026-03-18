import { ScriptData } from '@/(dashboard)/my-scripts/_types';

import { getScript } from './actions';
import ScriptActionBar from './ScriptActionBar';
import ScriptComponent from './ScriptComponent';

export default async function Page({ params }: { params: Promise<{ scriptId: string }> }) {
  const { scriptId } = await params;
  const { data, isError, error } = await getScript(scriptId);

  if (isError) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center gap-2 text-center">
        <p className="text-sm font-medium text-destructive">Failed to load script</p>
        <p className="text-xs text-muted-foreground">{String((error as any)?.message ?? '')}</p>
      </div>
    );
  }

  const sections =
    data?.sections && data?.sections?.length > 0
      ? data.sections.map((e: any) => ({
          timeRange: e.timeRange ?? `${e.start_time ?? ''}${e.end_time ? ` – ${e.end_time}` : ''}`,
          title: e.title ?? '',
          content: e.content ?? e.script ?? '',
        }))
      : JSON.parse(data?.content || '{}')?.script?.sections?.map((e: any) => ({
          timeRange: `${e.start_time ?? ''} – ${e.end_time ?? ''}`,
          title: e.title ?? '',
          content: e.script ?? '',
        })) || [];

  const allContent = data?.title + '\n\n' + sections.map((e: any) => `${e.title}\n\n${e.content}`).join('\n\n');

  return (
    <div className="flex justify-center px-8 pt-12 pb-24">
      <div className="w-full max-w-[800px]">

          {/* ── Script header ── */}
          <div className="mb-12">
            <h1 className="text-[42px] font-bold leading-[1.2] tracking-tight text-foreground mb-6">
              {data?.title}
            </h1>
            <ScriptActionBar text={allContent} script={data as ScriptData} />
          </div>

          {/* ── Script sections ── */}
          <ScriptComponent sections={sections} script={data as ScriptData} />

      </div>
    </div>
  );
}
