import { headers } from 'next/headers';
import Link from 'next/link';

import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Tabs, TabsList, TabsTrigger } from 'components/shadcn_ui/tabs';

const tabsPath = [
  { label: 'Profile', path: '/settings/profile' },
  { label: 'Notifications', path: '/settings/notifications' },
  { label: 'Subscription Plan', path: '/settings/subscription-plan' },
  { label: 'Privacy & Security', path: '/settings/privacy-security' },
] as const;

export default async function SettingTabs({ children }: { children: React.ReactNode }) {
  const headersList = await headers();
  const pathname = headersList.get('current_page');
  const activeTab = tabsPath.find((tab) => pathname?.includes(tab.path));

  return (
    <div className="flex grow flex-col gap-10">
      <Row className="flex-col items-start justify-normal gap-6 lg:flex-row lg:items-center lg:justify-between">
        <Text variant="3xl" className="text-[32px] font-semibold text-white">
          Settings
        </Text>
        <div className="w-full overflow-x-auto overflow-y-visible lg:w-fit">
          <Tabs defaultValue={activeTab?.label || ''} className="min-w-[550px]">
            <TabsList className="flex h-[52px] w-full items-center justify-normal gap-1.5 bg-transparent md:justify-normal md:gap-4 lg:h-fit">
              {tabsPath.map((tab) => (
                <Link key={tab.label} href={tab.path}>
                  <TabsTrigger
                    value={tab.label}
                    className="whitespace-nowrap rounded-full border-gray-100 bg-[#FFFFFF1A] px-3 py-3 text-base font-bold text-white data-[state=active]:bg-white data-[state=active]:text-black lg:px-6 lg:py-[18px]"
                  >
                    {tab.label}
                  </TabsTrigger>
                </Link>
              ))}
            </TabsList>
          </Tabs>
        </div>
      </Row>

      <div className="scrollbar pb-3">{children}</div>
    </div>
  );
}
