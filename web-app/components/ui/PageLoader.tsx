'use client';

import { createPortal } from 'react-dom';

import Loader, { LoaderModel } from './Loader';

export default function PageLoader(props: LoaderModel) {
  return createPortal(
    <div className="visible fixed bottom-0 left-0 right-0 top-0 z-[1001] h-screen w-screen bg-white/10 opacity-100 transition-opacity duration-150 ease-out">
      <div className="flex h-screen items-center justify-center">
        <Loader {...props} />
      </div>
    </div>,
    document.body,
  );
}

export function PageRestrict() {
  return createPortal(
    <div className="visible fixed bottom-0 left-0 right-0 top-0 z-[1001] h-screen w-screen bg-[#E5EAEA82] opacity-70 transition-opacity duration-150 ease-out">
      <div className="flex h-screen items-center justify-center" />
    </div>,
    document.body,
  );
}
