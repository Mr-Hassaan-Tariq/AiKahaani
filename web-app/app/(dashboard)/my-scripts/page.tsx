import { Suspense } from 'react';
import ComponentNav from '@/(dashboard)/_components/ComponentNav';

import { Magicpan } from './_components/components';
import MyScriptsContent from './_components/MyScriptsContent';

interface MyScriptsPageProps {
  searchParams?: {
    query?: string;
    search?: string;
  };
}

export default function MyScriptsPage({ searchParams }: MyScriptsPageProps) {
  return (
    <div className="space-y-6">
      <ComponentNav
        title="My Scripts"
        buttonText="Generate New Script"
        buttonIcon={Magicpan}
        buttonClassName="lg:max-w-[240px]"
        _onButtonClick="/new-script"
      />

      <Suspense fallback={<div>Loading...</div>}>
        <MyScriptsContent searchParams={searchParams} />
      </Suspense>
    </div>
  );
}
