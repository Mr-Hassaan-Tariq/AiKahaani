/** @type {import('tailwindcss').Config} */

module.exports = {
  darkMode: ['class', 'class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './@/components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: 'var(--Poppins-font)',
      },
      colors: {},
      keyframes: {
        'pulse-up': {
          '0%': { opacity: 0.3, transform: 'scale(1)' },
          '100%': { opacity: 0, transform: 'scale(3)' },
        },
      },
      animation: {
        'pulse-up': 'pulse-up 2s ease-out infinite',
      },
    },
  },
  plugins: [require('tailwindcss-animate'), require('@tailwindcss/container-queries')],
};
