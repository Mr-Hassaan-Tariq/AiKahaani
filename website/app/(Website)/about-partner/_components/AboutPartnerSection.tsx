import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function AboutPartnerSection({ id }: { id: string }) {
  return (
    <section id={id} className="relative overflow-hidden bg-black pt-40 text-center text-white">
      <Col
        className="relative w-full flex-col-reverse gap-6 overflow-hidden rounded-[32px] border border-brand-green/[32%] bg-brand-black lg:flex-row lg:items-center lg:justify-between"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(43, 255, 19, 0.02), transparent),
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 40px 40px, 40px 40px',
        }}
      >
        <div className="mt-10 flex h-[408px] w-full flex-shrink-0 flex-col items-center justify-center gap-8 rounded-[32px] border border-[rgba(186,255,56,0.12)] bg-[#181916] p-6 shadow-[inset_-22.09px_-6.18px_37.19px_0_rgba(32,34,31,0.25)] backdrop-blur-[11.2px] md:mt-0 lg:w-1/2" />

        <Col className="my-16 w-full gap-8 pl-16 lg:my-0">
          <Col className="max-w-[415px] gap-4 text-left">
            <Text variant="3xl">About [Partner Name]</Text>
            <Text className="text-[13px] text-[#AAACA6]">
              [Partner Name] is a [niche] creator sharing [type of content] to help viewers [main
              goal of audience].
            </Text>
          </Col>
          {localData.map((item, index) => (
            <Row key={index} className="justify-normal gap-3">
              {item.icon}
              <Text variant="sm" className="text-white">
                {item.title}
              </Text>
            </Row>
          ))}
        </Col>
      </Col>
    </section>
  );
}

const menIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path
      d="M24 9.54663C23.92 9.5333 23.8267 9.5333 23.7467 9.54663C21.9067 9.47996 20.44 7.9733 20.44 6.10663C20.44 4.19996 21.9733 2.66663 23.88 2.66663C25.7867 2.66663 27.32 4.2133 27.32 6.10663C27.3067 7.9733 25.84 9.47996 24 9.54663Z"
      stroke="url(#paint0_linear_799_57078)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M22.6267 19.2533C24.4533 19.5599 26.4667 19.2399 27.88 18.2933C29.76 17.0399 29.76 14.9866 27.88 13.7333C26.4533 12.7866 24.4133 12.4666 22.5867 12.7866"
      stroke="url(#paint1_linear_799_57078)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M7.95996 9.54663C8.03996 9.5333 8.13329 9.5333 8.21329 9.54663C10.0533 9.47996 11.52 7.9733 11.52 6.10663C11.52 4.19996 9.98662 2.66663 8.07996 2.66663C6.17329 2.66663 4.63995 4.2133 4.63995 6.10663C4.65329 7.9733 6.11996 9.47996 7.95996 9.54663Z"
      stroke="url(#paint2_linear_799_57078)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M9.33331 19.2533C7.50665 19.5599 5.49332 19.2399 4.07998 18.2933C2.19998 17.0399 2.19998 14.9866 4.07998 13.7333C5.50665 12.7866 7.54665 12.4666 9.37331 12.7866"
      stroke="url(#paint3_linear_799_57078)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M16 19.5067C15.92 19.4934 15.8267 19.4934 15.7467 19.5067C13.9067 19.44 12.44 17.9334 12.44 16.0667C12.44 14.16 13.9733 12.6267 15.88 12.6267C17.7867 12.6267 19.32 14.1734 19.32 16.0667C19.3067 17.9334 17.84 19.4534 16 19.5067Z"
      stroke="url(#paint4_linear_799_57078)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M12.12 23.7067C10.24 24.9601 10.24 27.0134 12.12 28.2667C14.2534 29.6934 17.7467 29.6934 19.88 28.2667C21.76 27.0134 21.76 24.9601 19.88 23.7067C17.76 22.2934 14.2534 22.2934 12.12 23.7067Z"
      stroke="url(#paint5_linear_799_57078)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient
        id="paint0_linear_799_57078"
        x1="20.44"
        y1="6.10663"
        x2="27.32"
        y2="6.10663"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_799_57078"
        x1="22.5867"
        y1="16.0161"
        x2="29.29"
        y2="16.0161"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_799_57078"
        x1="4.63995"
        y1="6.10663"
        x2="11.52"
        y2="6.10663"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint3_linear_799_57078"
        x1="2.66998"
        y1="16.0161"
        x2="9.37331"
        y2="16.0161"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint4_linear_799_57078"
        x1="12.44"
        y1="16.0667"
        x2="19.32"
        y2="16.0667"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint5_linear_799_57078"
        x1="10.71"
        y1="25.9917"
        x2="21.29"
        y2="25.9917"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
    </defs>
  </svg>
);

const youtubeIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path
      d="M13.3333 10.3333C13.3336 10.1557 13.3813 9.9814 13.4713 9.8283C13.5613 9.67519 13.6905 9.54883 13.8456 9.4622C14.0007 9.37558 14.176 9.33181 14.3536 9.33541C14.5311 9.33901 14.7046 9.38984 14.856 9.48267L19.7413 12.4813C19.8869 12.5708 20.0072 12.6961 20.0906 12.8452C20.174 12.9944 20.2178 13.1624 20.2178 13.3333C20.2178 13.5042 20.174 13.6723 20.0906 13.8214C20.0072 13.9706 19.8869 14.0959 19.7413 14.1853L14.856 17.1853C14.7044 17.2783 14.5307 17.3291 14.3529 17.3326C14.1751 17.3361 13.9996 17.2921 13.8444 17.2051C13.6893 17.1182 13.5601 16.9915 13.4703 16.838C13.3805 16.6845 13.3332 16.5098 13.3333 16.332V10.3333Z"
      stroke="url(#paint0_linear_799_57396)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M16 22.6666V28"
      stroke="url(#paint1_linear_799_57396)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M10.6667 28H21.3334"
      stroke="url(#paint2_linear_799_57396)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M26.6667 4H5.33335C3.86059 4 2.66669 5.19391 2.66669 6.66667V20C2.66669 21.4728 3.86059 22.6667 5.33335 22.6667H26.6667C28.1394 22.6667 29.3334 21.4728 29.3334 20V6.66667C29.3334 5.19391 28.1394 4 26.6667 4Z"
      stroke="url(#paint3_linear_799_57396)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient
        id="paint0_linear_799_57396"
        x1="13.3333"
        y1="13.334"
        x2="20.2178"
        y2="13.334"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_799_57396"
        x1="16"
        y1="25.3333"
        x2="17"
        y2="25.3333"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_799_57396"
        x1="10.6667"
        y1="28.5"
        x2="21.3334"
        y2="28.5"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint3_linear_799_57396"
        x1="2.66669"
        y1="13.3333"
        x2="29.3334"
        y2="13.3333"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
    </defs>
  </svg>
);

const awardIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path
      d="M25.3334 12C25.3334 13.9333 24.76 15.7066 23.7734 17.1866C22.3334 19.32 20.0534 20.8266 17.4 21.2133C16.9467 21.2933 16.48 21.3333 16 21.3333C15.52 21.3333 15.0534 21.2933 14.6 21.2133C11.9467 20.8266 9.66669 19.32 8.22669 17.1866C7.24002 15.7066 6.66669 13.9333 6.66669 12C6.66669 6.83996 10.84 2.66663 16 2.66663C21.16 2.66663 25.3334 6.83996 25.3334 12Z"
      stroke="url(#paint0_linear_799_57092)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M28.3333 24.6266L26.1333 25.1466C25.64 25.2666 25.2533 25.64 25.1467 26.1333L24.68 28.0933C24.4267 29.16 23.0667 29.48 22.36 28.64L16 21.3333L9.64 28.6533C8.93334 29.4933 7.57334 29.1733 7.32 28.1066L6.85334 26.1466C6.73334 25.6533 6.34667 25.2666 5.86667 25.16L3.66667 24.64C2.65334 24.4 2.29334 23.1333 3.02667 22.3999L8.22667 17.2C9.66667 19.3333 11.9467 20.84 14.6 21.2266C15.0533 21.3066 15.52 21.3466 16 21.3466C16.48 21.3466 16.9467 21.3066 17.4 21.2266C20.0533 20.84 22.3333 19.3333 23.7733 17.2L28.9733 22.3999C29.7067 23.1199 29.3467 24.3866 28.3333 24.6266Z"
      stroke="url(#paint1_linear_799_57092)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M16.7733 7.97337L17.56 9.5467C17.6667 9.76003 17.9467 9.97337 18.2 10.0134L19.6267 10.2534C20.5333 10.4 20.7467 11.0667 20.0933 11.72L18.9867 12.8267C18.8 13.0134 18.6933 13.3734 18.76 13.64L19.08 15.0134C19.3333 16.0934 18.76 16.52 17.8 15.9467L16.4667 15.16C16.2267 15.0134 15.8267 15.0134 15.5867 15.16L14.2533 15.9467C13.2933 16.5067 12.72 16.0934 12.9733 15.0134L13.2933 13.64C13.3467 13.3867 13.2533 13.0134 13.0667 12.8267L11.96 11.72C11.3067 11.0667 11.52 10.4134 12.4267 10.2534L13.8533 10.0134C14.0933 9.97337 14.3733 9.76003 14.48 9.5467L15.2667 7.97337C15.6533 7.12004 16.3467 7.12004 16.7733 7.97337Z"
      stroke="url(#paint2_linear_799_57092)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient
        id="paint0_linear_799_57092"
        x1="6.66669"
        y1="12"
        x2="25.3334"
        y2="12"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_799_57092"
        x1="2.63922"
        y1="23.1656"
        x2="29.3608"
        y2="23.1656"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_799_57092"
        x1="11.5807"
        y1="11.7677"
        x2="20.4726"
        y2="11.7677"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#2BFF13" />
        <stop offset="1" stopColor="#20BF0E" />
      </linearGradient>
    </defs>
  </svg>
);

const localData = [
  { title: '[X,000+] subscribers on YouTube', icon: menIcon },
  { title: '[X million+] views across all videos', icon: youtubeIcon },
  { title: '[Notable achievement or award]', icon: awardIcon },
];
