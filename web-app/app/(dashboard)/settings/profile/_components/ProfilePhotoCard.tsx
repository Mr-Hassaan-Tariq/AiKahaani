import Image from 'next/image';

import ChangePhotoModal from './ChangePhotoModal';
import DeletePhotoModal from './DeletePhotoModal';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Button } from 'components/shadcn_ui/button';

export default function ProfilePhotoCard() {
  return (
    <Card>
      <Col className="gap-6 lg:gap-8">
        <Text variant="2xl" className="text-xl text-white lg:text-2xl">
          Profile Photo
        </Text>

        <Row className="flex-col justify-normal gap-6 md:flex-row">
          <Image
            src="/images/profile-photo.png"
            alt="DP"
            width={500}
            height={500}
            className="h-[120px] w-[120px] rounded-full bg-white/10 object-cover"
          />

          <Col className="gap-6">
            <Col className="gap-3">
              <Row className="justify-normal">
                <Text variant="base">Recommended size:</Text>{' '}
                <Text variant="base" className="font-semibold">
                  400×400 px
                </Text>
              </Row>
              <Row className="justify-normal">
                <Text variant="base">Accepted formats:</Text>{' '}
                <Text variant="base" className="font-semibold">
                  JPG, PNG · Max file size: 5MB
                </Text>
              </Row>
            </Col>
            <Row className="justify-center lg:justify-normal">
              <ChangePhotoModal
                trigger={
                  <Button className="flex w-fit items-center justify-center rounded-full bg-white/10 p-3 text-sm font-semibold backdrop-blur-[2px] hover:bg-white/10 hover:opacity-70 active:scale-95">
                    {changePhotoIcon} Change photo
                  </Button>
                }
              />

              <DeletePhotoModal
                trigger={
                  <Button className="flex w-fit items-center justify-center rounded-full bg-[#FF50500D] p-3 text-sm font-semibold backdrop-blur-[2px] hover:bg-[#FF50500D] hover:opacity-70 active:scale-95">
                    {basketIcon} Remove photo
                  </Button>
                }
              />
            </Row>
          </Col>
        </Row>
      </Col>
    </Card>
  );
}

const changePhotoIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17" fill="none">
    <g clipPath="url(#clip0_5007_14645)">
      <path
        d="M9.75535 0.666992H4.91135C4.18326 0.666989 3.60626 0.666986 3.14118 0.704984C2.66558 0.743842 2.26317 0.824914 1.89572 1.01214C1.29987 1.31574 0.815432 1.80018 0.511833 2.39602C0.324609 2.76347 0.243537 3.16589 0.204679 3.64148C0.166681 4.10656 0.166683 4.68356 0.166687 5.41165V10.4937L0.166698 10.497L0.166687 10.5003V10.5186C0.166685 11.1244 0.166683 11.6045 0.193221 11.9934C0.220331 12.3908 0.2768 12.7294 0.407735 13.0455C0.729132 13.8214 1.3456 14.4379 2.12152 14.7593C2.43763 14.8902 2.77623 14.9467 3.17357 14.9738C3.5625 15.0003 4.04258 15.0003 4.64832 15.0003H8.16877C8.44491 15.0003 8.66877 14.7765 8.66877 14.5003C8.66877 14.2242 8.44491 14.0003 8.16877 14.0003H4.66669C4.03859 14.0003 3.59256 14.0001 3.24164 13.9761C2.89521 13.9525 2.67816 13.9074 2.50421 13.8354C1.97331 13.6155 1.55152 13.1937 1.33161 12.6628C1.25956 12.4889 1.21454 12.2718 1.1909 11.9254C1.16968 11.6143 1.16705 11.2285 1.16673 10.7074L3.7441 8.13002C4.06953 7.80459 4.59717 7.80459 4.92261 8.13002L8.00293 11.2104C8.19819 11.4056 8.51478 11.4056 8.71004 11.2104C8.9053 11.0151 8.9053 10.6985 8.71004 10.5033L5.62972 7.42292C4.91375 6.70695 3.75295 6.70695 3.03699 7.42292L1.16669 9.29322V5.43366C1.16669 4.67867 1.16708 4.1425 1.20136 3.72291C1.23516 3.30916 1.29942 3.05299 1.40284 2.85001C1.61057 2.44233 1.94202 2.11087 2.34971 1.90314C2.55269 1.79972 2.80886 1.73547 3.22261 1.70166C3.6422 1.66738 4.17837 1.66699 4.93335 1.66699H9.73335C10.4883 1.66699 11.0245 1.66738 11.4441 1.70166C11.8579 1.73547 12.114 1.79972 12.317 1.90314C12.7247 2.11087 13.0561 2.44233 13.2639 2.85001C13.3673 3.05299 13.4315 3.30916 13.4653 3.72291C13.4996 4.1425 13.5 4.67867 13.5 5.43366V9.15473C13.5 9.43087 13.7239 9.65473 14 9.65473C14.2762 9.65473 14.5 9.43087 14.5 9.15473V5.41164C14.5 4.68356 14.5 4.10656 14.462 3.64148C14.4232 3.16589 14.3421 2.76347 14.1549 2.39602C13.8513 1.80018 13.3668 1.31574 12.771 1.01214C12.4035 0.824914 12.0011 0.743842 11.5255 0.704984C11.0605 0.666986 10.4834 0.666989 9.75535 0.666992Z"
        fill="white"
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M9.66669 3.66699C10.6792 3.66699 11.5 4.4878 11.5 5.50033C11.5 6.51285 10.6792 7.33366 9.66669 7.33366C8.65416 7.33366 7.83335 6.51285 7.83335 5.50033C7.83335 4.4878 8.65416 3.66699 9.66669 3.66699ZM10.5 5.50033C10.5 5.04009 10.1269 4.66699 9.66669 4.66699C9.20645 4.66699 8.83335 5.04009 8.83335 5.50033C8.83335 5.96056 9.20645 6.33366 9.66669 6.33366C10.1269 6.33366 10.5 5.96056 10.5 5.50033Z"
        fill="white"
      />
      <path
        d="M15.3334 13.3337C15.6095 13.3337 15.8334 13.1098 15.8334 12.8337V12.167C15.8334 11.3386 15.1618 10.667 14.3334 10.667H11.5404L12.0202 10.1872C12.2155 9.99195 12.2155 9.67537 12.0202 9.48011C11.8249 9.28484 11.5084 9.28484 11.3131 9.48011L9.97976 10.8134C9.83676 10.9564 9.79398 11.1715 9.87137 11.3583C9.94876 11.5452 10.1311 11.667 10.3333 11.667H14.3334C14.6095 11.667 14.8334 11.8908 14.8334 12.167V12.8337C14.8334 13.1098 15.0572 13.3337 15.3334 13.3337Z"
        fill="white"
      />
      <path
        d="M9.50002 12.8337C9.50002 12.5575 9.72388 12.3337 10 12.3337C10.2762 12.3337 10.5 12.5575 10.5 12.8337V13.5003C10.5 13.7765 10.7239 14.0003 11 14.0003H15C15.2023 14.0003 15.3846 14.1221 15.462 14.309C15.5394 14.4958 15.4966 14.7109 15.3536 14.8539L14.0202 16.1872C13.8249 16.3825 13.5083 16.3825 13.3131 16.1872C13.1178 15.9919 13.1178 15.6754 13.3131 15.4801L13.7929 15.0003H11C10.1716 15.0003 9.50002 14.3288 9.50002 13.5003V12.8337Z"
        fill="white"
      />
    </g>
    <defs>
      <clipPath id="clip0_5007_14645">
        <rect width="16" height="16" fill="white" transform="translate(0 0.5)" />
      </clipPath>
    </defs>
  </svg>
);

const basketIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17" fill="none">
    <path
      d="M14 4.48665C11.78 4.26665 9.54667 4.15332 7.32 4.15332C6 4.15332 4.68 4.21999 3.36 4.35332L2 4.48665"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M5.66669 3.81301L5.81335 2.93967C5.92002 2.30634 6.00002 1.83301 7.12669 1.83301H8.87335C10 1.83301 10.0867 2.33301 10.1867 2.94634L10.3334 3.81301"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M12.5667 6.59375L12.1334 13.3071C12.06 14.3537 12 15.1671 10.14 15.1671H5.86002C4.00002 15.1671 3.94002 14.3537 3.86668 13.3071L3.43335 6.59375"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M6.88666 11.5H9.10666"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M6.33331 8.83301H9.66665"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
