import Image from 'next/image';
import Link from 'next/link';

import DesktopMenu from './_components/DesktopMenu';
import { MobileDrawer } from './_components/Drawer';
import { Dropdown } from './_components/DropdownMenu';
import MobileMenu from './_components/MobileMenu';
import { getNotifications, getUserProfile } from './actions';
import ClientImage from 'components/ui/ClientImage';
import NavPageTitle from 'components/layout/NavPageTitle';
import { ThemeToggle } from 'components/ThemeToggle';

function getInitials(name?: string, username?: string) {
  const base = name || username || '';
  if (!base) return 'U';
  const parts = base.trim().split(' ');
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data: user } = await getUserProfile();
  const { data: notify } = await getNotifications();
  const notificationItems = notify?.data ?? [];
  const initials = getInitials(user?.fullname, user?.username);

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-background">
      {/* ── Desktop sidebar ── */}
      <div className="hidden lg:flex">
        <DesktopMenu />
      </div>

      {/* ── Main column ── */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* ── Mobile top bar ── */}
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-background px-4 lg:hidden">
          {/* Left: hamburger + logo */}
          <div className="flex items-center gap-3">
            <MobileMenu />
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary">
                <Image
                  src="/logos/icon.svg"
                  alt="AiKahani"
                  width={18}
                  height={18}
                  unoptimized
                  style={{ filter: 'brightness(0) invert(1)' }} // red -> white
                  className="h-3.5 w-3.5"
                />
              </div>
              <span className="text-sm font-semibold text-foreground">AiKahani</span>
            </Link>
          </div>

          {/* Right: notifications + avatar */}
          <div className="flex items-center gap-2">
            <ThemeToggle className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground" />
            <MobileDrawer />
            {user?.profile_picture_url ? (
              <ClientImage
                src={user.profile_picture_url}
                alt="Profile"
                width={32}
                height={32}
                className="h-8 w-8 rounded-full object-cover ring-2 ring-border"
              />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground ring-2 ring-border">
                {initials}
              </div>
            )}
          </div>
        </header>

        {/* ── Desktop topbar ── */}
        <header className="hidden h-14 shrink-0 items-center justify-between border-b border-border bg-background px-6 lg:flex">
          <NavPageTitle />
          <div className="flex items-center gap-3">
            <ThemeToggle className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground" />
            <Dropdown notifications={notificationItems} />
            {user?.profile_picture_url ? (
              <ClientImage
                src={user.profile_picture_url}
                alt="Profile"
                width={32}
                height={32}
                className="h-8 w-8 rounded-full object-cover ring-2 ring-border"
              />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground">
                {initials}
              </div>
            )}
            <span className="text-sm font-medium text-foreground">
              {user?.fullname || user?.username || ''}
            </span>
          </div>
        </header>

        {/* ── Page content ── */}
        <main className="scrollbar-hide flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
