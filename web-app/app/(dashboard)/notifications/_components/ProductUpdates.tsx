'use client';

import Icon from '@assets/svg/screen-cursor-sparkles.svg';

import EmptyState from './EmptyState';

export default function ProductUpdatesPage() {
  return (
    <div className="mx-auto">
      <EmptyState
        icon={Icon}
        title="No product updates right now"
        description="We’ll let you know when something new drops. In the meantime, check out what’s already available!"
      />
    </div>
  );
}
