FROM node:20-alpine
WORKDIR /app

# Copy dependency files and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code and build for production
COPY . .
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "run", "start"]
