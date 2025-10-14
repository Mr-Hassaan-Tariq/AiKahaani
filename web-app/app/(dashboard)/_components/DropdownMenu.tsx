'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import BellIcon from '@assets/svg/bell-notification.svg';
import NotificationIcon from '@assets/svg/notification.svg';
import { X } from 'lucide-react';

import { formatTimeAgo } from 'lib/utils';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import Col from 'components/ui/Col';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from 'components/shadcn_ui/dropdown-menu';

type NotificationType = {
  id: number;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  metadata: Record<string, any>;
};

export function Dropdown() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await getClientDataAction<{ results: NotificationType[] }>(
        'v1/notifications/all-notifications/?limit=4&offset=0',
      );
      if (data?.results) {
        setNotifications(data.results);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open]);

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
        {loading ? (
          <p className="text-sm text-gray-400">Loading...</p>
        ) : notifications.length > 0 ? (
          notifications.map((item, index) => (
            <div key={item.id} className="mb-3">
              {/* Time */}
              {(index === 0 ||
                formatTimeAgo(notifications[index - 1].created_at) !==
                  formatTimeAgo(item.created_at)) && (
                <p className="mb-2 text-sm text-[#AAACA6]">{formatTimeAgo(item.created_at)}</p>
              )}

              {/* Item */}
              <div className="flex items-start gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-black">
                  <Image src={BellIcon} alt={item.title} width={16} height={16} />
                </div>
                <Col className="gap-1">
                  <p className="text-sm font-medium">{item.title}</p>
                  <p className="text-xs text-[#AAACA6]">
                    {item.message.slice(0, 50)}
                    {item.message.length > 50 && '...'}
                  </p>
                </Col>
              </div>
            </div>
          ))
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
