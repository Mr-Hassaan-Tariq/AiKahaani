'use client';

import { useRouter } from 'next/navigation';

import useBillingPortal from 'lib/hooks/useBIllingPortal';
import { Button } from 'components/ui/Button';

export function ManageSubscriptionButton() {
  const router = useRouter();
  const mutation = useBillingPortal();

  return (
    <Button
      variant="outline"
      size="sm"
      loading={mutation.status === 'pending'}
      disabled={mutation.status === 'pending'}
      onClick={() =>
        mutation.mutate(undefined, {
          onSuccess: (url) => {
            router.push(url);
          },
          onError: (error: any) => {
            alert(error.message || 'Something went wrong.');
          },
        })
      }
    >
      {mutation.status === 'pending' ? 'Redirecting…' : 'Manage subscription'}
    </Button>
  );
}
