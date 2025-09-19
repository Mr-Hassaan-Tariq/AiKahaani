import { useCallback, useMemo, useRef, useState } from 'react';

import { Script, ScriptActions, ScriptData } from '../_types';
import { useScriptGenerations } from 'lib/hooks/useScriptGenerations';

interface UseScriptsProps {
  initialScripts?: ScriptData[];
  onScriptUpdate?: (scripts: ScriptData[]) => void;
  useAPI?: boolean;
}

interface UseScriptsReturn {
  scripts: ScriptData[];
  filteredScripts: ScriptData[];
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
  refetch: () => Promise<void>;
  handleSearch: (query: string) => Promise<void>;
}

export function useScripts({
  initialScripts = [],
  onScriptUpdate,
  useAPI = true,
}: UseScriptsProps): UseScriptsReturn {
  // Use API hook if enabled
  const {
    scriptGenerations: apiScripts,
    loading: apiLoading,
    error: apiError,
    refetch: refetchAPI,
    deleteScript: deleteScriptAPI,
    updateScript: updateScriptAPI,
  } = useScriptGenerations();

  const [localScripts, setLocalScripts] = useState<ScriptData[]>(initialScripts);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState<string | null>(null);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const transformedScripts = useMemo(() => {
    if (useAPI) {
      return apiScripts as any; // Use original API response format
    }
    return localScripts;
  }, [useAPI, apiScripts, localScripts]);

  const scripts = useAPI
    ? apiError && initialScripts.length > 0
      ? initialScripts
      : transformedScripts
    : localScripts;
  const loading = useAPI ? apiLoading : localLoading;
  const error = useAPI ? (apiError && initialScripts.length > 0 ? null : apiError) : localError;

  const filteredScripts = useMemo(() => {
    let filtered = scripts;

    if (!useAPI && searchQuery.trim()) {
      filtered = filtered.filter((script: ScriptData) =>
        script.title.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    }

    if (selectedMode) {
      if (useAPI) {
        filtered = filtered.filter(
          (script: ScriptData) => 'type' in script && script.type === selectedMode,
        );
      } else {
        filtered = filtered.filter(
          (script: ScriptData) => 'mode' in script && script.mode === selectedMode,
        );
      }
    }

    return filtered;
  }, [scripts, searchQuery, selectedMode, useAPI]);

  // Script actions
  const actions: ScriptActions = {
    onDelete: useCallback(
      async (id: string) => {
        if (useAPI) {
          try {
            await deleteScriptAPI(id);
          } catch (err) {
            console.error('Failed to delete script:', err);
            throw err;
          }
        } else {
          setLocalLoading(true);
          try {
            setLocalScripts((prev) => {
              const updated = prev.filter((script) => script.id !== id);
              onScriptUpdate?.(updated);
              return updated;
            });
          } catch (err) {
            setLocalError('Failed to delete script: ' + (err as Error).message);
          } finally {
            setLocalLoading(false);
          }
        }
      },
      [useAPI, apiScripts, deleteScriptAPI, onScriptUpdate],
    ),

    onEdit: useCallback((id: string) => {
      console.log('Edit script:', id);
    }, []),

    onExport: useCallback((id: string) => {
      console.log('Export script:', id);
    }, []),
  };

  const addScript = useCallback(
    (script: Script) => {
      if (!useAPI) {
        setLocalScripts((prev) => {
          const updated = [...prev, script];
          onScriptUpdate?.(updated);
          return updated;
        });
      }
    },
    [useAPI, onScriptUpdate],
  );

  const updateScript = useCallback(
    async (id: string, updates: Partial<Script>) => {
      if (useAPI) {
        try {
          const apiUpdates: any = {};
          if (updates.title) apiUpdates.title = updates.title;
          await updateScriptAPI(id, apiUpdates);
        } catch (err) {
          console.error('Failed to update script:', err);
          throw err;
        }
      } else {
        setLocalScripts((prev) => {
          const updated = prev.map((script) =>
            script.id === id ? { ...script, ...updates } : script,
          );
          onScriptUpdate?.(updated);
          return updated;
        });
      }
    },
    [useAPI, apiScripts, updateScriptAPI, onScriptUpdate],
  );

  const deleteScript = useCallback(
    (id: string) => {
      actions.onDelete(id);
    },
    [actions],
  );

  const clearError = useCallback(() => {
    if (useAPI) {
      return;
    }
    setLocalError(null);
  }, [useAPI]);

  const refetch = useCallback(async () => {
    if (useAPI) {
      const typeParam =
        selectedMode === 'outline' || selectedMode === 'script' ? selectedMode : undefined;
      await refetchAPI(undefined, typeParam as 'script' | 'outline' | undefined);
    }
  }, [useAPI, refetchAPI, selectedMode]);

  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleSearch = useCallback(
    async (query: string) => {
      setSearchQuery(query);

      if (useAPI) {
        if (searchTimeoutRef.current) {
          clearTimeout(searchTimeoutRef.current);
        }

        searchTimeoutRef.current = setTimeout(async () => {
          const typeParam =
            selectedMode === 'outline' || selectedMode === 'script' ? selectedMode : undefined;
          await refetchAPI(query, typeParam as 'script' | 'outline' | undefined);
        }, 500);
      }
    },
    [useAPI, refetchAPI, selectedMode],
  );

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
    refetch,
    handleSearch,
  };
}
