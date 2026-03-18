'use client';

import { useState } from 'react';
import { Check, Copy, Download, PenLine, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

import ExportScriptModal from '@/(dashboard)/my-scripts/_components/ExportScriptModal';
import { ScriptData } from '@/(dashboard)/my-scripts/_types';

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
    <div className="flex items-center gap-3 flex-wrap">
      <button
        onClick={handleCopy}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground text-sm font-semibold transition-opacity hover:opacity-90"
      >
        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
        {copied ? 'Copied!' : 'Copy Script'}
      </button>

      <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-secondary text-secondary-foreground text-sm font-semibold transition-colors hover:bg-secondary/80">
        <PenLine className="h-4 w-4" />
        Edit
      </button>

      <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-secondary text-secondary-foreground text-sm font-semibold transition-colors hover:bg-secondary/80">
        <RefreshCw className="h-4 w-4" />
        Regenerate
      </button>

      <ExportScriptModal
        trigger={
          <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-secondary text-secondary-foreground text-sm font-semibold transition-colors hover:bg-secondary/80">
            <Download className="h-4 w-4" />
            Export
          </button>
        }
        script={script}
      />
    </div>
  );
}
