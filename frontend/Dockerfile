FROM node:20-alpine
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
ENV HOST=0.0.0.0
CMD ["yarn", "start"]
