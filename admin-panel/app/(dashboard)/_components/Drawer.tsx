'use client';

import * as React from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import Draft from '@assets/svg/draft.svg';
import Magicpan from '@assets/svg/magicpan.svg';
import NotificationIcon from '@assets/svg/notification.svg';
import { X } from 'lucide-react';

import Col from 'components/ui/Col';
import { Drawer, DrawerClose, DrawerContent, DrawerTrigger } from 'components/shadcn_ui/drawer';

type Notification = {
  id: number;
  title: string;
  description: string;
  time: string;
  icon: any;
};

export function MobileDrawer() {
  const router = useRouter();
  const notifications: Notification[] = [
    {
      id: 1,
      title: 'New niche added: “Listicle with a Twi…”',
      description: 'Perfect for countdown videos with a unique hook',
      time: '1 day ago',
      icon: Magicpan,
    },
    {
      id: 2,
      title: '2 unfinished scripts waiting',
      description: 'Pick up where you left off',
      time: '1 day ago',
      icon: Draft,
    },
    {
      id: 3,
      title: 'Trending format: “Conspiracy Shorts”',
      description: 'Optimized for short-form storytelling',
      time: '1 day ago',
      icon: Magicpan,
    },
    {
      id: 4,
      title: 'Script Generator update',
      description: 'Now supports 10 new viral intros!',
      time: '2 days ago',
      icon: Magicpan,
    },
  ];

  return (
    <Drawer>
      <DrawerTrigger asChild>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#2d2d2d] backdrop-blur-sm">
          <Image src={NotificationIcon} alt="NotificationIcon" width={16} height={16} />
        </div>
      </DrawerTrigger>
      <DrawerContent className="border-none bg-[#161616] p-4 text-white">
        {/* Header */}
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Notifications</h2>
          <DrawerClose asChild>
            <X className="h-5 w-5 cursor-pointer" />
          </DrawerClose>
        </div>

        {/* Notifications */}
        {notifications.map((item, index) => (
          <div key={item.id} className="mb-3">
            {/* Time */}
            {(index === 0 || notifications[index - 1].time !== item.time) && (
              <p className="mb-2 text-sm text-[#AAACA6]">{item.time}</p>
            )}

            {/* Item */}
            <div className="flex items-start gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-black">
                <Image src={item.icon} alt={item.title} width={16} height={16} />
              </div>
              <Col className="gap-1">
                <p className="text-sm font-medium">{item.title}</p>
                <p className="text-xs text-[#AAACA6]">{item.description}</p>
              </Col>
            </div>
          </div>
        ))}

        {/* Footer */}
        <DrawerClose asChild>
          <div className="mt-5 text-center" onClick={() => router.push('/notifications')}>
            <button className="text-sm hover:underline">View All Notifications</button>
          </div>
        </DrawerClose>
      </DrawerContent>
    </Drawer>
  );
}
