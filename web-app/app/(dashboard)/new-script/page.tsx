import GenerateScriptForm from './_components/GenerateScriptForm';
import NewScriptHeader from './_components/NewScriptHeader';
import Col from 'components/ui/Col';

export default function Page() {
  return (
    <Col className="gap-8">
      <NewScriptHeader />
      <GenerateScriptForm />
    </Col>
  );
}
