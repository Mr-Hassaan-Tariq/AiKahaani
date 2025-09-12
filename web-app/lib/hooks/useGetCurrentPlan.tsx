'use client';

import { useQuery } from '@tanstack/react-query';

import { getClientDataAction } from 'lib/utils/clientDataActions';

async function getCurrentPlan() {
  return await getClientDataAction<CurrentPlanType>('v1/payments/subscription/');
}

export default function useGetCurrentPlan() {
  return useQuery({
    queryKey: ['get-current-plan'],
    queryFn: () => getCurrentPlan(),
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 60 * 1, // 1 hours
  });
}

export interface CurrentPlanType {
  subscription?: null | unknown;
  id: string;
  user: number;
  start_date: string;
  end_date: string;
  plan: {
    id: string;
    product: {
      name: string;
      metadata: {
        billing_cycle: string;
        features: string;
        plan_type: string;
        sort_order: string;
        trial_days: string;
      };
    };
    amount: string;
    plan_type: string;
    billing_cycle: string;
    price: number;
    display_price: string;
    yearly_price: number;
    monthly_price: number;
    features: string;
    is_active: boolean;
    trial_days: number;
    description: string;
    sort_order: number;
    created: string;
    modified: string;
  };

  stripe_subscription_id: string | null;
  stripe_customer_id: string | null;
  status: string;
  current_period_start: string;
  current_period_end: string;
  trial_start: string;
  trial_end: string;
  canceled_at: string | null;
  cancel_at_period_end: boolean;
  is_active: boolean;
  is_trial: boolean;
  days_until_expiry: number;
  trial_days_remaining: number;
  trial_expiration_date: string;
  created: string;
  modified: string;
}
