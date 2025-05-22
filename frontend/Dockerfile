FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
ENV VITE_API_URL=http://backend:8000

# Expose the port
EXPOSE 8080

# Command to run the application in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 