'use client';

import { Dispatch, SetStateAction, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import dayjs from 'dayjs';
import { ChevronDown, ChevronRight, CircleCheck, CircleX, Info } from 'lucide-react';

import Button from './Button';
import Card from './Card';
import Col from './Col';
import Dialog from './Dialog';
import PageLoader from './PageLoader';
import Row from './Row';
import Text from './Text';
import useCreateBillingPortal from 'lib/hooks/useBIllingPortal';
import useCreateStripeSession from 'lib/hooks/useCreateStripeSession';
import useGetAllPlan, { PlanType } from 'lib/hooks/useGetAllPlan';
import useGetCurrentPlan from 'lib/hooks/useGetCurrentPlan';
import { cn } from 'lib/utils';
import useToast from 'lib/utils/useToast';
import ExternalLinkIcon from 'components/icons/ExternalLinkIcon';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';
import { Separator } from 'components/shadcn_ui/separator';
import { Skeleton } from 'components/shadcn_ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from 'components/shadcn_ui/tabs';

interface PlanUpgradeModalProps {
  align?: 'center' | 'start' | 'end';
}

const BYPASS_PAYMENT = process.env.NEXT_PUBLIC_BYPASS_PAYMENT_CHECKS === 'true';

export default function PlanUpgradeModal({ align = 'center' }: PlanUpgradeModalProps) {
  const toast = useToast();
  const router = useRouter();
  const [openPopover, setOpenPopover] = useState(false);
  const [open, setOpen] = useState(false);
  const [openAllPlans, setOpenAllPlans] = useState(false);
  const { data, isLoading, isError, error } = useGetCurrentPlan();

  if (BYPASS_PAYMENT) return null;

  const { isPending, mutate: createStripeSession } = useCreateStripeSession();
  const { mutate: createBillingPortal } = useCreateBillingPortal();

  useEffect(() => {
    if (isError) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      if ((error as any)?.error === 'No subscription found') {
        setOpenPopover(true);
        setOpen(true);
        return toast.error('You are not on any plan', 'Please upgrade to a plan');
      }

      // toast.error('Something went wrong', error.message);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isError, toast, isLoading]);

  const handleUpgrade = async (plan_id: string) => {
    createStripeSession(plan_id as never, {
      onSuccess: (data) => {
        window.location.href = data.url;
      },

      onError: (error) => {
        toast.error('Something went wrong', error.message);
      },
    });
  };

  const billingCycle = data?.plan?.product?.metadata.billing_cycle || data?.plan?.billing_cycle;
  const start = data?.current_period_start
    ? dayjs(data.current_period_start)
    : data?.start_date
      ? dayjs(data.start_date)
      : null;
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

  const headingText = () => {
    if (computedRemainingDays !== null && computedRemainingDays <= 3) {
      return {
        heading: `Your  ${data?.plan?.product.name} ending soon `,
        subheading: `You'r plan will be automatically renewed on \n${computedEndDate?.format('MMMM DD, YYYY')}.`,
      };
    } else if (data?.end_date) {
      return {
        heading: `Your ${data?.plan?.product.name} has expired`,
        subheading: `Your access is limited.
      Renew or upgrade to continue using all tools.`,
      };
    }
    return {
      heading: `You're currently on a ${data?.plan?.product.name}`,
      subheading: 'Billed monthly via Stripe.',
    };
  };
  useEffect(() => {
    if (!isLoading && !isError && !data?.plan?.product?.name) {
      setOpen(true);
    }
  }, [isLoading, isError, data]);

  // If no plan data, show the ViewTrialPlanModal directly
  if (!isLoading && !isError && !data?.plan?.product?.name) {
    return (
      <>
        <ViewTrialPlanModal
          open={open}
          setOpen={() => {}}
          handleUpgrade={handleUpgrade}
          onOpenAllPlans={() => {
            setOpenAllPlans(true);
          }}
          trigger={
            <div className="group flex h-8 min-w-20 cursor-pointer items-center justify-center gap-3 rounded-full border border-[#BAFF38]/[.12] bg-white/[.16] px-2 text-sm capitalize">
              Not Activated{' '}
              <ChevronDown
                size={20}
                className="text-white transition-all duration-500 group-data-[state=open]:rotate-180"
              />
            </div>
          }
        />
        <ViewAllPlanModal
          open={openAllPlans}
          setOpen={setOpenAllPlans}
          handleUpgrade={handleUpgrade}
          trigger={<div />}
        />
      </>
    );
  }

  return (
    <Popover open={openPopover} onOpenChange={setOpenPopover}>
      {isPending && <PageLoader size="2xl" color="white" />}
      {isLoading ? (
        <Skeleton className="h-8 w-20 rounded-full" />
      ) : (
        <PopoverTrigger asChild>
          <div className="group flex h-8 min-w-20 cursor-pointer items-center justify-center gap-3 rounded-full border border-[#BAFF38]/[.12] bg-white/[.16] px-2 text-sm capitalize">
            {data?.plan?.product.name || 'Not Activated'}{' '}
            <ChevronDown
              size={20}
              className="text-white transition-all duration-500 group-data-[state=open]:rotate-180"
            />
          </div>
        </PopoverTrigger>
      )}

      <PopoverContent
        className="z-50 w-full rounded-xl border border-[#BAFF38]/[.12] bg-white/10 p-6 backdrop-blur-lg sm:w-96"
        align={align}
      >
        <Col className="items-center gap-6">
          <Col className="items-center gap-3">
            <Text variant="xl" className="text-center font-semibold text-white">
              {data?.plan?.product.name ? headingText()?.heading : 'You are not on any plan'}
            </Text>
            <Text
              className="whitespace-pre-line text-center leading-tight text-[#AAACA6]"
              variant="sm"
            >
              {data?.plan?.product.name ? headingText()?.subheading : 'You are not on any plan'}
            </Text>
          </Col>
          <Col className="gag-4 w-full">
            <p
              onClick={() =>
                createBillingPortal(undefined, {
                  onSuccess: (data) => {
                    router.push(data);
                  },
                })
              }
            >
              <Button fullRounded>Upgrade now</Button>
            </p>
            <ViewAllPlanModal
              open={open}
              setOpen={(value) => {
                setOpen(value);
              }}
              handleUpgrade={handleUpgrade}
              trigger={
                <Button variant="ghost" className="mx-auto w-fit">
                  <Row className="cursor-pointer justify-center gap-2 hover:opacity-75">
                    <Text variant="sm" className="font-semibold text-white">
                      View all plans
                    </Text>
                    <ExternalLinkIcon />
                  </Row>
                </Button>
              }
            />
          </Col>
        </Col>
      </PopoverContent>
    </Popover>
  );
}

type ViewAllPlanModalProps = {
  open: boolean;
  setOpen: Dispatch<SetStateAction<boolean>>;
  trigger: React.ReactNode;
  handleUpgrade: (plan_id: string) => void;
};
type ViewTrialPlanModalProps = {
  open: boolean;
  setOpen: Dispatch<SetStateAction<boolean>>;
  trigger: React.ReactNode;
  handleUpgrade: (plan_id: string) => void;
  onOpenAllPlans?: () => void;
};
export function ViewTrialPlanModal({
  trigger,
  handleUpgrade,
  open,
  setOpen,
  onOpenAllPlans,
}: ViewTrialPlanModalProps) {
  const toast = useToast();
  const { data, isLoading, isError, error } = useGetAllPlan({ enabled: open });

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong', error.message);
    }
  }, [isError, toast, error, data]);

  const trialData = useMemo(() => data?.filter((e) => e.name === 'Free Trial'), [data]);

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Welcome to TubeGenius!"
      description="Your journey to smarter content creation starts now!"
      className="sm:max-w-[983px] lg:max-w-[680px]"
      closeActionButton={null}
      outsideInteract={false}
    >
      <Col className="mt-4 w-full items-center gap-8">
        {isLoading ? (
          <Skeleton className="h-[452px] w-full bg-white/[.05]" />
        ) : Number(data?.length) > 0 ? (
          <Tabs defaultValue="monthly" className="flex w-full flex-col gap-6">
            <TrailWidget
              data={trialData}
              isTrial={true}
              handleUpgrade={handleUpgrade}
              onOpenAllPlans={onOpenAllPlans}
            />
          </Tabs>
        ) : (
          <Text variant="base" className="flex h-24 items-center justify-center text-white">
            No plans found
          </Text>
        )}
      </Col>
    </Dialog>
  );
}

