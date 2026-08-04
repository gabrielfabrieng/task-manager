# syntax=docker/dockerfile:1

# --- deps: install once, cache by lockfile ---
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

# --- development: Vite dev server with HMR ---
FROM deps AS development
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# --- build: produce static assets ---
FROM deps AS build
COPY . .
RUN npm run build

# --- production: serve built assets via Nginx ---
FROM nginx:1.27-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.prod.conf /etc/nginx/conf.d/default.conf
