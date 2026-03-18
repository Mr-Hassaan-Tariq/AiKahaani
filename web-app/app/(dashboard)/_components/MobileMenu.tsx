'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MenuIcon } from 'lucide-react';

import { mainMenu, subMenu } from './DesktopMenu';
import LogoutModal from './LogoutModal';
import { cn } from 'lib/utils';
import { Sheet, SheetClose, SheetContent, SheetTrigger } from 'components/shadcn_ui/sheet';

export default function MobileMenu() {
  const pathname = usePathname() ?? '/';

  const isActive = (path: string) => {
    if (!path.startsWith('/')) return false;
    if (path === '/') return pathname === '/';
    return pathname === path || pathname.startsWith(`${path}/`);
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <button
          aria-label="Open navigation"
          className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-muted-foreground hover:bg-muted"
        >
          <MenuIcon className="h-4 w-4" />
        </button>
      </SheetTrigger>

      <SheetContent
        side="left"
        className="w-72 border-r border-border bg-sidebar p-0 text-sidebar-foreground"
      >
        <div className="flex h-full flex-col px-4 py-5">
          {/* Brand */}
          <div className="mb-7 px-2">
            <img
              src="/logos/colored-logo.svg"
              alt="AiKahani"
              width={220}
              height={80}
              className="h-14 w-auto dark:hidden"
            />
            <img
              src="/logos/logo-dark.svg"
              alt="AiKahani"
              width={220}
              height={80}
              className="hidden h-14 w-auto dark:block"
            />
          </div>

          {/* Main nav */}
          <nav className="flex flex-col gap-0.5">
            {mainMenu.map((item) => {
              const active = isActive(item.path);
              const Icon = item.icon;
              return (
                <SheetClose key={item.name} asChild>
                  <Link
                    href={item.path}
                    className={cn(
                      'flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium transition-colors',
                      active
                        ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    )}
                  >
                    <Icon className="h-[18px] w-[18px] shrink-0" />
                    {item.name}
                  </Link>
                </SheetClose>
              );
            })}
          </nav>

          <div className="flex-1" />

          {/* Sub nav */}
          <nav className="flex flex-col gap-0.5">
            {subMenu.map((item) => {
              const Icon = item.icon;
              return (
                <SheetClose key={item.name} asChild>
                  <Link
                    href={item.path}
                    target={item.external ? '_blank' : undefined}
                    rel={item.external ? 'noopener noreferrer' : undefined}
                    className="flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  >
                    <Icon className="h-[18px] w-[18px] shrink-0" />
                    {item.name}
                  </Link>
                </SheetClose>
              );
            })}
            <LogoutModal />
          </nav>
        </div>
      </SheetContent>
    </Sheet>
  );
}
