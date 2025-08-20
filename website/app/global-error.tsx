'use client';

import { ErrorComponent, IErrorComponentProps } from './error';

export default function GlobalError({ error, reset }: IErrorComponentProps) {
  return <ErrorComponent error={error} reset={reset} />;
}
