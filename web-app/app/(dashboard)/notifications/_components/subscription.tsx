'use client';

import Icon from '@assets/svg/card-sparkles.svg';

import EmptyState from '../../_components/EmptyState';

export default function SubscriptionPage() {
  return (
    <div>
      <EmptyState
        icon={Icon}
        title="No subscription updates yet"
        description="You'll see important updates here — like plan changes, billing reminders, or trial expiration alerts."
      />
    </div>
  );
}
