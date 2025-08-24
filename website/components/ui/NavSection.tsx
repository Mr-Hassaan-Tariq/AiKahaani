'use client';

import { useMemo, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import navLogo from 'assets/nav-logo.png';
import { ArrowRight, Menu, X } from 'lucide-react';

import { WEB_APP_URL } from '../../lib/constants';
import Row from './Row';
import { navItems } from 'lib/localData';
import { cn } from 'lib/utils';
import { Button } from 'components/shadcn_ui/button';

export default function NavSection() {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <nav className="relative flex items-center justify-between text-white">
      {/* Logo */}
      <Link href="/">
        <Image src={navLogo} alt="logo" width={200} height={100} placeholder="blur" />
      </Link>

      {/* Desktop Menu */}
      <ItemList isDesk />

      {/* Desktop Buttons */}
      <div className="hidden gap-4 md:flex">
        {loginButton}
        <Link href={`${WEB_APP_URL}/signup`} target="_blank">
          <Button className="flex h-[52px] items-center gap-2.5 rounded-full border border-[#2BFF13] bg-[#2BFF13] px-0 pl-4 font-bold text-black transition-all duration-300 hover:scale-95 hover:bg-[#2BFF13] hover:opacity-80">
            Get Started
            <Row className="h-12 w-12 justify-center gap-0 rounded-full bg-white">
              <ArrowRight size={20} />
            </Row>
          </Button>
        </Link>
      </div>

      {/* Mobile Hamburger Button */}
      <Button
        className="text-white md:hidden"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Toggle menu"
      >
        {isOpen ? <X size={28} /> : <Menu size={28} />}
      </Button>

      {/* Mobile Dropdown Menu */}
      {isOpen && (
        <div className="animate-slideDown absolute right-[-40px] top-16 z-50 h-screen w-screen overflow-hidden border-t border-gray-800 bg-black/95 backdrop-blur-md md:hidden">
          <ItemList />
          <div className="flex flex-row gap-4 px-6">
            <Link href={`${WEB_APP_URL}/signup`} target="_blank">
              <Button className="flex h-[52px] w-[150px] items-center gap-2.5 rounded-full border bg-[#FFFFFF1A] px-4 font-bold transition-all duration-300 hover:scale-95 hover:bg-[#2BFF13] hover:opacity-80">
                Login
              </Button>
            </Link>
            <Link href={`${WEB_APP_URL}/signup`} target="_blank">
              <Button className="flex h-[52px] items-center gap-2.5 rounded-full border border-[#2BFF13] bg-[#2BFF13] px-0 pl-4 font-bold text-black transition-all duration-300 hover:scale-95 hover:bg-[#2BFF13] hover:opacity-80">
                Get Started
                <Row className="h-12 w-12 justify-center gap-0 rounded-full bg-white">
                  <ArrowRight size={20} />
                </Row>
              </Button>
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}

function ItemList({ isDesk }: { isDesk?: boolean }) {
  const router = useRouter();
  const pathname = usePathname();

  const itemList = useMemo(() => {
    if (['/', '/affiliates', '/about-partner'].includes(pathname)) {
      return navItems.filter((e) => e.ref?.includes(pathname));
    }
    return [];
  }, [pathname]);

  return (
    <ul
      className={cn(
        isDesk ? 'hidden gap-8 md:flex' : 'flex flex-col gap-6 p-6 text-center text-lg'
      )}
    >
      {itemList.map((e) => (
        <li
          key={e.id}
          onClick={(ex) => {
            ex.preventDefault();
            if (e.link) {
              return router.push(e.link);
            }
            const element = document.getElementById(e.id);
            if (element) {
              element.scrollIntoView({ behavior: 'smooth' });
            }
          }}
          className="cursor-pointer transition duration-300 hover:text-green-500"
        >
          {e.label}
        </li>
      ))}
    </ul>
  );
}

const loginButton = (
  <Link href={`${WEB_APP_URL}/signup`} target="_blank">
    <Button className="h-10 rounded-lg bg-[#262724] px-6 font-bold md:h-[52px] md:rounded-full">
      Login
    </Button>
  </Link>
);
