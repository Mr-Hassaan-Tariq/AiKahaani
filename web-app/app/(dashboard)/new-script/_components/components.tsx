import Button from 'components/ui/Button';
import Col from 'components/ui/Col';
import Loader from 'components/ui/Loader';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export function LoadingScreen() {
  return (
    <Col className="relative h-[calc(100dvh-350px)] w-full animate-pulse items-center justify-center">
      <div className="absolute">
        <Row>
          {editIcon}
          <Text variant="lg" className="font-figtree font-bold tracking-normal text-white">
            Analyzing your topic and outlining key points...
          </Text>
        </Row>
      </div>
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          // eslint-disable-next-line react/no-array-index-key
          key={index}
          className="h-20 w-full bg-[linear-gradient(90deg,#161616_0%,#292929_67.79%,#333_83.65%,_#161616_100%)]"
        />
      ))}
      <Button disabled className="py-5">
        <Row>
          <Loader size="xs" color="black" />
          Generating your script outline...
        </Row>
      </Button>
    </Col>
  );
}

export const editIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path
      d="M3.50043 20.4999C4.33043 21.3299 5.67043 21.3299 6.50043 20.4999L19.5004 7.49994C20.3304 6.66994 20.3304 5.32994 19.5004 4.49994C18.6704 3.66994 17.3304 3.66994 16.5004 4.49994L3.50043 17.4999C2.67043 18.3299 2.67043 19.6699 3.50043 20.4999Z"
      stroke="white"
      stroke-width="1.2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M18.0098 8.98999L15.0098 5.98999"
      stroke="white"
      stroke-width="1.2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M8.5 2.44L10 2L9.56 3.5L10 5L8.5 4.56L7 5L7.44 3.5L7 2L8.5 2.44Z"
      stroke="white"
      stroke-width="1.2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M4.5 8.44L6 8L5.56 9.5L6 11L4.5 10.56L3 11L3.44 9.5L3 8L4.5 8.44Z"
      stroke="white"
      stroke-width="1.2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M19.5 13.44L21 13L20.56 14.5L21 16L19.5 15.56L18 16L18.44 14.5L18 13L19.5 13.44Z"
      stroke="white"
      stroke-width="1.2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
);
