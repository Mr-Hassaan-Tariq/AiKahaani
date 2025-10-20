'use client';

import Image from 'next/image';
import RightSvg from '@assets/svg/right.svg';

import { postClientDataAction } from 'lib/utils/clientDataActions';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

interface NotificationItemProps {
  id: number;
  title: string;
  description: string;
  time: string;
  actionText?: string;
  actionLink?: string;
  isNew?: boolean;
  icon?: any;
  onRead?: (id: number) => void;
}

export default function NotificationItem({
  id,
  title,
  description,
  time,
  actionText,
  actionLink,
  isNew = false,
  icon,
  onRead,
}: NotificationItemProps) {
  const handleMarkAsRead = async () => {
    if (!isNew) return;
    try {
      await postClientDataAction(`v1/notifications/${id}/read/`, {});
      onRead?.(id);
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

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

  const finalActionLink = getFinalURL(actionLink);

  return (
    <>
      {/* Desktop */}
      <div className="hidden md:block">
        <Row
          onClick={handleMarkAsRead}
          className="mb-3 cursor-pointer items-start justify-between rounded-xl border border-[var(--Stroke-Surface,#BAFF381F)] bg-[var(--Bg-Surface,#161616)] p-5 text-white hover:bg-[#1C1C1C]"
        >
          <Col className="flex-1 items-start gap-3">
            <Row className="items-center gap-2">
              <Image src={icon} alt="icon" width={20} height={20} />
              <h3 className="font-medium">{title}</h3>
            </Row>
            <p className="text-sm text-[#AAACA6]">{description}</p>
          </Col>

          <Col className="items-end gap-2">
            <Row className="items-center justify-end gap-2">
              {isNew && (
                <>
                  <span className="h-2 w-2 rounded-full bg-[linear-gradient(90deg,#2BFF13_0%,#20BF0E_100%)]"></span>
                  <span className="text-md font-semibold">New</span>
                  <span className="h-0.5 w-0.5 rounded-full bg-white"></span>
                </>
              )}
              <p className="text-sm font-medium text-[#AAACA6]">{time}</p>
            </Row>

            {actionText && actionLink && (
              <a
                href={finalActionLink}
                className="flex w-full items-center justify-end gap-2 text-right text-sm font-semibold hover:underline"
              >
                {actionText} <Image src={RightSvg} height={20} width={20} alt="RightSvg" />
              </a>
            )}
          </Col>
        </Row>
      </div>

      {/* Mobile */}
      <div className="block md:hidden">
        <Col
          onClick={handleMarkAsRead}
          className="mb-3 cursor-pointer items-start justify-between rounded-xl border border-[var(--Stroke-Surface,#BAFF381F)] bg-[var(--Bg-Surface,#161616)] p-3 text-white hover:bg-[#1C1C1C]"
        >
          <Row className="w-full items-center justify-end gap-2">
            {isNew && (
              <>
                <span className="h-2 w-2 rounded-full bg-[linear-gradient(90deg,#2BFF13_0%,#20BF0E_100%)]"></span>
                <span className="text-md font-semibold">New</span>
                <span className="h-0.5 w-0.5 rounded-full bg-white"></span>
              </>
            )}
            <p className="text-sm font-medium text-[#AAACA6]">{time}</p>
          </Row>

          <Col className="w-full items-start gap-2">
            <Row className="items-center gap-2">
              <Image src={icon} alt="icon" width={20} height={20} />
              <h3 className="font-medium">{title}</h3>
            </Row>
            <p className="text-sm text-[#AAACA6]">{description}</p>
          </Col>

          {actionText && actionLink && (
            <div className="flex w-full justify-end">
              <a
                href={finalActionLink}
                className="flex items-center gap-2 text-right text-sm font-semibold hover:underline"
              >
                {actionText} <Image src={RightSvg} height={20} width={20} alt="RightSvg" />
              </a>
            </div>
          )}
        </Col>
      </div>
    </>
  );
}
