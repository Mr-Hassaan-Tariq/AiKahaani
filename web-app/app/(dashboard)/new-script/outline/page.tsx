import OutlineComponent from './OutlineComponent';
import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';
import Text from 'components/ui/Text';

export default function Page() {
  return (
    <Col className="gap-8">
      <Col className="w-full items-center">
        <H3>Here’s your script outline</H3>
        <Text variant="lg" className="text-brand-secondary">
          Review and tweak the structure before generating the full script.
        </Text>
      </Col>
      <OutlineComponent />
    </Col>
  );
}