export function ViewAllPlanModal({ trigger, handleUpgrade, open, setOpen }: ViewAllPlanModalProps) {
  const toast = useToast();
  const { data, isLoading, isError, error } = useGetAllPlan({ enabled: open });

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong', error.message);
    }
  }, [isError, toast, error, data]);

  const monthlyData = useMemo(() => data?.filter((e) => e.billing_cycle === 'monthly'), [data]);
  const yearlyData = useMemo(() => data?.filter((e) => e.billing_cycle === 'yearly'), [data]);

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Choose the plan that fits your needs"
      className="sm:max-w-[983px]"
    >
      <Col className="mt-4 w-full items-center gap-8">
        {isLoading ? (
          <Skeleton className="h-[452px] w-full bg-white/[.05]" />
        ) : Number(data?.length) > 0 ? (
          <Tabs defaultValue="monthly" className="flex w-full flex-col gap-6">
            <TabsList className="flex flex-row gap-6 bg-transparent">
              {monthlyData && (
                <TabsTrigger
                  value="monthly"
                  className="h-[52px] w-fit rounded-full bg-white/10 px-6 py-4 backdrop-blur-[2px] hover:bg-white/10 hover:opacity-70"
                >
                  Monthly
                </TabsTrigger>
              )}
              {yearlyData && (
                <TabsTrigger
                  value="yearly"
                  className="relative h-[52px] w-fit rounded-full bg-white/10 px-6 py-4 backdrop-blur-[2px] hover:bg-white/10 hover:opacity-70"
                >
                  <div className="absolute -right-10 -top-3 z-50 flex items-center justify-center rounded-md border border-[#BAFF38]/[.12] bg-white/10 p-2 text-xs leading-[14px] text-white shadow-[0_0_4px_0_rgba(0,0,0,0.04),0_8px_16px_0_rgba(0,0,0,0.08)] backdrop-blur-md">
                    Save 20%
                  </div>
                  Yearly
                </TabsTrigger>
              )}
            </TabsList>
            <TabsContent value="monthly" className="max-w-[90vw] overflow-hidden overflow-x-auto">
              <TrailWidget data={monthlyData} handleUpgrade={handleUpgrade} />
            </TabsContent>
            <TabsContent value="yearly" className="max-w-[90vw] overflow-hidden overflow-x-auto">
              <TrailWidget data={yearlyData} handleUpgrade={handleUpgrade} />
            </TabsContent>
          </Tabs>
        ) : (
          <Text variant="base" className="flex h-24 items-center justify-center text-white">
            No plans found
          </Text>
        )}
      </Col>
    </Dialog>
  );
}

