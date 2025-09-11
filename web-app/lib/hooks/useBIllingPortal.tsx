'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

async function createBillingPortal() {
  const response = await postClientDataAction<{ url: string }, object>(
    'v1/payments/billing-portal/',
    {},
  );

  return response.url;
}

export default function useBillingPortal() {
  return useMutation({ mutationFn: createBillingPortal });
}
