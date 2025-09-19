import Image from 'next/image';

import CopyIcon from '/public/images/copy.svg';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function TitleList({
  titles,
  onCopy,
}: {
  titles: string[];
  onCopy: (title: string) => void;
}) {
  return (
    <Col
      className="flex max-h-[350px] w-full flex-col gap-3 overflow-y-auto pr-2"
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
    >
      {titles.map((title, index) => (
        <Row
          key={index}
          className="w-full items-center justify-between rounded-[16px] bg-[#FFFFFF1A] px-[12px] py-[16px]"
        >
          <Text className="text-md font-semibold text-white">
            {index + 1}. {title}
          </Text>
          <Image
            className="cursor-pointer"
            src={CopyIcon}
            alt="copy"
            width={24}
            height={24}
            onClick={() => onCopy(title)}
          />
        </Row>
      ))}
    </Col>
  );
}
