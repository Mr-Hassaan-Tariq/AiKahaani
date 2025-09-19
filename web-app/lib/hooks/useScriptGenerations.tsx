import { useCallback, useEffect, useState } from 'react';

import { ScriptGeneration } from '../api/types';
import { scriptsService } from '../api/wrapper';

interface UseScriptGenerationsReturn {
  scriptGenerations: ScriptGeneration[];
  loading: boolean;
  error: string | null;
  refetch: (search?: string, type?: 'script' | 'outline') => Promise<void>;
  deleteScript: (uuid: string) => Promise<void>;
  updateScript: (uuid: string, updates: Partial<ScriptGeneration>) => Promise<void>;
}

export const useScriptGenerations = (): UseScriptGenerationsReturn => {
  const [scriptGenerations, setScriptGenerations] = useState<ScriptGeneration[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch script generations
  const fetchScriptGenerations = useCallback(
    async (search?: string, type?: 'script' | 'outline') => {
      setLoading(true);
      setError(null);

      try {
        const data = await scriptsService.getScriptGenerations(search, type);
        setScriptGenerations(data);
      } catch (err) {
        const error = err as { message: string };
        setError(error.message || 'Failed to fetch script generations');
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  // Delete script generation
  const deleteScript = useCallback(async (uuid: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await scriptsService.deleteScriptGeneration(uuid);
      if (response.status === 204) {
        fetchScriptGenerations();
      }
      // setScriptGenerations((prev) => prev.filter((script) => script.uuid !== uuid));
    } catch (err) {
      const error = err as { message: string };
      setError(error.message || 'Failed to delete script');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update script generation
  const updateScript = useCallback(async (uuid: string, updates: Partial<ScriptGeneration>) => {
    setLoading(true);
    setError(null);

    try {
      const updatedScript = await scriptsService.updateScriptGeneration(uuid, updates);
      setScriptGenerations((prev) =>
        prev.map((script) => (script.uuid === uuid ? updatedScript : script)),
      );
    } catch (err) {
      const error = err as { message: string };
      setError(error.message || 'Failed to update script');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchScriptGenerations();
  }, [fetchScriptGenerations]);

  return {
    scriptGenerations,
    loading,
    error,
    refetch: fetchScriptGenerations,
    deleteScript,
    updateScript,
  };
};
