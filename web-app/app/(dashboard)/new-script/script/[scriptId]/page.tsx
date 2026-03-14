import Link from 'next/link';
import { Download, ExternalLink, Clock, FileText, Hash } from 'lucide-react';

import CopyAllButton from '@/(dashboard)/new-script/_components/CopyAllButton';
import ExportScriptModal from '@/(dashboard)/my-scripts/_components/ExportScriptModal';
import { ScriptData } from '@/(dashboard)/my-scripts/_types';
import { Button } from 'components/ui/Button';

import { getScript } from './actions';
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
    <div className="flex flex-col">
      {/* Actions bar */}
      <div className="flex items-center justify-end gap-2 border-b border-border px-7 py-3">
        <CopyAllButton text={allContent} />
        <ExportScriptModal
          trigger={
            <Button size="sm">
              <Download className="h-4 w-4" /> Export
            </Button>
          }
          script={data as ScriptData}
        />
      </div>

      <div className="p-7">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.5fr)_280px]">

          {/* ── Script sections ── */}
          <div className="flex flex-col gap-4">
            <ScriptComponent sections={sections} script={data as ScriptData} />
          </div>

          {/* ── Sidebar meta ── */}
          <div className="flex flex-col gap-4">

            {/* Stats card */}
            <div className="rounded-lg border border-border bg-card p-5 flex flex-col gap-4">
              <h3 className="text-sm font-semibold text-foreground">Script details</h3>
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[13px] text-muted-foreground">
                    <FileText className="h-3.5 w-3.5" />
                    Sections
                  </div>
                  <span className="text-[13px] font-semibold text-foreground">{sections.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[13px] text-muted-foreground">
                    <Hash className="h-3.5 w-3.5" />
                    Word count
                  </div>
                  <span className="text-[13px] font-semibold text-foreground">
                    {data?.word_count ? `~${data.word_count.toLocaleString()}` : '—'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[13px] text-muted-foreground">
                    <Clock className="h-3.5 w-3.5" />
                    Est. runtime
                  </div>
                  <span className="text-[13px] font-semibold text-foreground">
                    {data?.estimated_duration ? `~${data.estimated_duration} min` : '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* Actions card */}
            <div className="rounded-lg border border-border bg-card p-5 flex flex-col gap-3">
              <h3 className="text-sm font-semibold text-foreground">Actions</h3>
              <CopyAllButton text={allContent} />
              <ExportScriptModal
                trigger={
                  <Button size="sm" className="w-full" variant="outline">
                    <Download className="h-4 w-4" /> Download script
                  </Button>
                }
                script={data as ScriptData}
              />
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/my-scripts">
                  <ExternalLink className="h-4 w-4" /> View all scripts
                </Link>
              </Button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
