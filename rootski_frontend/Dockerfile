FROM node:16.9.1

WORKDIR /app

COPY ./package.json ./package.json
RUN npm install --force

COPY . .

CMD npm run start
