'use client';

import { useState } from 'react';
import { Copy } from 'lucide-react';

import Button from 'components/ui/Button';

export default function CopyAllButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button
      onClick={handleCopy}
      className="flex items-center justify-center gap-2 rounded-full bg-[#2B2B2B] px-5 py-2 text-sm text-white shadow-[0_0_10px_rgba(255,255,255,0.05)] transition-all duration-200 hover:bg-[#3A3A3A]"
    >
      <Copy className="h-4 w-4" />
      {copied ? 'Copied!' : 'Copy'}
    </Button>
  );
}
