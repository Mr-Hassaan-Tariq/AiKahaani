'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// import dayjs from 'dayjs';
// import advanced from 'dayjs/plugin/advancedFormat';
// import timezone from 'dayjs/plugin/timezone';
// import utc from 'dayjs/plugin/utc';

// dayjs.extend(utc);
// dayjs.extend(timezone);
// dayjs.extend(advanced);

export default function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 4 * 1000,
      },
    },
  });

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
