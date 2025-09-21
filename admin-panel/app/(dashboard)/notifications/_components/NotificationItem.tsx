import Image from 'next/image';
import RightSvg from '@assets/svg/right.svg';

import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

interface NotificationItemProps {
  title: string;
  description: string;
  time: string;
  actionText?: string;
  actionLink?: string;
  isNew?: boolean;
  icon?: any;
}

export default function NotificationItem({
  title,
  description,
  time,
  actionText,
  actionLink,
  isNew = false,
  icon,
}: NotificationItemProps) {
  return (
    <>
      <div className="hidden md:block">
        <Row className="mb-3 items-start justify-between rounded-xl border border-[var(--Stroke-Surface,#BAFF381F)] bg-[var(--Bg-Surface,#161616)] p-5 text-white">
          <Col className="items-start gap-3">
            <Row className="items-center gap-2">
              <Image src={icon} alt="icon" width={20} height={20} />
              <h3 className="font-medium">{title}</h3>
            </Row>
            <p className="text-sm text-[#AAACA6]">{description}</p>
          </Col>
          <Col className="justify-end">
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
                href={actionLink}
                className="flex items-center gap-2 text-sm font-semibold hover:underline"
              >
                {actionText} <Image src={RightSvg} height={20} width={20} alt="RightSvg" />
              </a>
            )}
          </Col>
        </Row>
      </div>
      <div className="block md:hidden">
        <Col className="mb-3 items-start justify-between rounded-xl border border-[var(--Stroke-Surface,#BAFF381F)] bg-[var(--Bg-Surface,#161616)] p-3 text-white">
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
          <Col className="items-start gap-2">
            <Row className="items-center gap-2">
              <Image src={icon} alt="icon" width={20} height={20} />
              <h3 className="font-medium">{title}</h3>
            </Row>
            <p className="text-sm text-[#AAACA6]">{description}</p>
          </Col>
          {actionText && actionLink && (
            <a
              href={actionLink}
              className="text-md flex items-center gap-2 font-semibold hover:underline"
            >
              {actionText} <Image src={RightSvg} height={20} width={20} alt="RightSvg" />
            </a>
          )}
        </Col>
      </div>
    </>
  );
}
