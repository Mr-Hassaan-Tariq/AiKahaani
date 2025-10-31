'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import mainLogo from '@assets/sidebar/mainLogo.png';

import LogoutModal from './LogoutModal';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';
import CrownIcon from 'components/icons/CrownIcon';
import MyScriptsIcon from 'components/icons/MyScriptsIcon';
import ScriptGeneratorIcon from 'components/icons/ScriptGeneratorIcon';
import SettingsIcon from 'components/icons/SettingsIcon';
import SubTitleIcon from 'components/icons/SubTitleIcon';

export default function DesktopMenu() {
  const pathname = usePathname() || '/';

  const isActive = (path: string) => {
    if (path === '/') {
      return (
        pathname === '/' ||
        pathname === '/new-script' ||
        pathname.startsWith('/new-script/') ||
        pathname.includes('/new-script') ||
        pathname.includes('new-script')
      );
    }
    return pathname === path || pathname.startsWith(path + '/');
  };

  const renderIcon = (icon: React.ReactNode, active: boolean) => {
    if (React.isValidElement(icon)) {
      const el = icon as React.ReactElement<any, any>;
      const existing = (el.props as any)?.className ?? '';
      const className = `h-5 w-5 ${existing}`.trim();
      return React.cloneElement(el, { className, active });
    }
    return icon;
  };

  return (
    <div className="scrollbar sticky top-0 h-screen max-h-screen w-full overflow-hidden overflow-y-auto rounded-r-3xl border-r border-[#BAFF381F] bg-[#161616] px-7 py-8 text-white">
      <Col className="mx-auto h-full min-w-[170px] gap-12">
        {/* Logo */}
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

          {/* Sub Menu */}
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
    name: 'Script Generator',
    icon: <ScriptGeneratorIcon />,
    path: '/',
  },
  {
    name: 'My Scripts',
    icon: <MyScriptsIcon />,
    path: '/my-scripts',
  },
  {
    name: 'Niche Vault',
    icon: <CrownIcon />,
    path: '/niche-vault',
  },
  {
    name: 'Title Generation',
    icon: <SubTitleIcon />,
    path: '/title-generation',
  },
];

export const subMenu = [
  // {
  //   name: 'Affiliate Program',
  //   icon: <UsersIcon />,
  //   path: '/script-generator',
  // },
  {
    name: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings',
  },
];
