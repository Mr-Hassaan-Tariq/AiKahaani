# TubeGenius - Full-Stack Django & Next.js Platform

A modern, scalable full-stack web platform built with Django REST Framework and Next.js 15. TubeGenius provides a robust foundation for building web applications with microsite architecture, type-safe API integration, and comprehensive development tooling.

## 🚀 Features

### **Backend (Django)**
- **Django REST Framework** - Robust API development
- **JWT Authentication** - Secure token-based authentication
- **OpenAPI/Swagger** - Auto-generated API documentation
- **Custom User Model** - Extended Django user with profile management
- **Modern Admin Theme** - Django Unfold for beautiful admin interface
- **Comprehensive Testing** - pytest with factory-boy for test data
- **Database Management** - PostgreSQL with migrations

### **Frontend (Next.js)**
- **Dual Frontend Architecture** - Separate applications for main site and platform
- **Next.js 15** - Latest React framework with App Router
- **React 19** - Latest React features and performance improvements
- **TypeScript** - Type-safe development experience
- **Microsite Architecture** - Multiple frontend applications sharing common packages
- **API Type Safety** - Generated TypeScript types from Django backend
- **Server Actions** - Form handling and API communication
- **Tailwind CSS v4** - Modern utility-first CSS framework
- **Authentication** - NextAuth.js with JWT integration
- **Code Quality** - ESLint, Prettier, and comprehensive linting setup

### **Development & DevOps**
- **Docker Compose** - One-command full-stack development
- **VS Code Integration** - Dev containers and pre-configured tasks
- **Hot Reloading** - Fast development with Turbopack
- **Environment Management** - Flexible configuration system
- **Package Management** - pnpm workspaces for frontend, uv for backend

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (v2.0+)
- **Git**
- **VS Code** (recommended with Dev Containers extension)

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Mr-Hassaan-Tariq/Tubegenius
cd Tubegenius
```

### 2. Configure Environment Variables

Set up environment files for backend and frontend applications:

```bash
# Backend environment
cp .env.backend.template .env.backend

# Main frontend environment
cp .env.frontend.template .env.frontend

# Platform frontend environment (if needed)
cp .env.frontend-platform.template .env.frontend-platform
```

**Important**: Update the following in your environment files:

- **Backend** (`.env.backend`):
  - `SECRET_KEY` - Django secret key
  - `DEBUG=1` - Enable debug mode
  - `DATABASE_PASSWORD` - PostgreSQL password

- **Main Frontend** (`.env.frontend`):
  - `NEXTAUTH_SECRET` - Generate with: `openssl rand -base64 32`

- **Platform Frontend** (`.env.frontend-platform`):
  - `NEXTAUTH_SECRET` - Generate with: `openssl rand -base64 32`

### 3. Start the Application

```bash
docker compose up
```

### 4. Access the Application

After successful startup, access the following services:

- **Main Frontend Application**: http://localhost:3000
- **Platform Frontend Application**: http://localhost:3001 (if configured)
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/api/schema/swagger-ui/
- **Django Admin**: http://localhost:8000/admin/

### 5. Create Superuser

```bash
docker compose exec api uv run -- python manage.py createsuperuser
```

## 🏗️ Project Structure

```
Tubegenius/
├── backend/                 # Django REST API
│   ├── api/                # Django application
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # API serializers
│   │   ├── views.py        # API views
│   │   ├── urls.py         # URL routing
│   │   └── tests/          # Test suite
│   ├── manage.py           # Django management
│   └── pyproject.toml      # Python dependencies
├── frontend/               # Main Next.js application
│   ├── apps/              # Microsite applications
│   │   └── web/           # Main web application
│   ├── packages/          # Shared packages
│   │   ├── types/         # Generated API types
│   │   └── ui/            # Shared UI components
│   └── package.json       # Node.js dependencies
├── frontend-platform/      # Platform-specific Next.js application
│   ├── apps/              # Microsite applications
│   │   └── web/           # Platform web application
│   ├── packages/          # Shared packages
│   │   ├── types/         # Generated API types
│   │   └── ui/            # Shared UI components
│   └── package.json       # Node.js dependencies
├── docker-compose.yaml     # Container orchestration
└── README.md              # This file
```

## 🔧 Development

### Backend Development

#### Adding Dependencies

```bash
# Add new Python package
docker compose exec api uv add package-name

