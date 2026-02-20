# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: run
FROM node:20-alpine
ARG PROJECT_NAME=auto-dbms-ui
WORKDIR /app
COPY --from=builder /app/dist/${PROJECT_NAME} ./dist/${PROJECT_NAME}
EXPOSE 4000
ENV PORT=4000
CMD ["sh", "-c", "node dist/${PROJECT_NAME}/server/server.mjs"]
