import { useCallback, useMemo, useState } from 'react';

import { Script, ScriptActions } from '../_types';

interface UseScriptsProps {
  initialScripts: Script[];
  onScriptUpdate?: (scripts: Script[]) => void;
}

interface UseScriptsReturn {
  scripts: Script[];
  filteredScripts: Script[];
  searchQuery: string;
  selectedMode: string | null;
  actions: ScriptActions;
  loading: boolean;
  error: string | null;
  setSearchQuery: (query: string) => void;
  setSelectedMode: (mode: string | null) => void;
  addScript: (script: Script) => void;
  updateScript: (id: string, updates: Partial<Script>) => void;
  deleteScript: (id: string) => void;
  clearError: () => void;
}

export function useScripts({ initialScripts, onScriptUpdate }: UseScriptsProps): UseScriptsReturn {
  const [scripts, setScripts] = useState<Script[]>(initialScripts);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filter scripts based on search query and selected mode
  const filteredScripts = useMemo(() => {
    let filtered = scripts;

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter((script) =>
        script.title.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    }

    // Filter by mode
    if (selectedMode) {
      filtered = filtered.filter((script) => script.mode === selectedMode);
    }

    return filtered;
  }, [scripts, searchQuery, selectedMode]);

  // Script actions
  const actions: ScriptActions = {
    onDelete: useCallback(
      (id: string) => {
        setLoading(true);
        try {
          setScripts((prev) => {
            const updated = prev.filter((script) => script.id !== id);
            onScriptUpdate?.(updated);
            return updated;
          });
        } catch (err) {
          setError('Failed to delete script' + (err as Error).message);
        } finally {
          setLoading(false);
        }
      },
      [onScriptUpdate],
    ),

    onEdit: useCallback((id: string) => {
      console.log('Edit script:', id);
      // TODO: Implement edit functionality
    }, []),

    onExport: useCallback((id: string) => {
      console.log('Export script:', id);
      // TODO: Implement export functionality
    }, []),
  };

  const addScript = useCallback(
    (script: Script) => {
      setScripts((prev) => {
        const updated = [...prev, script];
        onScriptUpdate?.(updated);
        return updated;
      });
    },
    [onScriptUpdate],
  );

  const updateScript = useCallback(
    (id: string, updates: Partial<Script>) => {
      setScripts((prev) => {
        const updated = prev.map((script) =>
          script.id === id ? { ...script, ...updates } : script,
        );
        onScriptUpdate?.(updated);
        return updated;
      });
    },
    [onScriptUpdate],
  );

  const deleteScript = useCallback(
    (id: string) => {
      actions.onDelete(id);
    },
    [actions],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    scripts,
    filteredScripts,
    searchQuery,
    selectedMode,
    actions,
    loading,
    error,
    setSearchQuery,
    setSelectedMode,
    addScript,
    updateScript,
    deleteScript,
    clearError,
  };
}