# Add development dependency
docker compose exec api uv add --dev package-name
```

#### Running Tests

```bash
# Run all tests
docker compose exec api uv run -- pytest .

# Run specific test file
docker compose exec api uv run -- pytest api/tests/test_api.py

# Run specific test
docker compose exec api uv run -- pytest api/tests/test_api.py -k "test_name"
```

#### Database Operations

```bash
# Create migrations
docker compose exec api uv run -- python manage.py makemigrations

# Apply migrations
docker compose exec api uv run -- python manage.py migrate

# Create superuser
docker compose exec api uv run -- python manage.py createsuperuser
```

### Frontend Development

The project includes two separate frontend applications:

- **`frontend/`** - Main application (runs on port 3000)
- **`frontend-platform/`** - Platform-specific application (can be configured for different ports)

#### Package Management

```bash
# Main frontend - Add global dependency (shared across all microsites)
docker compose exec web pnpm add package-name -w

# Main frontend - Add site-specific dependency
docker compose exec web pnpm --filter web add package-name

# Main frontend - Add development dependency
docker compose exec web pnpm add -D package-name -w

# Platform frontend - Add dependencies (run from frontend-platform directory)
cd frontend-platform
pnpm add package-name
```

#### Code Quality

```bash
# Main frontend - Lint code
docker compose exec web pnpm lint

# Main frontend - Fix linting issues
docker compose exec web pnpm lint:fix

# Main frontend - Format code
docker compose exec web pnpm prettier:fix

# Main frontend - Type checking
docker compose exec web pnpm type-check

# Main frontend - Generate API types
docker compose exec web pnpm openapi:generate

# Platform frontend - Run quality checks (from frontend-platform directory)
cd frontend-platform
pnpm lint
pnpm type-check
```

#### Available Scripts

**Main Frontend (`frontend/`)** - Available via Docker:

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm start` | Start production server |
| `pnpm lint` | Check for linting errors |
| `pnpm lint:fix` | Auto-fix linting issues |
| `pnpm format` | Format code and fix issues |
| `pnpm type-check` | Run TypeScript checking |
| `pnpm openapi:generate` | Generate API types |

**Platform Frontend (`frontend-platform/`)** - Run locally:

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm start` | Start production server |
| `pnpm lint` | Check for linting errors |
| `pnpm lint:fix` | Auto-fix linting issues |
| `pnpm format` | Format code and fix issues |
| `pnpm type-check` | Run TypeScript checking |

## 🔐 Authentication

TubeGenius uses JWT-based authentication with Django Simple JWT on the backend and NextAuth.js on the frontend.

### Backend Authentication

- **JWT Tokens**: Access and refresh token system
- **User Model**: Extended Django user with profile fields
- **Admin Interface**: Modern admin theme with user management

### Frontend Authentication

- **NextAuth.js**: Credentials provider with JWT
- **Protected Routes**: Server-side session validation
- **User Registration**: Account creation with admin activation

### Environment Configuration

```env
# Backend (.env.backend)
SECRET_KEY=your-django-secret-key
DEBUG=1

# Frontend (.env.frontend)
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## 🔌 API Integration

### Server Actions

The frontend uses Next.js Server Actions for API communication:

```typescript
// Example server action
export async function fetchUserData() {
  const client = getApiClient();
  const response = await client.users.usersMeRetrieve();
  return response.data;
}
```

### API Client

- **Generated Client**: TypeScript client from OpenAPI schema
- **Type Safety**: Full type coverage for API responses
- **Authentication**: Automatic token handling

