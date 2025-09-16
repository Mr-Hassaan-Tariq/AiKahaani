import { ReactNode } from 'react';

import Card from 'components/ui/Card';

export default function Layout({ children }: { children: ReactNode }) {
  return <Card>{children}</Card>;
}
