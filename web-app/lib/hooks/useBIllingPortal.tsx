'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

// NOTE: Payment endpoints are not yet implemented in the backend.

async function createBillingPortal() {
  const response = await postClientDataAction<{ url: string }, object>(
    '/v1/payments/billing-portal',
    {},
  );

  return (response as any)?.url ?? (response as any)?.data?.url;
}

export default function useBillingPortal() {
  return useMutation({ mutationFn: createBillingPortal });
}
