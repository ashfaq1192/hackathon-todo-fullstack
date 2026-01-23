# Multi-stage Dockerfile for Next.js Frontend
# Target: <500MB final image size

# =============================================================================
# Stage 1: Dependencies - Install node_modules
# =============================================================================
FROM node:22-alpine AS deps

WORKDIR /app

# Install dependencies required for native modules
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./

# Install dependencies based on lockfile
RUN \
    if [ -f pnpm-lock.yaml ]; then \
        corepack enable pnpm && pnpm install --frozen-lockfile; \
    elif [ -f yarn.lock ]; then \
        yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then \
        npm ci; \
    else \
        npm install; \
    fi

# =============================================================================
# Stage 2: Builder - Build the application
# =============================================================================
FROM node:22-alpine AS builder

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Add standalone output to next.config.js if not present
RUN if ! grep -q "output.*standalone" next.config.js 2>/dev/null; then \
        echo "Adding standalone output to next.config.js"; \
        sed -i 's/const nextConfig = {/const nextConfig = {\n  output: "standalone",/' next.config.js; \
    fi

# Build the application
RUN npm run build

# =============================================================================
# Stage 3: Runner - Production image
# =============================================================================
FROM node:22-alpine AS runner

WORKDIR /app

# Set environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Copy standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Run the application
CMD ["node", "server.js"]
