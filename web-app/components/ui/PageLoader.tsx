'use client';

import { createPortal } from 'react-dom';
import { PageSpinner } from './Spinner';

export default function PageLoader() {
  return createPortal(<PageSpinner />, document.body);
}

export function PageRestrict() {
  return createPortal(
    <div className="fixed inset-0 z-[1001] bg-background/60 backdrop-blur-sm" />,
    document.body,
  );
}
