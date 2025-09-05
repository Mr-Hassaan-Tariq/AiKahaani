'use client';

import { useQuery } from '@tanstack/react-query';

import { getClientDataAction } from 'lib/utils/clientDataActions';

async function getTrailStatus() {
  return await getClientDataAction('v1/payments/user/trial-status/');
}

export default function useGetTrailStatus() {
  return useQuery({
    queryKey: ['get-trail-status'],
    queryFn: () => getTrailStatus(),
    retry: false,
    refetchOnWindowFocus: false,
  });
}
