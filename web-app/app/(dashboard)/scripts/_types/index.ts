export type ScriptStatus = 'Outline only' | 'Script in progress' | 'Completed';
export type ScriptMode = 'outline' | 'script';

export interface Script {
  id: string;
  title: string;
  status: ScriptStatus;
  lastEdited: string;
  duration: string;
  wordCount: string;
  mode: ScriptMode;
}

export interface ScriptActions {
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
  onExport?: (id: string) => void;
}

export interface ScriptListProps {
  scripts: Script[];
  actions: ScriptActions;
  loading?: boolean;
  emptyState?: React.ReactNode;
  className?: string;
}

export interface ScriptCardProps {
  script: Script;
  actions: ScriptActions;
  className?: string;
}

export interface ScriptsTabProps {
  children: React.ReactNode;
  onSearch?: (query: string) => void;
  onFilter?: () => void;
  searchValue?: string;
  className?: string;
}

export interface TabConfig {
  label: string;
  path: string;
  query?: string;
}

export interface ScriptsPageProps {
  onCreateScript?: () => void;
  onCreateOutline?: () => void;
}

export interface EmptyStateProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}
