# TubeGenius Platform Frontend

A modern, high-performance platform-specific frontend application built with Next.js 15, React 19, and TypeScript. This frontend serves as a dedicated platform interface for the TubeGenius ecosystem, providing specialized features and functionality separate from the main application.

## 🚀 Features

- **Next.js 15** - Latest React framework with App Router
- **React 19** - Latest React features and performance improvements
- **TypeScript** - Type-safe development experience
- **Tailwind CSS v4** - Modern utility-first CSS framework
- **Platform-Specific Features** - Dedicated functionality for platform management
- **Microsite Architecture** - Multiple frontend applications sharing common packages
- **API Type Safety** - Generated TypeScript types from Django backend
- **Server Actions** - Form handling and API communication
- **ESLint + Prettier** - Comprehensive code quality and formatting
- **Turbopack** - Fast development builds
- **Responsive Design** - Mobile-first approach
- **Authentication** - JWT-based auth with NextAuth.js
- **Independent Deployment** - Can be deployed separately from main frontend

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18.17 or higher)
- **pnpm** (recommended) or npm/yarn
- **Docker & Docker Compose** (for full-stack development)
- **Git**

## 🛠️ Installation

### Option 1: Full Stack with Docker (Main Frontend)

1. **Clone the repository**

   ```bash
   git clone https://github.com/Mr-Hassaan-Tariq/Tubegenius
   cd Tubegenius
   ```

2. **Configure environment files**

   ```bash
   cp .env.backend.template .env.backend
   cp .env.frontend.template .env.frontend
   ```

3. **Start the entire stack**

   ```bash
   docker compose up
   ```

   Access the application at:
   - Main Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Swagger UI: http://localhost:8000/api/schema/swagger-ui/

### Option 2: Platform Frontend Development (This Application)

1. **Navigate to platform frontend directory**

   ```bash
   cd frontend-platform
   ```

2. **Install dependencies**

   ```bash
   pnpm install
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server**

   ```bash
   pnpm dev
   ```

   Access the platform frontend at: http://localhost:3000

## 🏗️ Project Structure

```
frontend-platform/
├── apps/                    # Microsite applications
│   └── web/                # Platform web application
│       ├── app/            # Next.js App Router pages
│       ├── actions/        # Server actions for API calls
│       ├── lib/            # Utility functions and configurations
│       └── components/     # Platform-specific components
├── packages/               # Shared packages between microsites
│   ├── types/             # Generated TypeScript types from backend
│   └── ui/                # Shared UI component library
├── public/                # Static assets
├── .vscode/               # VS Code settings
├── eslint.config.mjs      # ESLint configuration
├── .prettierrc           # Prettier configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

## 🏃‍♂️ Development

### Starting the Development Server

```bash
# Local development (recommended for platform frontend)
cd frontend-platform
pnpm dev

# With Docker (for main frontend)
docker compose exec web pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the platform frontend.

### Available Scripts

| Command                 | Description                                |
| ----------------------- | ------------------------------------------ |
| `pnpm dev`              | Start development server with Turbopack    |
| `pnpm build`            | Build the application for production       |
| `pnpm start`            | Start the production server                |
| `pnpm lint`             | Check for linting errors                   |
| `pnpm lint:fix`         | Auto-fix linting issues                    |
| `pnpm prettier:check`   | Check code formatting                      |
| `pnpm prettier:fix`     | Format code with Prettier                  |
| `pnpm format`           | Format code and fix linting issues         |
| `pnpm type-check`       | Run TypeScript type checking               |
| `pnpm openapi:generate` | Generate TypeScript types from backend API |

**Note**: This platform frontend runs independently and can be configured to use different ports or domains as needed.

## 🎨 Code Quality

This project uses a comprehensive code quality setup to ensure maintainable and consistent code.

### Linting & Formatting

- **ESLint** - JavaScript/TypeScript linting with Next.js and React rules
- **Prettier** - Code formatting for consistent style
- **TypeScript** - Static type checking

### Code Style

The project enforces consistent code style through:

- **Single quotes** for strings
- **2-space indentation**
- **80-character line width**
- **Trailing commas** in objects and arrays
- **Semicolons** required
- **Organized imports** with automatic sorting

### VS Code Integration

The project includes VS Code settings (`.vscode/settings.json`) that:

- Auto-format on save using Prettier
- Auto-fix ESLint issues on save
- Organize imports automatically
- Provide Tailwind CSS IntelliSense

### Recommended Extensions

For the best development experience, install these VS Code extensions:

1. **ESLint** (`dbaeumer.vscode-eslint`)
2. **Prettier** (`esbenp.prettier-vscode`)
3. **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)
4. **TypeScript Importer** (`pmneo.tsimporter`)

## 🔧 Configuration Files

### ESLint (`eslint.config.mjs`)

- Extends Next.js and TypeScript configurations
- Includes React-specific rules
- Enforces import ordering
- Prevents common JavaScript/TypeScript issues

### Prettier (`.prettierrc`)

- Consistent code formatting rules
- Single quotes, 2-space indentation
- 80-character line width
- Trailing commas for cleaner diffs

### TypeScript (`tsconfig.json`)

- Strict type checking enabled
- Next.js optimizations
- Path mapping for clean imports

## 🔌 API Integration

### Server Actions

The frontend uses Next.js Server Actions for API communication with the Django backend. Server actions are located in `apps/web/actions/` and handle:

- Form submissions
- Data fetching
- Authentication
- CRUD operations

### API Client

The project includes a generated API client using `openapi-typescript-codegen`:

```typescript
import { getApiClient } from '@/lib/api';

