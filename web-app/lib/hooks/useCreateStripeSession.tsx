'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

// async function createStripeSession(item: { name: string; price: number }) {
//   try {
//     const response = await fetch('/api/create-checkout-session', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({ item }),
//     });

//     if (!response.ok) {
//       throw new Error('Failed to create checkout session');
//     }

//     return await response.json();
//     // eslint-disable-next-line @typescript-eslint/no-explicit-any
//   } catch (err: any) {
//     throw new Error(err.message);
//   }
// }

interface ResponseType {
  session_id: string;
  url: string;
}

// NOTE: Payment endpoints are not yet implemented in the backend.
// These will 404 until the payment integration is added.

async function createStripeSession(plan_id: string) {
  return await postClientDataAction<ResponseType, { plan_id: string }>(
    '/v1/payments/checkout/session',
    { plan_id },
  );
}

export default function useCreateStripeSession() {
  return useMutation({ mutationFn: createStripeSession });
}