### Updating API Types

After backend changes, regenerate TypeScript types:

```bash
docker compose exec web pnpm openapi:generate
```

## 🧪 Testing

### Backend Testing

The project uses pytest with comprehensive test setup:

- **pytest-django**: Django testing utilities
- **pytest-factoryboy**: Test data generation
- **Test Structure**: Organized in `backend/api/tests/`

### Running Tests

```bash
# All tests
docker compose exec api uv run -- pytest .

# Specific file
docker compose exec api uv run -- pytest api/tests/test_api.py

# Specific test
docker compose exec api uv run -- pytest -k "test_name"
```

## 🐳 Docker Development

### Container Management

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Stop all services
docker compose down

# Rebuild containers
docker compose up --build

# View logs
docker compose logs -f
```

### Individual Services

```bash
# Backend only
docker compose up api

# Main frontend only
docker compose up web

# Database only
docker compose up db

# Platform frontend (run locally)
cd frontend-platform
pnpm dev
```

## 💻 VS Code Development

The project includes comprehensive VS Code configuration:

### Dev Containers

- **Backend Container**: Python development environment
- **Frontend Container**: Node.js development environment
- **Automatic Setup**: Pre-configured extensions and settings

### Features

- **Hot Reloading**: Automatic code reloading
- **IntelliSense**: Full TypeScript and Python support
- **Debugging**: Pre-configured debug configurations
- **Tasks**: Automated development tasks

### Getting Started

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Click "Reopen in Container" when prompted
4. Select your preferred development container

## 🚀 Deployment

### Production Build

```bash
# Build main frontend
docker compose exec web pnpm build

# Build platform frontend (run locally)
cd frontend-platform
pnpm build

# Collect static files (backend)
docker compose exec api uv run -- python manage.py collectstatic

# Run migrations
docker compose exec api uv run -- python manage.py migrate
```

### Environment Variables

Configure production environment variables:

```env
# Production settings
DEBUG=0
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run quality checks**
   ```bash
   # Backend
   docker compose exec api uv run -- pytest

   # Frontend
   docker compose exec web pnpm lint
   docker compose exec web pnpm type-check
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Quality Standards

- **Backend**: Follow PEP 8 and Django conventions
- **Frontend**: Use ESLint and Prettier configurations
- **Testing**: Maintain test coverage
- **Documentation**: Update relevant documentation

## 📚 Documentation

- [Frontend README](./frontend/README.md) - Detailed frontend documentation
- [Linting Guide](./frontend/LINTING.md) - Code quality setup
- [Django Documentation](https://docs.djangoproject.com/) - Django framework guide
- [Next.js Documentation](https://nextjs.org/docs) - Next.js framework guide
- [Docker Documentation](https://docs.docker.com/) - Container platform guide

## 🐛 Troubleshooting

### Common Issues

**Docker Issues**
```bash
# Container not starting
docker compose down
docker compose up --build

# Permission issues
sudo chown -R $USER:$USER .
```

**Database Issues**
```bash
# Reset database
docker compose down -v
docker compose up
```

**Frontend Issues**
```bash
# Clear main frontend node modules
docker compose exec web rm -rf node_modules pnpm-lock.yaml
docker compose exec web pnpm install

# Clear platform frontend node modules (run locally)
cd frontend-platform
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Backend Issues**
```bash
# Clear Python cache
docker compose exec api find . -type d -name "__pycache__" -exec rm -r {} +
```

### Performance Optimization

- **Frontend**: Use Turbopack for faster builds
- **Backend**: Enable database query optimization
- **Docker**: Use volume caching for dependencies

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [Next.js](https://nextjs.org/) - React framework
- [Docker](https://www.docker.com/) - Container platform
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety

## 📞 Support

For support and questions:

- **Issues**: Create an issue in the repository
- **Documentation**: Check the documentation links above
- **Community**: Join our development community

---

**Built with ❤️ using Django, Next.js, and modern web technologies**
