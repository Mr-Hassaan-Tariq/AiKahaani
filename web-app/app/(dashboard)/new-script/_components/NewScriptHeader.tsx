import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';
import Text from 'components/ui/Text';

export default function NewScriptHeader() {
  return (
    <Col className="w-full items-center">
      <H3>Create Your Script</H3>
      <Text variant="lg" className="text-brand-secondary">
        Fill out the details below to generate your YouTube script
      </Text>
    </Col>
  );
}
