import GenerateScriptForm from './_components/GenerateScriptForm';
import NewScriptHeader from './_components/NewScriptHeader';
import { getConfig } from './actions';
import Col from 'components/ui/Col';

export default async function Page() {
  const { data, error, isError } = await getConfig();

  if (isError) {
    return <div className="text-white">Error: {error?.message}</div>;
  }

  return (
    <Col className="gap-8">
      <NewScriptHeader />
      <GenerateScriptForm configData={data} />
    </Col>
  );
}
