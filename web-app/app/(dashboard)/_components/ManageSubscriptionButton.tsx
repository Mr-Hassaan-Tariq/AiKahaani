'use client';

import { useRouter } from 'next/navigation';

import useBillingPortal from 'lib/hooks/useBIllingPortal';
import Button from 'components/ui/Button';

export function ManageSubscriptionButton() {
  const router = useRouter();
  const mutation = useBillingPortal();

  return (
    <Button
      variant="gray"
      className="whitespace-nowrap px-8"
      height={41}
      onClick={() =>
        mutation.mutate(undefined, {
          onSuccess: (url) => {
            router.push(url);
          },
          onError: (error: any) => {
            alert(error.message || 'Something went wrong while redirecting.');
          },
        })
      }
      disabled={mutation.status === 'pending'}
    >
      {mutation.status === 'pending' ? 'Redirecting...' : 'Manage subscription'}
    </Button>
  );
}
