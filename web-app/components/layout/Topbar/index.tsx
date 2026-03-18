import { ReactNode } from 'react';

import { cn } from 'lib/utils';

interface TopbarProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  className?: string;
}

/**
 * Page-level topbar.
 * Used at the top of each dashboard page's content — not in the layout itself,
 * so each page can supply its own title, subtitle, and action buttons.
 *
 * Usage:
 *   <Topbar title="Script Generator" subtitle="..." actions={<Button>New</Button>} />
 */
export default function Topbar({ title, subtitle, actions, className }: TopbarProps) {
  return (
    <header
      className={cn(
        'flex min-h-[76px] shrink-0 items-center justify-between border-b border-border bg-background px-7 py-5',
        className,
      )}
    >
      {/* Left: title + subtitle */}
      <div className="flex min-w-0 flex-col gap-1.5">
        <h1 className="truncate text-2xl font-semibold tracking-tight text-foreground">{title}</h1>
        {subtitle && (
          <p className="truncate text-sm font-medium text-muted-foreground">{subtitle}</p>
        )}
      </div>

      {/* Right: action buttons */}
      {actions && <div className="ml-4 flex shrink-0 items-center gap-2">{actions}</div>}
    </header>
  );
}
