'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import BellIcon from '@assets/svg/bell-notification.svg';
import NotificationIcon from '@assets/svg/notification.svg';
import { X } from 'lucide-react';

import MagicPan from '../../../public/images/magicpen.svg';
import { formatTimeAgo } from 'lib/utils';
import Col from 'components/ui/Col';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from 'components/shadcn_ui/dropdown-menu';

export function Dropdown({ notifications }: { notifications: any[] }) {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  const getFinalURL = (link?: string) => {
    if (!link) return '#';

    if (link.startsWith('/scripts/')) {
      const id = link.replace('scripts/', '');
      return `/new-script/script/${id}`;
    }

    if (link.startsWith('/outlines/')) {
      const id = link.replace('/outlines/', '');
      return `/new-script/${id}`;
    }

    return link;
  };

  // Handle redirect based on metadata
  const handleNotificationClick = (metadata: Record<string, any>) => {
    const metaValue = metadata?.script || metadata?.outline;
    if (metaValue?.link) {
      const finalURL = getFinalURL(metaValue?.link);
      router.push(finalURL);
      setOpen(false);
    }
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <div className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-full bg-[#2d2d2d] backdrop-blur-sm">
          <Image src={NotificationIcon} alt="NotificationIcon" width={16} height={16} />
        </div>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        className="w-[340px] rounded-xl border-none bg-[#343434] p-4 text-white"
        align="end"
      >
        {/* Header */}
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Notifications</h2>
          <X className="h-5 w-5 cursor-pointer" onClick={() => setOpen(false)} />
        </div>

        {/* Notifications */}
        {notifications?.length > 0 ? (
          notifications[0]?.results?.map((item: any, index: number) => {
            const hasMetadata = Object.keys(item?.metadata || {}).length > 0;
            const icon = hasMetadata ? MagicPan : BellIcon;

            return (
              <div
                key={item?.id}
                className="mb-3 cursor-pointer rounded-lg p-2 transition-all hover:bg-[#3d3d3d]"
                onClick={() => handleNotificationClick(item?.metadata)}
              >
                {/* Time Grouping */}
                {(index === 0 ||
                  formatTimeAgo(notifications[index - 1]?.created_at) !==
                    formatTimeAgo(item?.created_at)) && (
                  <p className="mb-2 text-sm text-[#AAACA6]">{formatTimeAgo(item?.created_at)}</p>
                )}

                {/* Item */}
                <div className="flex items-start gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-black">
                    <Image src={icon} alt={item?.title} width={16} height={16} />
                  </div>
                  <Col className="gap-1">
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="text-xs text-[#AAACA6]">
                      {item?.message?.slice(0, 50)}
                      {item?.message?.length > 50 && '...'}
                    </p>
                  </Col>
                </div>
              </div>
            );
          })
        ) : (
          <p className="text-sm text-gray-400">No notifications yet</p>
        )}

        {/* Footer */}
        <div className="mt-5 text-center">
          <button
            className="text-sm hover:underline"
            onClick={() => {
              router.push('/notifications');
              setOpen(false);
            }}
          >
            View All Notifications
          </button>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
