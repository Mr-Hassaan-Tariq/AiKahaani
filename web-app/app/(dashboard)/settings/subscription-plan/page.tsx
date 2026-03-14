'use client';

import { useState } from 'react';
import { ManageSubscriptionButton } from '@/(dashboard)/_components/ManageSubscriptionButton';
import dayjs from 'dayjs';
import { CircleCheck } from 'lucide-react';

import useCreateStripeSession from 'lib/hooks/useCreateStripeSession';
import useGetCurrentPlan from 'lib/hooks/useGetCurrentPlan';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';
import { ViewAllPlanModal } from 'components/ui/PlanUpgradeModal';
import { Spinner } from 'components/ui/Spinner';
import { cn } from 'lib/utils';

const STATUS_COLORS = {
  active: 'bg-success',
  expiring: 'bg-warning',
  expired: 'bg-destructive',
};

export default function Page() {
  const [openAllPlans, setOpenAllPlans] = useState(false);
  const toast = useToast();
  const { mutate: createStripeSession } = useCreateStripeSession();
  const { data, isLoading, isError, error } = useGetCurrentPlan();

  const handleUpgrade = async (plan_id: string) => {
    createStripeSession(plan_id as never, {
      onSuccess: (data) => { window.location.href = data.url; },
      onError: (error) => { toast.error('Something went wrong', error.message); },
    });
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[200px] items-center justify-center">
        <Spinner size="md" color="primary" />
      </div>
    );
  }

  if (isError) {
    return <p className="text-sm text-destructive">Error: {error?.message}</p>;
  }

  if (data?.subscription === null) {
    return <p className="text-sm text-muted-foreground">No subscription found.</p>;
  }

  const billingCycle = data?.plan?.product?.metadata?.billing_cycle || data?.plan?.billing_cycle;
  const start = data?.start_date ? dayjs(data.start_date) : null;
  const computedEndDate = (() => {
    if (!start || !billingCycle) return null;
    if (billingCycle === 'weekly') return start.add(7, 'day');
    if (billingCycle === 'monthly') return start.add(1, 'month');
    if (billingCycle === 'yearly') return start.add(1, 'year');
    return null;
  })();
  const remainingDays = computedEndDate ? computedEndDate.diff(dayjs(), 'day') : null;
  const statusKey =
    remainingDays !== null && remainingDays <= 3 ? 'expiring'
    : data?.end_date ? 'expired'
    : 'active';
  const statusLabel = statusKey === 'expiring' ? 'Expiring soon' : statusKey === 'expired' ? 'Expired' : 'Active';

  return (
    <div className="flex flex-col gap-5 max-w-2xl">
      {/* Plan header */}
      <div className="rounded-xl border border-border bg-card p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Current plan</p>
            <h3 className="mt-1 text-lg font-semibold capitalize text-foreground">
              {data?.plan?.product?.name}
            </h3>
            <p className="mt-0.5 text-sm text-muted-foreground">
              ${data?.plan?.amount}
              <span className="ml-0.5 text-xs capitalize">/ {billingCycle}</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <ManageSubscriptionButton />
            <Button size="sm" onClick={() => setOpenAllPlans(true)}>
              Upgrade plan
            </Button>
          </div>
        </div>

        {/* Status row */}
        <div className="mt-5 grid gap-3 border-t border-border pt-5 sm:grid-cols-3 text-sm">
          <div>
            <p className="text-xs text-muted-foreground">Status</p>
            <div className="mt-1 flex items-center gap-1.5">
              <span className={cn('h-2 w-2 rounded-full', STATUS_COLORS[statusKey])} />
              <span className="font-medium text-foreground">{statusLabel}</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Renews / Expires</p>
            <p className="mt-1 font-medium text-foreground">
              {computedEndDate ? computedEndDate.format('MMM D, YYYY') : '—'}
            </p>
          </div>
          {remainingDays !== null && (
            <div>
              <p className="text-xs text-muted-foreground">Access</p>
              <p className="mt-1 font-medium text-foreground">{remainingDays} days remaining</p>
            </div>
          )}
        </div>
      </div>

      {/* Features */}
      {data?.plan?.product?.metadata?.features && (
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="mb-4 text-sm font-semibold text-foreground">Plan includes</p>
          <div className="grid gap-2.5 sm:grid-cols-2">
            {Object.keys(JSON.parse(data.plan.product.metadata.features ?? '[]')).map((e) => (
              <div key={e} className="flex items-center gap-2">
                <CircleCheck className="h-4 w-4 shrink-0 text-success" />
                <span className="text-sm capitalize text-foreground">{e.replace(/_/g, ' ')}</span>
              </div>
            ))}
          </div>
          {data?.trial_start && (
            <p className="mt-4 text-xs text-muted-foreground">
              Upgrade to keep your work and continue using AiKahani.
            </p>
          )}
        </div>
      )}

      <ViewAllPlanModal
        open={openAllPlans}
        setOpen={setOpenAllPlans}
        handleUpgrade={handleUpgrade}
        trigger={<div />}
      />
    </div>
  );
}
