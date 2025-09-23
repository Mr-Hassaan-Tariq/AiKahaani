'use client';

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';

import { ScriptActions } from '../_types';
import useDeleteScriptGeneration from 'lib/hooks/useDeleteScriptGeneration';

export function useScriptActions() {
  const router = useRouter();
  const { mutate: deleteScript, isPending: isDeleting } = useDeleteScriptGeneration();

  const actions: ScriptActions = {
    onDelete: useCallback(
      async (id: string) => {
        try {
          await deleteScript(id);
        } catch (err) {
          throw err;
        }
      },
      [deleteScript],
    ),

    onEdit: useCallback(
      (id: string) => {
        console.log('Edit script:', id);
        // TODO: Implement edit functionality
        router.push(`/my-scripts/edit/${id}`);
      },
      [router],
    ),

    onExport: useCallback((id: string) => {
      console.log('Export script:', id);
      // TODO: Implement export functionality
    }, []),
  };

  return {
    actions,
    isDeleting,
  };
}

export function useOutlineActions() {
  const router = useRouter();
  const { mutate: deleteScript, isPending: isDeleting } = useDeleteScriptGeneration();

  const actions: ScriptActions = {
    onDelete: useCallback(
      async (id: string) => {
        try {
          await deleteScript(id);
        } catch (err) {
          throw err;
        }
      },
      [deleteScript],
    ),

    onEdit: useCallback(
      (id: string) => {
        console.log('Edit script:', id);
        // TODO: Implement edit functionality
        router.push(`/my-scripts/edit/${id}`);
      },
      [router],
    ),

    onExport: useCallback((id: string) => {
      console.log('Export script:', id);
      // TODO: Implement export functionality
    }, []),
  };

  return {
    actions,
    isDeleting,
  };
}
