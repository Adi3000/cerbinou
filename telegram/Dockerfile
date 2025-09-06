# COMPILE PHASE
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# IMAGE BUILD
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --omit=dev

COPY --chown=node:node --from=builder /app/dist ./dist

CMD ["node", "dist/index.js"]
