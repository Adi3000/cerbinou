FROM node:24-alpine AS build


WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production=false

COPY . /app
RUN npx tsc

# Docker for final image
FROM node:24-alpine

WORKDIR /app

COPY --from=build /app/package.json ./package.json
COPY --from=build /app/package-lock.json ./package-lock.json
COPY --from=build /app/dist ./dist

RUN npm ci --omit=dev

CMD ["node", "dist/index.js"]