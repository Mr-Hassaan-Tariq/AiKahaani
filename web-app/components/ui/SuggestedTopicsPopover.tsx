import { useState } from 'react';
import Image from 'next/image';
import { Lightbulb, Shuffle } from 'lucide-react';

import CopyIcon from '/public/images/copy.svg';
import Text from 'components/ui/Text';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

type Props = {
  suggestions?: string[];
};

export default function SuggestedTopicsPopover({ suggestions = [] }: Props) {
  const [items, setItems] = useState<string[]>(
    suggestions.length
      ? suggestions
      : [
          'Why people fake their own death',
          'The man who disappeared... twice',
          'A genius who changed the world, but no one knows their name',
        ],
  );

  const shuffle = () => {
    const arr = [...items];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    setItems(arr);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // optional feedback: you can fire a toast here
    } catch {
      // ignore
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm font-medium text-gray-300 transition-colors hover:text-white"
        >
          <Lightbulb size={16} className="text-gray-300" />
          <span className="text-xs">Suggest topic</span>
        </button>
      </PopoverTrigger>

      <PopoverContent
        side="bottom"
        align="end"
        className="w-[420px] rounded-xl border border-[#BAFF38]/20 bg-[rgba(20,20,20,0.92)] p-3 shadow-[0_6px_30px_rgba(0,0,0,0.6)] backdrop-blur-sm"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-2">
          <div className="flex items-center gap-3">
            <Lightbulb size={18} className="text-white" />
            <Text className="font-semibold text-white">Suggested topics</Text>
          </div>

          <button
            type="button"
            onClick={shuffle}
            className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-xs text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
            title="Shuffle topics"
          >
            <Shuffle size={14} />
            <span>Shuffle topics</span>
          </button>
        </div>

        {/* Items */}
        <ul className="mt-1 space-y-2">
          {items.map((s, i) => (
            <li
              key={i}
              className="hover:bg-white/3 flex items-center justify-between gap-3 rounded-md px-3 py-2 transition-colors"
            >
              <div className="flex items-start gap-3">
                {/* small bullet */}
                <span className="mt-2 inline-block h-2 w-2 rounded-full bg-white/80" />
                <Text className="max-w-[320px] text-sm leading-tight text-gray-200">{s}</Text>
              </div>

              <div className="flex items-center gap-2">
                <Image
                  className="cursor-pointer"
                  src={CopyIcon}
                  alt="copy"
                  width={16}
                  height={16}
                  onClick={() => copyToClipboard(s)}
                />
              </div>
            </li>
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  );
}
