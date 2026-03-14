import { Copy } from 'lucide-react';

export default function TitleList({
  titles,
  onCopy,
}: {
  titles: string[];
  onCopy: (title: string) => void;
}) {
  return (
    <div className="flex max-h-80 w-full flex-col gap-2 overflow-y-auto pr-1">
      {titles.map((title, i) => (
        <div
          key={i}
          className="flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3"
        >
          <span className="text-sm text-foreground">
            <span className="mr-2 font-semibold text-primary">{i + 1}.</span>
            {title}
          </span>
          <button
            onClick={() => onCopy(title)}
            className="shrink-0 text-muted-foreground transition-colors hover:text-foreground"
            aria-label="Copy title"
          >
            <Copy className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
