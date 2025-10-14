import { ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimeAgo(dateString: string): string {
  const now = new Date();
  const created = new Date(dateString);
  const seconds = Math.floor((now.getTime() - created.getTime()) / 1000);

  const intervals: [number, string][] = [
    [60, 'second'],
    [60, 'minute'],
    [24, 'hour'],
    [7, 'day'],
    [4.345, 'week'],
    [12, 'month'],
    [Number.POSITIVE_INFINITY, 'year'],
  ];

  let interval = seconds;
  let unit = 'second';

  for (let i = 0; i < intervals.length; i++) {
    if (interval < intervals[i][0]) break;
    interval /= intervals[i][0];
    unit = intervals[i][1];
  }

  const value = Math.floor(interval);
  return `${value} ${unit}${value !== 1 ? 's' : ''} ago`;
}
