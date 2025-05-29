FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
ENV VITE_API_URL=""
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install Node.js for frontend serving
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy and set up backend
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Copy built frontend
WORKDIR /app/frontend
COPY --from=frontend-build /frontend/dist ./dist
RUN npm install -g serve

# Setup start script
WORKDIR /app
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8010
EXPOSE 8080

CMD ["./start.sh"] 