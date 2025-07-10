FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY --chown=node:node . .

CMD ["npm", "start"]