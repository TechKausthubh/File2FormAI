FROM node:20.19.5-alpine

WORKDIR /workspace
RUN corepack enable

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile --filter @file2formai/web...

COPY apps/web apps/web
WORKDIR /workspace/apps/web

EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
