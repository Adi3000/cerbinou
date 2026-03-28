FROM node:22-alpine

WORKDIR /app

COPY package*.json tsconfig.json *.ts ./

RUN mkdir -p /data && npm install && npm run build

COPY --chown=node:node . .

CMD ["npm", "start"]