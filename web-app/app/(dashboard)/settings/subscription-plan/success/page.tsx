'use client';

import { useRouter } from 'next/navigation';
import { CircleCheck } from 'lucide-react';

import { Button } from 'components/ui/Button';

export default function SuccessPage() {
  const router = useRouter();
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
        <CircleCheck className="h-8 w-8 text-success" />
      </div>
      <div>
        <h1 className="text-xl font-semibold text-foreground">Payment Successful!</h1>
        <p className="mt-1 text-sm text-muted-foreground">Your subscription has been activated.</p>
      </div>
      <Button size="sm" onClick={() => router.push('/settings/subscription-plan')}>
        View subscription
      </Button>
    </div>
  );
}
