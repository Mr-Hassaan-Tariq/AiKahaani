'use client';

import { useState } from 'react';
import ExportScriptModal from '@/(dashboard)/my-scripts/_components/ExportScriptModal';
import { ScriptData } from '@/(dashboard)/my-scripts/_types';
import { Check, Copy, Download, PenLine, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
  text: string;
  script: ScriptData;
}

export default function ScriptActionBar({ text, script }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        onClick={handleCopy}
        className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
      >
        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
        {copied ? 'Copied!' : 'Copy Script'}
      </button>

      <button className="inline-flex items-center gap-2 rounded-full bg-secondary px-5 py-2.5 text-sm font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
        <PenLine className="h-4 w-4" />
        Edit
      </button>

      <button className="inline-flex items-center gap-2 rounded-full bg-secondary px-5 py-2.5 text-sm font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
        <RefreshCw className="h-4 w-4" />
        Regenerate
      </button>

      <ExportScriptModal
        trigger={
          <button className="inline-flex items-center gap-2 rounded-full bg-secondary px-5 py-2.5 text-sm font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
            <Download className="h-4 w-4" />
            Export
          </button>
        }
        script={script}
      />
    </div>
  );
}
