import { useEffect } from 'react';
import EmptyState from '@/(dashboard)/_components/EmptyState';
import Icon from '@assets/svg/document-list.svg';

import { EMPTY_STATES } from '../_constants';
import { useScripts } from '../_hooks/useScripts';
import ScriptList from './ScriptList';

export default function ScriptsPage() {
  const { filteredScripts, searchQuery, actions, loading, refetch, setSelectedMode } = useScripts({
    useAPI: true,
    onScriptUpdate: (updatedScripts) => {
      console.log('Scripts updated:', updatedScripts);
    },
  });

  // Ensure API is filtered to scripts on mount
  useEffect(() => {
    setSelectedMode('script');
    refetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ScriptList
      scripts={filteredScripts}
      actions={actions}
      loading={loading}
      emptyState={
        searchQuery ? (
          <EmptyState
            icon={Icon}
            title={EMPTY_STATES.scripts.title}
            description={EMPTY_STATES.scripts.description}
          />
        ) : undefined
      }
    />
  );
}
