import Image from 'next/image';
import mainLogo from '@assets/sidebar/mainLogo.png';

import DesktopMenu from './_components/DesktopMenu';
import { Dropdown } from './_components/DropdownMenu';
import MobileMenu from './_components/MobileMenu';
import PlanUpgradeModal from 'components/ui/PlanUpgradeModal';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
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
              <Image src={mainLogo} alt="mainLogo" className="object-cover" />
              <Row className="gap-4">
                <div className="h-8 w-8 rounded-full bg-gray-600" />
                <MobileMenu />
              </Row>
            </Row>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="scrollbar max-h-screen min-h-screen w-full overflow-y-auto">
          <Row className="hidden h-20 w-full rounded-br-3xl border-b border-[#BAFF381F] bg-[#161616] px-8 text-white lg:flex">
            <Text variant="base" className="flex gap-4 text-white">
              Plan: <PlanUpgradeModal align="start" />
            </Text>

            <Row>
              <Dropdown />
              <div className="h-10 w-10 rounded-full bg-gray-600" />
              <Text variant="base" className="text-white">
                Jane Smith
              </Text>
            </Row>
          </Row>
          <div className="mx-auto mt-14 max-w-screen-2xl px-4 py-10 lg:mt-0 lg:px-16 lg:py-16">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
