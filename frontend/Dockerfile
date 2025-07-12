FROM node:20-alpine

WORKDIR /app

# create a non-root user for running the app
RUN adduser -D appuser

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN chown -R appuser:appuser /app

# switch to the unprivileged user
USER appuser

ENV HOST=0.0.0.0
CMD ["yarn", "start"]
