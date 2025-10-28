'use client';

import { useState } from 'react';
import { Copy } from 'lucide-react';
import { toast } from 'sonner';

export default function CopyAllButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied!', {
      description: 'Script copied to clipboard 📋',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center justify-center gap-2 rounded-full bg-[#2B2B2B] px-5 py-3 text-sm text-white transition-all hover:bg-[#3A3A3A] active:scale-95"
    >
      <Copy className="h-4 w-4" />
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
}
