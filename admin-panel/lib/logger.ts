export const logger = {
  log: (...args: unknown[]) => {
    if (process.env.NODE_ENV !== 'production') {
      // eslint-disable-next-line no-console
      console.log('[LOG]:', ...args);
    }
  },
  error: (...args: unknown[]) => {
    console.error('[ERROR]:', ...args);
  },
  warn: (...args: unknown[]) => {
    console.warn('[WARN]:', ...args);
  },
  info: (...args: unknown[]) => {
    // eslint-disable-next-line no-console
    console.info('[INFO]:', ...args);
  },
};
