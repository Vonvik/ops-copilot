# ---------- Stage 1: deps ----------
FROM node:20-slim AS deps
WORKDIR /app

RUN corepack enable

# Copiamos manifests y lockfiles (para cache)
COPY package.json ./
COPY pnpm-lock.yaml* yarn.lock* package-lock.json* ./

# Instalación según el gestor detectado
RUN set -eux; \
  if [ -f pnpm-lock.yaml ]; then \
    corepack prepare pnpm@9 --activate && pnpm install --frozen-lockfile; \
  elif [ -f yarn.lock ]; then \
    yarn install --frozen-lockfile; \
  elif [ -f package-lock.json ]; then \
    npm ci; \
  else \
    npm install; \
  fi

# ---------- Stage 2: build ----------
FROM node:20-slim AS build
WORKDIR /app

RUN corepack enable

# Build-arg para variables públicas (Next las lee en build time)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Si no existe public/, la creamos para que el COPY del runner no falle
RUN set -eux; \
  if [ ! -d public ]; then mkdir -p public; fi

# Asegura que exista next.config.* para que el COPY del runner no falle
RUN set -eux; \
  if [ ! -f next.config.js ] && [ ! -f next.config.mjs ] && [ ! -f next.config.ts ]; then \
    echo "module.exports = {}" > next.config.js; \
  fi

# Build Next.js
RUN set -eux; \
  if [ -f pnpm-lock.yaml ]; then corepack prepare pnpm@9 --activate && pnpm run build; \
  elif [ -f yarn.lock ]; then yarn build; \
  else npm run build; \
  fi

# ---------- Stage 3: runner ----------
FROM node:20-slim AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

RUN useradd -m nextjs

COPY --from=build /app/package.json ./package.json
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/next.config.* ./
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next

EXPOSE 3000

USER nextjs

CMD ["node", "node_modules/next/dist/bin/next", "start", "-p", "3000"]
