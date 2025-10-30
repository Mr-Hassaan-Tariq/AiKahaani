import Image from 'next/image';
import Link from 'next/link';
import mainLogo from '@assets/sidebar/mainLogo.png';

import DesktopMenu from './_components/DesktopMenu';
import { MobileDrawer } from './_components/Drawer';
import { Dropdown } from './_components/DropdownMenu';
import MobileMenu from './_components/MobileMenu';
import { getUserProfile } from './actions';
import ClientImage from 'components/ui/ClientImage';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data } = await getUserProfile();
  return (
    <div className="h-[100dvh] min-h-screen w-full overflow-hidden bg-[#0E0F0C]">
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
              <Row className="gap-4">
                <MobileDrawer />
                <ClientImage
                  src={data?.profile_picture || ''}
                  alt="DP"
                  width={100}
                  height={100}
                  priority={true}
                  className="h-8 w-8 rounded-full bg-gray-600 object-cover"
                />
                <MobileMenu />
              </Row>
            </Row>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="scrollbar max-h-screen min-h-screen w-full overflow-y-auto">
          <Row className="hidden h-20 w-full rounded-br-3xl border-b border-[#BAFF381F] bg-[#161616] px-8 text-white lg:flex">
            <p className="text-lg">Welcome back</p>
            <Row>
              <Dropdown />
              <ClientImage
                src={data?.profile_picture || ''}
                alt="DP"
                width={100}
                height={100}
                priority={true}
                className="h-10 w-10 rounded-full bg-gray-600 object-cover"
              />
              <Text variant="base" className="text-white">
                {data?.fullname || ''}
              </Text>
            </Row>
          </Row>

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
