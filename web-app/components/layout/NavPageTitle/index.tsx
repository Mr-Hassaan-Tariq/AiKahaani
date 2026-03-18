'use client';

import { usePathname } from 'next/navigation';

function getTitle(pathname: string): string {
  if (pathname === '/') return 'Dashboard';
  if (pathname === '/new-script') return 'Script Generator';
  if (pathname.startsWith('/new-script/script/')) return 'Full Script';
  if (pathname.startsWith('/new-script/')) return 'Script Outline';
  if (pathname.startsWith('/my-scripts')) return 'My Scripts';
  if (pathname.startsWith('/niche-vault')) return 'Niche Vault';
  if (pathname.startsWith('/title-generation')) return 'Title Generation';
  if (pathname.startsWith('/notifications')) return 'Notifications';
  if (pathname.startsWith('/settings/profile')) return 'Profile Settings';
  if (pathname.startsWith('/settings/notifications')) return 'Notification Settings';
  if (pathname.startsWith('/settings/privacy-security')) return 'Privacy & Security';
  if (pathname.startsWith('/settings/subscription-plan')) return 'Subscription Plan';
  if (pathname.startsWith('/settings')) return 'Settings';
  return 'Dashboard';
}

export default function NavPageTitle() {
  const pathname = usePathname() ?? '/';
  return <h1 className="text-base font-semibold text-foreground">{getTitle(pathname)}</h1>;
}
