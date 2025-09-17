import EmptyState from '@/(dashboard)/_components/EmptyState';
import Icon from '@assets/svg/document-list.svg';

import { EMPTY_STATES } from '../_constants';

export default function ScriptsPage() {
  return (
    <EmptyState
      icon={Icon}
      title={EMPTY_STATES.scripts.title}
      description={EMPTY_STATES.scripts.description}
    />
  );
}
