'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';

import DashboardStats from './_components/DashboardStats';
import Card from 'components/ui/Card';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = Cookies.get('access_token');
    if (!token) router.replace('/signin');
  }, [router]);

  return (
    <div className="space-y-6">
      <Card>
        <DashboardStats />
      </Card>
    </div>
  );
}
