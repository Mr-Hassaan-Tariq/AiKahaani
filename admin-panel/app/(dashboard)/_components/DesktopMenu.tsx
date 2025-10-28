'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import mainLogo from '@assets/sidebar/mainLogo.png';
import { Crown, LayoutDashboard, Settings, Users } from 'lucide-react';

import LogoutModal from './LogoutModal';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';

export default function DesktopMenu() {
  const pathname = usePathname() || '/';

  const isActive = (path: string) => {
    if (path === '/') return pathname === '/';
    return pathname === path || pathname.startsWith(path + '/');
  };

  const ACTIVE_COLOR = '#20BF0E';
  const INACTIVE_COLOR = '#AAACA6';

  const renderIcon = (icon: React.ReactNode, active: boolean) => {
    if (React.isValidElement(icon)) {
      const el = icon as React.ReactElement<any, any>;
      const existing = (el.props as any)?.className ?? '';
      const className = `h-5 w-5 ${existing}`.trim();

      const color = active ? ACTIVE_COLOR : INACTIVE_COLOR;

      return React.cloneElement(el, {
        className,
        color,
        stroke: color,
        active,
      });
    }
    return icon;
  };

  return (
    <div className="scrollbar sticky top-0 h-screen max-h-screen w-full overflow-hidden overflow-y-auto rounded-r-3xl border-r border-[#BAFF381F] bg-[#161616] px-7 py-8 text-white">
      <Col className="mx-auto h-full min-w-[170px] gap-12">
        <Link href="/">
          <Image src={mainLogo} alt="mainLogo" className="object-cover" />
        </Link>

        <Col className="h-full justify-between">
          <Col className="gap-6">
            {mainMenu.map((e) => {
              const active = isActive(e.path);

              return (
                <Link
                  key={e.name}
                  href={e.path}
                  aria-current={active ? 'page' : undefined}
                  className="group flex w-full cursor-pointer flex-row items-center gap-3 whitespace-nowrap"
                >
                  <div className="flex items-center justify-center">
                    {renderIcon(e.icon, active)}
                  </div>
                  <Text
                    variant="lg"
                    className={`transition-colors ${
                      active ? 'font-semibold text-white' : 'text-[#AAACA6]'
                    } group-hover:text-[#20BF0E]/80`}
                  >
                    {e.name}
                  </Text>
                </Link>
              );
            })}
          </Col>

          <Col className="gap-6">
            {subMenu.map((e) => {
              const active = isActive(e.path);

              return (
                <Link
                  key={e.name}
                  href={e.path}
                  aria-current={active ? 'page' : undefined}
                  className="group flex w-full cursor-pointer flex-row items-center gap-3 whitespace-nowrap"
                >
                  <div className="flex items-center justify-center">
                    {renderIcon(e.icon, active)}
                  </div>
                  <Text
                    variant="lg"
                    className={`transition-colors ${
                      active ? 'font-semibold text-white' : 'text-[#AAACA6]'
                    } group-hover:text-[#20BF0E]/80`}
                  >
                    {e.name}
                  </Text>
                </Link>
              );
            })}

            <LogoutModal />
          </Col>
        </Col>
      </Col>
    </div>
  );
}

export const mainMenu = [
  {
    name: 'Dashboard',
    icon: <LayoutDashboard />,
    path: '/',
  },
  {
    name: 'User Management',
    icon: <Users />,
    path: '/users',
  },
  {
    name: 'Niche Vault',
    icon: <Crown />,
    path: '/niches',
  },
];

export const subMenu = [
  {
    name: 'Settings',
    icon: <Settings />,
    path: '/settings',
  },
];
