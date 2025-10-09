'use client';

import { useState } from 'react';
import { Copy } from 'lucide-react';

import Button from 'components/ui/Button';

export default function CopyAllButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button
      onClick={handleCopy}
      className="mt-3 flex items-center justify-center gap-2 bg-white/10 px-4 py-2 text-sm transition-colors duration-200"
    >
      <Copy className="h-4 w-4" />
      {copied ? 'Copied!' : 'Copy All'}
    </Button>
  );
}