const cardCss =
  'rounded-xl h-full lg:h-[475px]  border-[#BAFF3812] bg-white/10 px-6 py-6 shadow-[0_0_4px_0_rgba(0,0,0,0.04),0_8px_16px_0_rgba(0,0,0,0.08)] lg:px-6 lg:py-6';
const trailIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
    <path
      d="M15.3899 4.89009C15.5156 5.01592 15.6726 5.10594 15.8446 5.15089C16.0167 5.19583 16.1977 5.19406 16.3689 5.14577C16.54 5.09747 16.6952 5.00439 16.8185 4.87613C16.9417 4.74787 17.0285 4.58906 17.0699 4.41609C17.1737 3.98399 17.3908 3.58736 17.6988 3.26707C18.0069 2.94677 18.3947 2.71437 18.8225 2.59381C19.2502 2.47325 19.7023 2.46888 20.1323 2.58116C20.5623 2.69343 20.9546 2.91829 21.2688 3.23258C21.5829 3.54687 21.8077 3.93922 21.9198 4.36924C22.0319 4.79926 22.0274 5.25139 21.9067 5.67908C21.786 6.10677 21.5535 6.49456 21.2331 6.8025C20.9127 7.11045 20.516 7.32743 20.0839 7.43109C19.9109 7.47249 19.7521 7.55927 19.6238 7.68249C19.4956 7.80571 19.4025 7.96091 19.3542 8.13208C19.3059 8.30326 19.3041 8.48422 19.3491 8.65631C19.394 8.8284 19.484 8.98539 19.6099 9.11109L21.2929 10.7931C21.517 11.0173 21.6949 11.2834 21.8162 11.5763C21.9375 11.8691 22 12.1831 22 12.5001C22 12.8171 21.9375 13.131 21.8162 13.4239C21.6949 13.7168 21.517 13.9829 21.2929 14.2071L19.6099 15.8901C19.4842 16.0159 19.3272 16.1059 19.1551 16.1509C18.983 16.1958 18.802 16.1941 18.6309 16.1458C18.4597 16.0975 18.3045 16.0044 18.1813 15.8761C18.058 15.7479 17.9713 15.5891 17.9299 15.4161C17.8261 14.984 17.609 14.5874 17.3009 14.2671C16.9928 13.9468 16.605 13.7144 16.1773 13.5938C15.7495 13.4733 15.2974 13.4689 14.8674 13.5812C14.4374 13.6934 14.0451 13.9183 13.731 14.2326C13.4168 14.5469 13.1921 14.9392 13.0799 15.3692C12.9678 15.7993 12.9723 16.2514 13.093 16.6791C13.2137 17.1068 13.4462 17.4946 13.7666 17.8025C14.087 18.1104 14.4837 18.3274 14.9159 18.4311C15.0888 18.4725 15.2476 18.5593 15.3759 18.6825C15.5042 18.8057 15.5972 18.9609 15.6455 19.1321C15.6938 19.3033 15.6956 19.4842 15.6507 19.6563C15.6057 19.8284 15.5157 19.9854 15.3899 20.1111L13.7069 21.7931C13.4827 22.0173 13.2166 22.1951 12.9237 22.3164C12.6308 22.4377 12.3169 22.5002 11.9999 22.5002C11.6828 22.5002 11.3689 22.4377 11.076 22.3164C10.7831 22.1951 10.517 22.0173 10.2929 21.7931L8.60986 20.1101C8.48416 19.9843 8.32717 19.8942 8.15508 19.8493C7.983 19.8043 7.80204 19.8061 7.63086 19.8544C7.45968 19.9027 7.30448 19.9958 7.18126 20.124C7.05804 20.2523 6.97126 20.4111 6.92986 20.5841C6.82606 21.0162 6.60895 21.4128 6.3009 21.7331C5.99284 22.0534 5.60498 22.2858 5.17725 22.4064C4.74952 22.5269 4.29738 22.5313 3.86741 22.419C3.43743 22.3067 3.04515 22.0819 2.73096 21.7676C2.41678 21.4533 2.19205 21.061 2.07992 20.6309C1.96779 20.2009 1.9723 19.7488 2.09301 19.3211C2.21371 18.8934 2.44623 18.5056 2.76663 18.1977C3.08703 17.8897 3.48373 17.6728 3.91586 17.5691C4.08884 17.5277 4.24764 17.4409 4.3759 17.3177C4.50417 17.1945 4.59724 17.0393 4.64554 16.8681C4.69384 16.6969 4.6956 16.516 4.65066 16.3439C4.60572 16.1718 4.51569 16.0148 4.38986 15.8891L2.70686 14.2071C2.48269 13.9829 2.30486 13.7168 2.18354 13.4239C2.06222 13.131 1.99978 12.8171 1.99978 12.5001C1.99978 12.1831 2.06222 11.8691 2.18354 11.5763C2.30486 11.2834 2.48269 11.0173 2.70686 10.7931L4.38986 9.11009C4.51557 8.98426 4.67255 8.89423 4.84464 8.84929C5.01673 8.80435 5.19769 8.80612 5.36887 8.85441C5.54005 8.90271 5.69524 8.99579 5.81846 9.12405C5.94168 9.25231 6.02847 9.41111 6.06986 9.58409C6.17367 10.0162 6.39078 10.4128 6.69883 10.7331C7.00688 11.0534 7.39475 11.2858 7.82248 11.4064C8.25021 11.5269 8.70234 11.5313 9.13232 11.419C9.5623 11.3067 9.95458 11.0819 10.2688 10.7676C10.5829 10.4533 10.8077 10.061 10.9198 9.63094C11.0319 9.20092 11.0274 8.74879 10.9067 8.3211C10.786 7.89341 10.5535 7.50562 10.2331 7.19767C9.91269 6.88973 9.516 6.67275 9.08386 6.56909C8.91089 6.52769 8.75208 6.44091 8.62382 6.31769C8.49556 6.19447 8.40248 6.03927 8.35419 5.86809C8.30589 5.69692 8.30412 5.51596 8.34906 5.34387C8.39401 5.17178 8.48403 5.01479 8.60986 4.88909L10.2929 3.20709C10.517 2.98291 10.7831 2.80509 11.076 2.68377C11.3689 2.56244 11.6828 2.5 11.9999 2.5C12.3169 2.5 12.6308 2.56244 12.9237 2.68377C13.2166 2.80509 13.4827 2.98291 13.7069 3.20709L15.3899 4.89009Z"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

