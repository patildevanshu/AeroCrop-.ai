# ── Stage 1: Build React Vite SPA ──────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Accept build-time API URL (e.g. https://api.yourdomain.com)
ARG VITE_API_URL="
ENV VITE_API_URL=

RUN npm run build

# ── Stage 2: Serve with Nginx ──────────────────────────────────────────────
FROM nginx:alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s \
 CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD [nginx, -g, daemon off;]