// Example usage in server action
export async function fetchUserData() {
  const client = getApiClient();
  const response = await client.users.usersMeRetrieve();
  return response.data;
}
```

### Updating API Types

After backend changes, regenerate TypeScript types:

```bash
# Local development (platform frontend)
cd frontend-platform
pnpm openapi:generate

# With Docker (main frontend)
docker compose exec web pnpm openapi:generate
```

## 🔐 Authentication

The frontend uses NextAuth.js for authentication with JWT tokens from the Django backend.

### Configuration

1. **Set environment variables** in `.env.frontend`:

   ```env
   NEXTAUTH_SECRET=your-secret-key
   NEXTAUTH_URL=http://localhost:3000
   ```

2. **Generate secret key**:
   ```bash
   openssl rand -base64 32
   ```

### Protected Routes

Use `getServerSession` to protect routes:

```typescript
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '@/lib/auth';

export default async function ProtectedPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect('/login');
  }

  return <div>Protected content</div>;
}
```

## 📦 Package Management

### Adding Global Dependencies

For dependencies shared across all microsites:

```bash
# Local development (platform frontend)
cd frontend-platform
pnpm add package-name -w

# With Docker (main frontend)
docker compose exec web pnpm add package-name -w
```

### Adding Site-Specific Dependencies

For dependencies specific to a microsite:

```bash
# Local development (platform frontend)
cd frontend-platform
pnpm --filter web add package-name

# With Docker (main frontend)
docker compose exec web pnpm --filter web add package-name
```

### Using Shared Packages

Install shared packages in microsites:

```bash
# Local development (platform frontend)
cd frontend-platform
pnpm --filter web add @frontend/ui

# With Docker (main frontend)
docker compose exec web pnpm --filter web add @frontend/ui
```

## 🚀 Deployment

### Production Build

```bash
# Local development (platform frontend)
cd frontend-platform
pnpm build
pnpm start

# With Docker (main frontend)
docker compose exec web pnpm build
docker compose exec web pnpm start
```

### Environment Variables

Create a `.env.local` file with the following variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000

# Analytics (optional)
NEXT_PUBLIC_GA_ID=your-ga-id
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run quality checks**
   ```bash
   pnpm format
   pnpm lint
   pnpm type-check
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Commit Guidelines

- Use conventional commit messages
- Include descriptive commit messages
- Reference issues when applicable

## 📚 Documentation

- [Linting Guide](./LINTING.md) - Detailed linting configuration and usage
- [Main Project README](../README.md) - Full project documentation and dual frontend architecture
- [Main Frontend README](../frontend/README.md) - Main frontend application documentation
- [Next.js Documentation](https://nextjs.org/docs) - Next.js features and API
- [React Documentation](https://react.dev) - React features and best practices
- [TypeScript Handbook](https://www.typescriptlang.org/docs/) - TypeScript guide

## 🐛 Troubleshooting

### Common Issues

**ESLint errors after installation**

```bash
pnpm lint:fix
```

**Prettier formatting issues**

```bash
pnpm prettier:fix
```

**TypeScript errors**

```bash
pnpm type-check
```

**Dependencies issues**

```bash
# Platform frontend
cd frontend-platform
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Main frontend (Docker)
docker compose exec web rm -rf node_modules pnpm-lock.yaml
docker compose exec web pnpm install
```

**API types out of sync**

```bash
# Platform frontend
cd frontend-platform
pnpm openapi:generate

# Main frontend (Docker)
docker compose exec web pnpm openapi:generate
```

### Performance Issues

- Use Turbopack for faster development builds
- Enable React DevTools for debugging
- Monitor bundle size with `@next/bundle-analyzer`

### Docker Issues

**Container not starting**

```bash
docker compose down
docker compose up --build
```

**Permission issues**

```bash
sudo chown -R $USER:$USER .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE.md) file for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org) - React framework
- [Vercel](https://vercel.com) - Deployment platform
- [Tailwind CSS](https://tailwindcss.com) - CSS framework
- [TypeScript](https://www.typescriptlang.org) - Type safety
- [Django](https://www.djangoproject.com) - Backend framework

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the troubleshooting section above
- Refer to the [main project README](../README.md) for full-stack guidance
- Check the [main frontend README](../frontend/README.md) for main application details

## 🔄 Platform Frontend vs Main Frontend

This platform frontend is designed to run independently from the main frontend application:

- **Independent Development**: Can be developed and deployed separately
- **Different Use Cases**: Platform-specific features and functionality
- **Flexible Configuration**: Can be configured for different ports, domains, or environments
- **Shared Backend**: Both frontends connect to the same Django API backend
- **Code Sharing**: Can share common packages and utilities with the main frontend

---

**Built with ❤️ using Next.js, React, and TypeScript for the TubeGenius Platform**
