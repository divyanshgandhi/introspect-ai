FROM alpine:latest

WORKDIR /app

# Install dependencies
RUN apk add --no-cache \
    curl \
    docker \
    docker-compose \
    bash \
    git

# Copy project files
COPY . .

# Default command to run the entire system
CMD ["docker-compose", "up"] 