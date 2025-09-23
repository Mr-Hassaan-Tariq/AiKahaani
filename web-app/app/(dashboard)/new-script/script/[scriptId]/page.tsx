import { getScript } from './actions';
import ScriptComponent from './ScriptComponent';
import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';

export default async function Page({ params }: { params: Promise<{ scriptId: string }> }) {
  const { scriptId } = await params;
  const { data, isError, error } = await getScript(scriptId);

  return (
    <Col className="gap-8">
      <Col className="w-full items-center">
        <H3 className="text-center">{data?.title || 'Untitled Script'}</H3>
      </Col>
      {isError ? (
        <div className="text-white">{error.message?.toString()}</div>
      ) : (
        <ScriptComponent sections={data.sections} script={data} />
      )}
    </Col>
  );
}
