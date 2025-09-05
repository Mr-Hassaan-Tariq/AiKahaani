'use client';

import { useRouter } from 'next/navigation';

import Button from 'components/ui/Button';

export default function SuccessPage() {
  const router = useRouter();
  return (
    <div>
      <div className="flex items-center justify-center text-white">
        <div className="text-center">
          {/* Title */}
          <h1 className="mt-4 text-2xl font-semibold">Payment Successful!</h1>

          {/* Subtitle */}
          <p className="mt-2 text-gray-500">Your payment has been completed.</p>

          <Button className="mt-5" onClick={() => router.push('/settings/subscription-plan')}>
            Finish
          </Button>
        </div>
      </div>
    </div>
  );
}
