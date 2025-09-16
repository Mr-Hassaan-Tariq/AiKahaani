import ScriptComponent from './ScriptComponent';
import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';

export default function Page() {
  return (
    <Col className="gap-8">
      <Col className="w-full items-center">
        <H3 className="text-center">
          Full Script: <br /> Top 5 Productivity Hacks That Actually Work
        </H3>
      </Col>
      <ScriptComponent />
    </Col>
  );
}
