'use client';

import EmptyState from '@/(dashboard)/_components/EmptyState';
import Icon from '@assets/svg/document-list.svg';

import { EMPTY_STATES } from '../_constants';
import { useScriptActions } from '../_hooks/useScriptActions';
import ScriptList from './ScriptList';
import { ScriptGeneration } from 'lib/api/types';

interface OutlinesPageProps {
  initialScripts?: ScriptGeneration[];
}

export default function OutlinesPage({ initialScripts = [] }: OutlinesPageProps) {
  const { actions } = useScriptActions();

  // Filter scripts to only show outlines
  const outlineScripts = initialScripts.filter((script) => script.type === 'outline');

  return (
    <ScriptList
      scripts={outlineScripts}
      actions={actions}
      loading={false}
      emptyState={
        <EmptyState
          icon={Icon}
          title={EMPTY_STATES.outlines.title}
          description={EMPTY_STATES.outlines.description}
        />
      }
    />
  );
}
