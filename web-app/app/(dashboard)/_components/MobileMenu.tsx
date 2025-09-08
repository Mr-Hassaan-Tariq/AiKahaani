'use client';

import Link from 'next/link';
import { MenuIcon } from 'lucide-react';

import { mainMenu, subMenu } from './DesktopMenu';
import LogoutModal from './LogoutModal';
import Col from 'components/ui/Col';
import PlanUpgradeModal from 'components/ui/PlanUpgradeModal';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Sheet, SheetClose, SheetContent, SheetTrigger } from 'components/shadcn_ui/sheet';

export default function MobileMenu() {
  return (
    <Sheet>
      <SheetTrigger>
        <MenuIcon size={24} />
      </SheetTrigger>
      <SheetContent
        side="right"
        className="w-80 border-l border-[#BAFF381F] bg-[#161616] text-white"
      >
        <Text variant="base" className="flex items-center gap-4 text-white">
          Plan: <PlanUpgradeModal />
        </Text>
        <Col className="h-full w-full items-start justify-between pt-8">
          <Col className="w-full gap-6">
            {mainMenu.map((e) => (
              <Link href={e.path} key={e.name}>
                <SheetClose>
                  <Row className="group w-full cursor-pointer justify-start gap-4 whitespace-nowrap [font-feature-settings:'liga'_off,'clig'_off]">
                    {e.icon}
                    <p className="text-[#AAACA6] group-hover:text-[#20BF0E]/80">{e.name}</p>
                  </Row>
                </SheetClose>
              </Link>
            ))}
          </Col>
          <Col className="w-full gap-6">
            {subMenu.map((e) => (
              <Link href={e.path} key={e.name}>
                <SheetClose className="px-0 py-0">
                  <Row className="group w-full cursor-pointer justify-start gap-4 whitespace-nowrap [font-feature-settings:'liga'_off,'clig'_off]">
                    {e.icon}
                    <Text variant="lg" className="text-[#AAACA6] group-hover:text-[#20BF0E]/80">
                      {e.name}
                    </Text>
                  </Row>
                </SheetClose>
              </Link>
            ))}

            <LogoutModal />
          </Col>
        </Col>
      </SheetContent>
    </Sheet>
  );
}
