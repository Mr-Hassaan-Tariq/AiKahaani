# Linting Configuration Guide

This project uses a comprehensive linting setup with ESLint, Prettier, and TypeScript for code quality and consistency.

## Setup

The linting configuration is already set up with the following tools:

- **ESLint**: JavaScript/TypeScript linting with Next.js and React rules
- **Prettier**: Code formatting
- **TypeScript**: Type checking
- **lint-staged**: Pre-commit hooks (configured in package.json)

## Available Scripts

```bash
# Lint code for errors
npm run lint

# Lint and auto-fix errors
npm run lint:fix

# Check Prettier formatting
npm run prettier:check

# Format code with Prettier
npm run prettier:fix

# Format code and fix linting issues
npm run format

# Type checking
npm run type-check
```

## Configuration Files

### ESLint (`.eslint.config.mjs`)

- Extends Next.js and TypeScript configurations
- Includes React-specific rules
- Enforces import ordering
- Prevents common JavaScript/TypeScript issues

### Prettier (`.prettierrc`)

- Single quotes for strings
- 2-space indentation
- 80 character line width
- Trailing commas in objects and arrays
- Semicolons required

### TypeScript (`tsconfig.json`)

- Strict type checking enabled
- Next.js optimizations
- Path mapping for clean imports

## VS Code Integration

The `.vscode/settings.json` file configures VS Code to:

- Format on save using Prettier
- Auto-fix ESLint issues on save
- Organize imports automatically
- Provide Tailwind CSS IntelliSense

## Recommended Extensions

Install these VS Code extensions for the best development experience:

1. **ESLint** (`dbaeumer.vscode-eslint`)
2. **Prettier** (`esbenp.prettier-vscode`)
3. **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)
4. **TypeScript Importer** (`pmneo.tsimporter`)

## Pre-commit Hooks

The project uses `lint-staged` to run linting and formatting on staged files before commits. This ensures code quality in the repository.

## Common Issues and Solutions

### Import Order Issues

ESLint enforces a specific import order:

1. Built-in Node.js modules
2. External dependencies
3. Internal modules
4. Relative imports

### TypeScript Errors

- Use `npm run type-check` to check for type errors
- Ensure all props are properly typed
- Avoid using `any` type (use `unknown` or proper types instead)

### Prettier Conflicts

If you have formatting conflicts:

1. Run `npm run prettier:fix` to format all files
2. Configure your editor to use Prettier as the default formatter
3. Enable "Format on Save" in VS Code

## Customizing Rules

### Adding ESLint Rules

Edit the `rules` section in `eslint.config.mjs`:

```javascript
rules: {
  // Your custom rules here
  'your-rule': 'error'
}
```

### Modifying Prettier Settings

Edit `.prettierrc` to change formatting preferences:

```json
{
  "printWidth": 100,
  "tabWidth": 4
}
```

## Best Practices

1. **Run linting before commits**: Use `npm run format` to ensure code quality
2. **Fix warnings**: Don't ignore ESLint warnings, fix them
3. **Use TypeScript**: Leverage TypeScript for better type safety
4. **Consistent formatting**: Let Prettier handle all formatting decisions
5. **Import organization**: Let ESLint organize your imports automatically

## Troubleshooting

### ESLint Not Working

1. Ensure ESLint extension is installed in VS Code
2. Check that `eslint.config.mjs` is properly configured
3. Restart VS Code after configuration changes

### Prettier Conflicts

1. Make sure Prettier extension is installed
2. Set Prettier as default formatter in VS Code
3. Check for conflicting formatting extensions

### TypeScript Errors

1. Run `npm run type-check` to see all type errors
2. Ensure all dependencies are properly installed
3. Check `tsconfig.json` configuration
