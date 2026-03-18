'use client';

import useGetCurrentPlan from 'lib/hooks/useGetCurrentPlan';

export default function CreditsCard() {
  const { data, isLoading } = useGetCurrentPlan();

  const planName = data?.plan?.product?.name ?? 'Free';
  const daysLeft = data?.days_until_expiry ?? 0;
  const isActive = data?.is_active ?? false;
  const isTrial  = data?.is_trial  ?? false;

  // Progress: days remaining out of ~30
  const totalDays = 30;
  const usedDays  = Math.max(0, totalDays - daysLeft);
  const pct       = Math.min((usedDays / totalDays) * 100, 100);

  if (isLoading) {
    return (
      <div className="rounded-lg bg-muted p-3 animate-pulse">
        <div className="h-2.5 w-24 rounded bg-border mb-2" />
        <div className="h-1.5 w-full rounded-full bg-border mb-2" />
        <div className="h-2 w-32 rounded bg-border" />
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-muted p-3">
      {/* Header row */}
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-xs font-semibold text-foreground">
          {isTrial ? 'Trial period' : planName}
        </span>
        <span className="text-xs text-muted-foreground">
          {daysLeft}d left
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-2 h-1.5 w-full overflow-hidden rounded-full bg-border">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Status note */}
      <p className="text-xs leading-relaxed text-muted-foreground">
        {isActive
          ? `${daysLeft} days remaining on your ${planName} plan.`
          : 'Your plan is inactive. Upgrade to continue.'}
      </p>
    </div>
  );
}
