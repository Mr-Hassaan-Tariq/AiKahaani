import Image from 'next/image';
import Link from 'next/link';
import mainLogo from '@assets/sidebar/mainLogo.png';

import DesktopMenu from './_components/DesktopMenu';
import { MobileDrawer } from './_components/Drawer';
import { Dropdown } from './_components/DropdownMenu';
import MobileMenu from './_components/MobileMenu';
import { getNotifications, getUserProfile } from './actions';
import ClientImage from 'components/ui/ClientImage';
import PlanUpgradeModal from 'components/ui/PlanUpgradeModal';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data } = await getUserProfile();

  const { data: notify } = await getNotifications();
  const notifications = Array.isArray(notify) ? notify : notify ? [notify] : [];
  const getInitials = (name?: string, username?: string) => {
    const base = name || username || '';
    if (!base) return 'U';
    const parts = base.trim().split(' ');
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  };

  const initials = getInitials(data?.fullname, data?.username);

  return (
    <div className="h-[100dvh] min-h-screen w-full bg-[#0E0F0C]">
      <div className="mx-auto flex">
        {/* Desktop Sidebar */}
        <div className="hidden h-screen lg:block lg:w-[265px]">
          <DesktopMenu />
        </div>

        {/* Mobile Top Navigation */}
        <div className="fixed left-0 right-0 top-0 z-40 border-b border-gray-800 bg-[#0E0F0C] px-4 py-3 lg:hidden">
          <div className="flex items-center justify-between text-white">
            <Row className="w-full justify-between">
              <Link href="/">
                <Image src={mainLogo} alt="mainLogo" className="object-cover" />
              </Link>
              <Row className="items-center gap-4">
                <MobileDrawer />
                {data?.profile_picture ? (
                  <ClientImage
                    src={data.profile_picture}
                    alt="DP"
                    width={100}
                    height={100}
                    priority={true}
                    className="h-8 w-8 rounded-full bg-gray-600 object-cover"
                  />
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-600 text-xs font-bold text-white">
                    {initials}
                  </div>
                )}
                <MobileMenu />
              </Row>
            </Row>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="scrollbar max-h-screen min-h-screen w-full overflow-y-auto">
          {/* Sticky Navbar */}
          <Row className="sticky top-0 z-50 hidden h-20 w-full items-center justify-between rounded-br-3xl border-b border-[#BAFF381F] bg-[#161616]/80 px-8 text-white backdrop-blur-lg lg:flex">
            <Text variant="base" className="flex gap-4 text-white">
              Plan:
              <PlanUpgradeModal align="start" />
            </Text>

            <Row className="items-center gap-3">
              <Dropdown notifications={notifications || []} />

              {data?.profile_picture ? (
                <ClientImage
                  src={data.profile_picture}
                  alt="DP"
                  width={100}
                  height={100}
                  priority={true}
                  className="h-10 w-10 rounded-full bg-gray-600 object-cover"
                />
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-600 text-sm font-bold text-white">
                  {initials}
                </div>
              )}
              <Text variant="base" className="text-white">
                {data?.fullname || data?.username || ''}
              </Text>
            </Row>
          </Row>

          {/* Content */}
          <div className="relative">
            <div className="mx-auto mt-14 max-h-full min-h-[87.8dvh] max-w-screen-2xl px-4 py-10 lg:mt-0 lg:px-20 lg:py-16">
              <div className="relative z-10">{children}</div>
              <div className="absolute bottom-0 right-0 z-0 rotate-180 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)]">
                <Image
                  src={'/BgGrid.svg'}
                  width={2000}
                  height={2000}
                  alt="bottomLogo"
                  className="h-full w-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
