import DashboardStats from './_components/DashboardStats';
import Card from 'components/ui/Card';

export default function Home() {
  return (
    <div className="space-y-6">
      <Card>
        <DashboardStats />
      </Card>
    </div>
  );
}
