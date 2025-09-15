import EmptyState from '@/(dashboard)/_components/EmptyState';
import Icon from '@assets/svg/document-list.svg';

import { EMPTY_STATES } from '../_constants';

export default function OutlinesPage() {
  return (
    <EmptyState
      icon={Icon}
      title={EMPTY_STATES.outlines.title}
      description={EMPTY_STATES.outlines.description}
    />
  );
}
