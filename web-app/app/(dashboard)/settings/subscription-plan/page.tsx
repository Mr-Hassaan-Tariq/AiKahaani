import dayjs from 'dayjs';
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

  return (
    <Card>
      <Col className="gap-8">
        <Row>
          <Text variant="3xl" className="capitalize text-white">
            {data?.plan.plan_type} plan
          </Text>
          <Row className="items-end gap-1">
            <Text variant="3xl" className="text-white">
              ${data?.plan.price} /
            </Text>
            <Text variant="sm" className="mb-1 text-brand-secondary">
              {data?.plan.billing_cycle}
            </Text>
          </Row>
        </Row>

        <Col className="gap-4">
          <Text variant="lg" className="flex items-center gap-3 text-brand-secondary">
            Status: {dot} <p className="capitalize text-white">{data?.status}</p>
          </Text>
          <Text variant="lg" className="flex items-center gap-3 text-brand-secondary">
            Ends:{' '}
            <p className="text-white">{dayjs(data?.current_period_end).format('MMMM DD, YYYY')}</p>
          </Text>
          <Row className="flex-col gap-6 lg:flex-row">
            <Text variant="lg" className="flex items-center gap-3 text-brand-secondary">
              Access: <p className="text-white">All tools unlocked for 7 more days</p>
            </Text>
            <Row className="w-full lg:w-fit">
              <Button variant="gray" className="whitespace-nowrap px-8" height={41}>
                Manage subscription
              </Button>
              {data.plan.plan_type !== 'pro' && <Button height={41}>Upgrade plan</Button>}
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
              {['Script Generator', 'Title & Niche Tools', 'Saved Scripts'].map((e) => (
                <Row key={e} className="justify-normal gap-2">
                  <CircleCheck size={20} className="text-white" />
                  <Text variant="sm" className="text-white">
                    {e}
                  </Text>
                </Row>
              ))}
            </Col>
            <Text variant="base" className="font-bold leading-5 text-white">
              Upgrade to keep your work and continue using TubeGenius.
            </Text>
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
