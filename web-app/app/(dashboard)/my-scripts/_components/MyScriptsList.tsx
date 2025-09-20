'use client';

import { useState } from 'react';

import { useScriptActions } from '../_hooks/useScriptActions';
import ScriptList from './ScriptList';
import { ScriptGeneration } from 'lib/api/types';

interface MyScriptsListProps {
  initialScripts?: ScriptGeneration[];
  error?: any;
  isError?: boolean;
  searchQuery?: string;
}

export default function MyScriptsList({
  initialScripts = [],
  error,
  isError,
  searchQuery,
}: MyScriptsListProps) {
  const [scripts, setScripts] = useState<ScriptGeneration[]>(initialScripts);
  const { actions } = useScriptActions();

  // Update scripts when initialScripts change (e.g., after refresh)
  if (initialScripts !== scripts && initialScripts.length !== scripts.length) {
    setScripts(initialScripts);
  }

  const emptyState = searchQuery ? (
    <div className="py-12 text-center">
      <div className="mb-4 text-6xl">🔍</div>
      <h3 className="mb-2 text-xl font-semibold text-white">No scripts found for {searchQuery}</h3>
      <p className="text-gray-400">Try adjusting your search terms or create a new script.</p>
    </div>
  ) : undefined;

  return (
    <>
      {isError && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
          <div className="flex items-center justify-between">
            <p className="text-red-400">Error: {error?.message || 'Failed to load scripts'}</p>
            <button
              onClick={() => window.location.reload()}
              className="ml-4 rounded bg-red-500/20 px-3 py-1 text-sm text-red-400 hover:bg-red-500/30"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      <ScriptList scripts={scripts} actions={actions} loading={false} emptyState={emptyState} />
    </>
  );
}
