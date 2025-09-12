import Link from 'next/link';
import { ManageSubscriptionButton } from '@/(dashboard)/_components/ManageSubscriptionButton';
import dayjs from 'dayjs';
import { env } from 'env.mjs';
import { CircleCheck } from 'lucide-react';

import { getCurrentPlan } from './actions';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default async function Page() {
  const { data, isError, error } = await getCurrentPlan();
  if (isError) {
    return (
      <div className="flex h-full w-full items-center justify-center text-lg text-white">
        Error: {error.message}
      </div>
    );
  }

  if (!data.subscription === null) {
    return (
      <div className="flex h-full w-full items-center justify-center text-lg text-white">
        No subscription found
      </div>
    );
  }
  const billingCycle = data?.plan?.product?.metadata.billing_cycle || data?.plan?.billing_cycle;
  const start = data?.start_date ? dayjs(data.start_date) : null;
  const computedEndDate = (() => {
    if (!start || !billingCycle) return null;
    if (billingCycle === 'weekly') return start.add(7, 'day');
    if (billingCycle === 'monthly') return start.add(1, 'month');
    if (billingCycle === 'yearly') return start.add(1, 'year');
    return null;
  })();

  const computedRemainingDays = (() => {
    if (!computedEndDate) return null;
    return computedEndDate.diff(dayjs(), 'day');
  })();
  return (
    <Card>
      <Col className="gap-8">
        <Row>
          <Text variant="3xl" className="capitalize text-white">
            {data?.plan?.product?.name}
          </Text>
          <Row className="items-end gap-1">
            <Text variant="3xl" className="text-white">
              ${data?.plan?.amount} /
            </Text>
            <Text variant="sm" className="mb-1 text-brand-secondary">
              {data?.plan?.product?.metadata.billing_cycle}
            </Text>
          </Row>
        </Row>

        <Col className="gap-4">
          <Text variant="lg" className="flex items-center gap-3 text-brand-secondary">
            Status: {dot} <p className="capitalize text-white">{data?.status}</p>
          </Text>
          <Text variant="lg" className="flex items-center gap-3 text-brand-secondary">
            Ends:{' '}
            <p className="text-white">
              {computedEndDate ? computedEndDate.format('MMMM DD, YYYY') : '-'}
            </p>
          </Text>
          <Row className="flex-col gap-6 lg:flex-row">
            <Text variant="lg" className="flex items-center gap-3 text-brand-secondary">
              Access:{' '}
              <p className="text-white">All tools unlocked for {computedRemainingDays} more days</p>
            </Text>
            <Row>
              <Link href={'#'}>
                <ManageSubscriptionButton />
              </Link>
              {data?.plan?.plan_type !== 'pro' && (
                <Link href={env.NEXT_PUBLIC_STRIPE_PORTAL_LINK}>
                  <Button height={41}>Upgrade plan</Button>
                </Link>
              )}
            </Row>
          </Row>
        </Col>

        <Card className="rounded-xl border-[#BAFF3812] bg-white/10 px-4 py-4 shadow-[0_0_4px_0_rgba(0,0,0,0.04),0_8px_16px_0_rgba(0,0,0,0.08)] lg:px-4 lg:py-4">
          <Col className="gap-5">
            <Text variant="base" className="font-bold leading-5 text-white">
              You currently have full access to all tools. Once your trial ends, you’ll lose access
              to:
            </Text>
            <Col className="gap-4">
              {data?.plan?.product?.metadata?.features &&
                Object.keys(JSON.parse(data?.plan?.product?.metadata?.features ?? [])).map((e) => (
                  <Row key={e} className="justify-normal gap-2">
                    <CircleCheck size={20} className="text-white" />
                    <Text variant="sm" className="capitalize text-white">
                      {e?.replace(/_/g, ' ')}
                    </Text>
                  </Row>
                ))}
            </Col>
            {data.trial_start && (
              <Text variant="base" className="font-bold leading-5 text-white">
                Upgrade to keep your work and continue using TubeGenius.
              </Text>
            )}
          </Col>
        </Card>
      </Col>
    </Card>
  );
}

const dot = (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none">
    <circle cx="6" cy="6" r="6" fill="#00B559" />
  </svg>
);
