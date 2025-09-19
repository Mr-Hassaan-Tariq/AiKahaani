import { getOutline } from './actions';
import OutlineComponent from './OutlineComponent';
import { logger } from 'lib/logger';
import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';
import Text from 'components/ui/Text';

export default async function Page({ params }: { params: Promise<{ outlineId: string }> }) {
  const { outlineId } = await params;

  const { data, error, isError } = await getOutline(outlineId);

  if (isError) {
    return <div className="text-white"> Error: {error?.message}</div>;
  }
  logger.info(data);

  return (
    <Col className="gap-8">
      <Col className="w-full items-center">
        <H3>Here’s your script outline</H3>
        <Text variant="lg" className="text-brand-secondary">
          Review and tweak the structure before generating the full script.
        </Text>
      </Col>
      <OutlineComponent outline={data} />
    </Col>
  );
}
