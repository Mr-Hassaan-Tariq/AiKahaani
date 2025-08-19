import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    ignores: [
      // Dependencies
      'node_modules/',
      '.pnp',
      '.pnp.js',

      // Production builds
      '.next/',
      'out/',
      'build/',
      'dist/',

      // Environment files
      '.env*',

      // Logs
      'npm-debug.log*',
      'yarn-debug.log*',
      'yarn-error.log*',
      'pnpm-debug.log*',

      // Runtime data
      'pids',
      '*.pid',
      '*.seed',
      '*.pid.lock',

      // Coverage directory
      'coverage/',
      '*.lcov',
      '.nyc_output',

      // Cache directories
      '.eslintcache',
      '.cache',
      '.parcel-cache',

      // Generated files
      'next-env.d.ts',
      '*.tsbuildinfo',

      // Lock files
      'package-lock.json',
      'yarn.lock',
      'pnpm-lock.yaml',
    ],
    rules: {
      // TypeScript specific rules
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-var-requires': 'error',

      // React specific rules
      'react/jsx-uses-react': 'off', // Not needed in React 17+
      'react/react-in-jsx-scope': 'off', // Not needed in React 17+
      'react/prop-types': 'off', // Using TypeScript instead
      'react/jsx-props-no-spreading': 'warn',
      'react/jsx-no-useless-fragment': 'error',
      'react/jsx-key': 'error',
      'react/no-array-index-key': 'warn',

      // General JavaScript/TypeScript rules
      'no-console': 'warn',
      'no-debugger': 'error',
      'no-alert': 'warn',
      'no-var': 'error',
      'prefer-const': 'error',
      'no-unused-expressions': 'error',
      'no-duplicate-imports': 'error',
      'no-multiple-empty-lines': ['error', { max: 2, maxEOF: 1 }],
      'eol-last': 'error',
      'comma-dangle': 'off',
      quotes: ['error', 'single', { avoidEscape: true }],
      semi: ['error', 'always'],

      // Import rules
      // 'import/order': [
      //   'error',
      //   {
      //     groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      //     'newlines-between': 'always',
      //     alphabetize: {
      //       order: 'asc',
      //       caseInsensitive: true,
      //     },
      //   },
      // ],
      'import/no-duplicates': 'error',
      'import/no-unresolved': 'off', // TypeScript handles this
    },
  },
  {
    files: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      'no-console': 'off',
    },
  },
];

export default eslintConfig;
