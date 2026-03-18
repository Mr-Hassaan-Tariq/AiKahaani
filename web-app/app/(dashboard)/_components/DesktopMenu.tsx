'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FolderOpen, History, LayoutDashboard, Settings, Sparkles, Type } from 'lucide-react';

import LogoutModal from './LogoutModal';
import { cn } from 'lib/utils';

// ── Nav config ───────────────────────────────────────────────────────
export const mainMenu = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { name: 'Script Generator', icon: Sparkles, path: '/new-script' },
  { name: 'My Scripts', icon: History, path: '/my-scripts' },
  { name: 'Niche Vault', icon: FolderOpen, path: '/niche-vault' },
  { name: 'Title Generation', icon: Type, path: '/title-generation' },
];

export const subMenu = [{ name: 'Settings', icon: Settings, path: '/settings', external: false }];

// ── Sidebar ──────────────────────────────────────────────────────────
export default function DesktopMenu() {
  const pathname = usePathname() ?? '/';

  const isActive = (path: string) => {
    if (!path.startsWith('/')) return false;
    if (path === '/') return pathname === '/';
    return pathname === path || pathname.startsWith(`${path}/`);
  };

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-border bg-sidebar px-4 py-5">
      {/* ── Brand ── */}
      <Link href="/" className="mb-7 flex items-center px-2">
        <img
          src="/logos/colored-logo.svg"
          alt="AiKahani"
          width={220}
          height={80}
          className="h-14 w-auto"
        />
      </Link>

      {/* ── Main nav ── */}
      <div className="mb-1">
        <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          Workspace
        </p>
        <nav className="flex flex-col gap-0.5">
          {mainMenu.map((item) => {
            const active = isActive(item.path);
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.path}
                aria-current={active ? 'page' : undefined}
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
            );
          })}
        </nav>
      </div>

      {/* ── Spacer ── */}
      <div className="flex-1" />

      {/* ── Sub nav + logout ── */}
      <nav className="mt-3 flex flex-col gap-0.5">
        {subMenu.map((item) => {
          const active =
            !item.external && (pathname === item.path || pathname.startsWith(`${item.path}/`));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.path}
              target={item.external ? '_blank' : undefined}
              rel={item.external ? 'noopener noreferrer' : undefined}
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
          );
        })}

        <LogoutModal />
      </nav>
    </aside>
  );
}
