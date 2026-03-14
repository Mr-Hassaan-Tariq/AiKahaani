import { cn } from 'lib/utils';

export default function Tabs({
  activeTab,
  setActiveTab,
  isGenerating,
}: {
  activeTab: 'generate' | 'optimize';
  setActiveTab: (tab: 'generate' | 'optimize') => void;
  isGenerating: boolean;
}) {
  return (
    <div className="mt-4 flex items-center rounded-lg border border-border bg-muted p-0.5">
      {(['generate', 'optimize'] as const).map((tab) => (
        <button
          key={tab}
          disabled={isGenerating}
          onClick={() => setActiveTab(tab)}
          className={cn(
            'flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors',
            activeTab === tab
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground',
            isGenerating && 'cursor-not-allowed opacity-50',
          )}
        >
          {tab === 'generate' ? 'Generate New' : 'Optimize Existing'}
        </button>
      ))}
    </div>
  );
}
