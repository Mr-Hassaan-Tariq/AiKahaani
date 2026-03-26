FROM node:20-alpine

# Enable pnpm via corepack (matches packageManager field in package.json)
RUN corepack enable && corepack prepare pnpm@9.14.2 --activate

WORKDIR /app

# Install dependencies as a cached layer; actual node_modules are preserved
# in a named volume in dev so they survive source-code bind-mount overrides.
COPY package.json ./
RUN pnpm install

# Copy source (overridden by bind-mount in dev).
COPY . .

EXPOSE 3000
