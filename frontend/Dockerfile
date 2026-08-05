FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install curl/wget for health check
RUN apk add --no-cache curl

# Copy package management files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy frontend source files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:5173/ || exit 1

# Default command to run Vite with host 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
