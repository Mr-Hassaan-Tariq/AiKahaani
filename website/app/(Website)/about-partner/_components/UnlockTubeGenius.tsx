import { ArrowRight } from 'lucide-react';

import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function UnlockTubeGenius() {
  return (
    <section className="relative overflow-hidden bg-black pt-20 text-center text-white lg:pt-40">
      <Row
        className="relative h-[300px] w-full items-center justify-center rounded-[32px] border border-brand-green/[32%] bg-brand-black lg:h-[408px]"
        style={{
          backgroundImage: `
        linear-gradient(to right, rgba(43, 255, 19, 0.02), transparent),
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
      `,
          backgroundSize: '100% 100%, 40px 40px, 40px 40px',
        }}
      >
        <Col className="w-fit items-center justify-center gap-8">
          <Col className="max-w-[615px] gap-4 text-left">
            <Text className="text-center text-3xl lg:text-5xl">
              Unlock the TubeGenius Advantage for $1
            </Text>
            <Text variant="xl" className="text-center text-[#AAACA6]">
              Limited-time offer for my community. Start creating smarter today.
            </Text>
          </Col>
          <button
            className="flex w-fit items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
            style={{ fontWeight: '600' }}
          >
            Start for $1
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
              <ArrowRight size={20} />
            </span>
          </button>
        </Col>
      </Row>
    </section>
  );
}
