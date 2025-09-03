'use server';

import { CurrentPlanType } from 'lib/hooks/useGetCurrentPlan';
import { getServerDataAction } from 'lib/utils/getServerDataAction';

export async function getCurrentPlan() {
  return await getServerDataAction<CurrentPlanType>('v1/payments/subscription/');
}
