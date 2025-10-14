'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import ComponentNav from '@/(dashboard)/_components/ComponentNav';
import { toast } from 'sonner'; // if you're using a toast library

import { RightCircle } from './components';
import { postClientDataAction } from 'lib/utils/clientDataActions';
import { Tabs, TabsList, TabsTrigger } from 'components/shadcn_ui/tabs';

const tabsPath = [
  { label: 'All', path: '/notifications' },
  { label: 'Product Updates', path: '/notifications?query=product-updates' },
  { label: 'Subscription', path: '/notifications?query=subscription' },
] as const;

export default function NotificationTabs({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);

  const query = searchParams.get('query');
  const activeTab =
    tabsPath.find((tab) => tab.path === pathname + '?query=' + query) ?? tabsPath[0];

  const handleMarkAllRead = async () => {
    try {
      setLoading(true);
      const response = await postClientDataAction('v1/notifications/read-all/');
      console.log('response', response);
      toast.success('All notifications marked as read');
    } catch (error) {
      console.error('Error marking notifications as read:', error);
      toast.error('Something went wrong!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex grow flex-col gap-5">
      <ComponentNav
        title="Notifications"
        buttonText={loading ? 'Marking...' : 'Mark all as read'}
        buttonIcon={RightCircle}
        _onButtonClick={handleMarkAllRead}
        disabled={loading}
      />
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
