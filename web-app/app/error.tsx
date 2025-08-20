'use client';

import { FC } from 'react';
import Link from 'next/link';

export interface IErrorComponentProps {
  error: Error;
  reset: () => void;
}

export default function Error({ error, reset }: IErrorComponentProps) {
  return <ErrorComponent error={error} reset={reset} />;
}

export const ErrorComponent: FC<IErrorComponentProps> = ({ error, reset }) => (
  <div className="flex w-full flex-col gap-10 px-4 py-10 md:flex-row lg:gap-20 lg:px-20 lg:pt-16 2xl:gap-36 2xl:px-[123px]">
    <div className="w-full">
      <div className="mt-20 flex items-center justify-center">
        <div>
          <h1 className="text-primary-eerie_black text-2xl font-medium">Something went wrong!</h1>
          <div className="mt-2 font-medium">
            Please try again in a few minutes. If the problem persists ,{' '}
            <Link
              href="https://www.gogeviti.com/contact-us"
              target="_blank"
              className="text-primary-eerie_black underline"
            >
              contact us
            </Link>
          </div>
          <button onClick={() => reset()} className="mt-5 rounded-full" />
          <div className="mt-14 pl-3 text-sm font-medium md:text-base">Cause</div>
          <div className="rounded-lg border bg-slate-100 p-3 font-poppins text-sm text-gray-500 md:text-base">
            {error.toString()}
          </div>
        </div>
      </div>
    </div>
  </div>
);
