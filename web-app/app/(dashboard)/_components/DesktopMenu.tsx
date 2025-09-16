'use client';

import Image from 'next/image';
import Link from 'next/link';
import mainLogo from '@assets/sidebar/mainLogo.png';

import LogoutModal from './LogoutModal';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';
import CrownIcon from 'components/icons/CrownIcon';
import MyScriptsIcon from 'components/icons/MyScriptsIcon';
import ScriptGeneratorIcon from 'components/icons/ScriptGeneratorIcon';
import SettingsIcon from 'components/icons/SettingsIcon';
import SubTitleIcon from 'components/icons/SubTitleIcon';
import UsersIcon from 'components/icons/UsersIcon';

export default function DesktopMenu() {
  return (
    <div className="scrollbar sticky top-0 h-screen max-h-screen w-full overflow-hidden overflow-y-auto rounded-r-3xl border-r border-[#BAFF381F] bg-[#161616] px-7 py-8 text-white">
      <Col className="mx-auto h-full min-w-[170px] gap-12">
        <Link href="/">
          <Image src={mainLogo} alt="mainLogo" className="object-cover" />
        </Link>

        <Col className="h-full justify-between">
          <Col className="gap-6">
            {mainMenu.map((e) => (
              <Link
                key={e.name}
                href={e.path}
                className="group flex w-full cursor-pointer flex-row items-center justify-normal gap-2.5 whitespace-nowrap [font-feature-settings:'liga'_off,'clig'_off]"
              >
                {e.icon}
                <Text variant="lg" className="text-white group-hover:text-[#20BF0E]/40">
                  {e.name}
                </Text>
              </Link>
            ))}
          </Col>
          <Col className="gap-6">
            {subMenu.map((e) => (
              <Link
                key={e.name}
                href={e.path}
                className="group flex w-full cursor-pointer flex-row items-center justify-normal gap-2.5 whitespace-nowrap [font-feature-settings:'liga'_off,'clig'_off]"
              >
                {e.icon}
                <Text variant="lg" className="text-[#AAACA6] group-hover:text-[#20BF0E]/40">
                  {e.name}
                </Text>
              </Link>
            ))}

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
    path: '/new-script',
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
  {
    name: 'Affiliate Program',
    icon: <UsersIcon />,
    path: '/script-generator',
  },
  {
    name: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings',
  },
];
