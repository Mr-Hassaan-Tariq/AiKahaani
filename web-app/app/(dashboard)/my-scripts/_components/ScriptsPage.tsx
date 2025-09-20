'use client';

import EmptyState from '@/(dashboard)/_components/EmptyState';
import Icon from '@assets/svg/document-list.svg';

import { EMPTY_STATES } from '../_constants';
import { useScriptActions } from '../_hooks/useScriptActions';
import ScriptList from './ScriptList';
import { ScriptGeneration } from 'lib/api/types';

interface ScriptsPageProps {
  initialScripts?: ScriptGeneration[];
}

export default function ScriptsPage({ initialScripts = [] }: ScriptsPageProps) {
  const { actions } = useScriptActions();

  // Filter scripts to only show full scripts
  const scriptScripts = initialScripts.filter((script) => script.type === 'script');

  return (
    <ScriptList
      scripts={scriptScripts}
      actions={actions}
      loading={false}
      emptyState={
        <EmptyState
          icon={Icon}
          title={EMPTY_STATES.scripts.title}
          description={EMPTY_STATES.scripts.description}
        />
      }
    />
  );
}
