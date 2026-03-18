'use client';

import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';

export function ThemeToggle({ className }: { className?: string }) {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const handleToggle = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  // Avoid hydration mismatch: until mounted we don't know current theme.
  if (!mounted) {
    return (
      <button type="button" className={className} aria-label="Toggle dark mode" disabled>
        <Moon className="h-5 w-5 text-muted-foreground" />
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handleToggle}
      className={className}
      aria-label="Toggle dark mode"
    >
      <Sun className="hidden h-5 w-5 dark:block" />
      <Moon className="block h-5 w-5 dark:hidden" />
    </button>
  );
}
