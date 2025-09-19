export type ScriptStatus = 'draft' | 'generated' | 'saved';
export type ScriptMode = 'outline' | 'script';

// Legacy Script interface for backward compatibility
export interface Script {
  id: string;
  title: string;
  status: ScriptStatus;
  lastEdited: string;
  duration: string;
  wordCount: string;
  mode: ScriptMode;
}

// New Script interface that matches API response
export interface ScriptFromAPI {
  uuid: string;
  title: string;
  type: 'script' | 'outline';
  status: 'draft' | 'generated' | 'saved';
  status_display: string;
  word_count: number | null;
  estimated_duration: number | null;
  created: string;
  modified: string;
  is_published: boolean | null;
  version: number;
}

export interface ScriptData {
  title: string;

  id?: string;
  status?: ScriptStatus;
  lastEdited?: string;
  duration?: string;
  wordCount?: string;
  mode?: ScriptMode;

  uuid?: string;
  type?: 'script' | 'outline';
  status_display?: string;
  word_count?: number | null;
  estimated_duration?: number | null;
  created?: string;
  modified?: string;
  is_published?: boolean | null;
  version?: number;
}

export interface ScriptActions {
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
  onExport?: (id: string) => void;
}

export interface ScriptListProps {
  scripts: ScriptData[];
  actions: ScriptActions;
  loading?: boolean;
  emptyState?: React.ReactNode;
  className?: string;
}

export interface ScriptCardProps {
  script: ScriptData;
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
