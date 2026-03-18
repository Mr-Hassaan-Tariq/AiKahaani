import { ReactNode } from 'react';

// No Card wrapper — each page provides its own layout via Topbar
export default function Layout({ children }: { children: ReactNode }) {
  return <div>{children}</div>;
}