interface TrailWidgetProps {
  data?: PlanType[];
  handleUpgrade: (plan_id: string) => void;
  isTrial?: boolean;
  onOpenAllPlans?: () => void;
}

function TrailWidget({ data, handleUpgrade, isTrial = false, onOpenAllPlans }: TrailWidgetProps) {
  return (
    <>
      <Row className="scrollbar-hide scroll-fade-x w-full gap-6 overflow-clip overflow-x-auto">
        {data &&
          data.map(
            (e, index) =>
              e?.features.length && (
                <Card key={index} className={cn(cardCss, 'hover:bg-white/[.16 ] min-w-[300px]')}>
                  <Col className="h-fit gap-6">
                    <Col className="gap-4">
                      {e?.description && (
                        <div className="flex w-fit items-center justify-center rounded-md border border-[#BAFF38]/[.12] bg-white/10 p-2 text-[10px] leading-[14px] text-white shadow-[0_0_4px_0_rgba(0,0,0,0.04),0_8px_16px_0_rgba(0,0,0,0.08)] backdrop-blur-md md:text-xs">
                          {/* Try TubeGenius for 7 days — just $1 */}
                          {e?.description}
                        </div>
                      )}
                      <Row>
                        <Row>
                          {trailIcon}
                          <Text variant="2xl" className="text-lg text-white lg:text-2xl">
                            {e?.name}
                          </Text>
                        </Row>
                        <Row className="items-end gap-1">
                          <Text variant="3xl" className="text-lg text-white lg:text-2xl">
                            ${e?.price} /
                          </Text>
                          <Text variant="sm" className="mb-1 text-brand-secondary">
                            {e?.billing_cycle}
                          </Text>
                        </Row>
                      </Row>
                    </Col>

                    <Separator className="w-full bg-white/[.16]" />

                    <div className="relative">
                      <Col
                        className="scrollbar-hide h-32 gap-4 overflow-y-auto"
                        id="featuresScroll"
                      >
                        {e?.features &&
                          Object.keys(JSON.parse(e?.features)).map((feature: string) => (
                            <Row key={feature} className="justify-normal gap-2">
                              {JSON.parse(e?.features)[feature] ? (
                                <CircleCheck size={24} className="text-[#00B559]" />
                              ) : (
                                <CircleX size={24} className="text-[#FF5050]" />
                              )}
                              <Text variant="base" className="capitalize text-white">
                                {feature?.replace(/_/g, ' ')}
                              </Text>
                            </Row>
                          ))}
                      </Col>
                    </div>

                    <Separator className="w-full bg-white/[.16]" />

                    {isTrial && (
                      <Row className="justify-normal gap-2 text-white">
                        <Info size={16} />
                        <Text variant="xs">Note: Auto-upgrades to Basic plan after trial ends</Text>
                      </Row>
                    )}

                    {!isTrial && (
                      <Button
                        className="mt-auto"
                        onClick={() => e?.id && handleUpgrade(e.id as string)}
                      >
                        Upgrade now
                      </Button>
                    )}

                    {isTrial && (
                      <Row className="mt-auto gap-3">
                        <Button variant="gray" className="flex-1 bg-black" onClick={onOpenAllPlans}>
                          <Row className="md:text-md items-center gap-2 text-sm">
                            Other Plans <ChevronRight />
                          </Row>
                        </Button>
                        <Button
                          className="md:text-md flex-1 text-sm"
                          onClick={() => e?.id && handleUpgrade(e.id as string)}
                        >
                          Start trial for $1
                        </Button>
                      </Row>
                    )}
                  </Col>
                </Card>
              ),
          )}
      </Row>
      {isTrial && (
        <p className="text-center text-[12px] text-white">
          After 7 days, your plan will automatically continue as the Premium ($45/month){' '}
          <span className="text-[#2BFF13]">Terms & Conditions↗</span>
        </p>
      )}
    </>
  );
}
