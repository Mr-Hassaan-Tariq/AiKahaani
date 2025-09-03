'use client';

import { useQuery } from '@tanstack/react-query';

import { getClientDataAction } from 'lib/utils/clientDataActions';

async function getAllPlan() {
  return await getClientDataAction<PlanType[]>('v1/payments/plans/');
}

export default function useGetAllPlan({ enabled }: { enabled: boolean }) {
  return useQuery({
    queryKey: ['get-all-plan'],
    queryFn: () => getAllPlan(),
    retry: false,
    enabled,
  });
}

export interface PlanType {
  id: string;
  name: string;
  plan_type: 'trial' | 'basic' | 'pro';
  billing_cycle: 'weekly' | 'monthly' | 'yearly';
  price: string;
  display_price: string;
  yearly_price: number;
  monthly_price: number;
  features: string; // JSON string containing feature flags
  is_active: boolean;
  trial_days: number;
  description: string;
  sort_order: number;
  created: string; // ISO date string
  modified: string; // ISO date string
}
