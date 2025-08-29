'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { Tabs, TabsList, TabsTrigger } from 'components/shadcn_ui/tabs';

const tabsPath = [
  { label: 'All', path: '/notifications' },
  { label: 'Product Updates', path: '/notifications/product-updates' },
  { label: 'Subscription', path: '/notifications/subscription' },
] as const;

export default function NotificationTabs({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const activeTab = tabsPath.find((tab) => tab.path === pathname) ?? tabsPath[0];

  return (
    <div className="flex grow flex-col gap-7">
      <div className="w-full overflow-x-auto overflow-y-visible lg:w-fit">
        <Tabs defaultValue={activeTab.label} className="min-w-[550px]">
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
      <div className="scrollbar pb-3">{children}</div>
    </div>
  );
}
