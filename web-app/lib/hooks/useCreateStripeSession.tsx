'use client';

import { useMutation } from '@tanstack/react-query';

async function createStripeSession(item: { name: string; price: number }) {
  try {
    const response = await fetch('/api/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item }),
    });

    if (!response.ok) {
      throw new Error('Failed to create checkout session');
    }

    return await response.json();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (err: any) {
    throw new Error(err.message);
  }
}

export default function useCreateStripeSession() {
  return useMutation({ mutationFn: createStripeSession });
}
