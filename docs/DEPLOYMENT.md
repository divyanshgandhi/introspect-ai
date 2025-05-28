# 🚀 Introspect AI Production Deployment Guide

This guide will walk you through deploying Introspect AI to a cloud VM with NGINX reverse proxy for the subdomain `www.divyanshgandhi.com/introspect`.

## 🏗️ Architecture Overview

```
Internet → NGINX (Port 80/443) → Frontend (React) + Backend (FastAPI)
                ↓
        www.divyanshgandhi.com/introspect → Frontend
        www.divyanshgandhi.com/introspect/api → Backend API
```

## 📋 Prerequisites

1. **Cloud VM** (Ubuntu 20.04+ recommended)
2. **Domain** pointing to your VM IP (`www.divyanshgandhi.com`)
3. **Docker & Docker Compose** installed
4. **Google/Gemini API keys**

## 🛠️ Step-by-Step Deployment

### Step 1: Set Up Your Cloud VM

1. **Create a VM** on your preferred cloud provider (AWS, DigitalOcean, etc.)
2. **Open ports** 80 and 443 in your firewall
3. **Point your domain** `www.divyanshgandhi.com` to your VM's IP address

### Step 2: Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Deploy the Application

1. **Clone the repository** to your VM:
```bash
git clone <your-repo-url> introspect-ai
cd introspect-ai
```

2. **Set up environment variables**:
```bash
cp environment.example .env
nano .env  # Edit with your actual API keys
```

Required environment variables:
```
GOOGLE_API_KEY=your_actual_google_api_key
GEMINI_API_KEY=your_actual_gemini_api_key
EXTRACT_MODEL=gemini-1.5-flash
PROMPT_MODEL=gemini-1.5-flash
VITE_API_URL=/introspect/api
```

3. **Make deployment script executable**:
```bash
chmod +x deploy.sh
```

4. **Deploy the application**:
```bash
./deploy.sh
```

### Step 4: Verify Deployment

1. **Check if containers are running**:
```bash
docker-compose -f docker-compose.prod.yml ps
```

2. **Test the application**:
- Visit: `http://your-vm-ip/introspect`
- Or: `http://www.divyanshgandhi.com/introspect` (if domain is configured)

3. **Monitor logs**:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔒 Setting Up HTTPS (Optional but Recommended)

### Step 1: Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Step 2: Obtain SSL Certificate

```bash
# Stop the current nginx container
docker-compose -f docker-compose.prod.yml stop nginx

# Get SSL certificate
sudo certbot certonly --standalone -d www.divyanshgandhi.com -d divyanshgandhi.com

# The certificates will be saved to:
# /etc/letsencrypt/live/www.divyanshgandhi.com/fullchain.pem
# /etc/letsencrypt/live/www.divyanshgandhi.com/privkey.pem
```

### Step 3: Update NGINX Configuration for SSL

1. **Copy SSL certificates to your project**:
```bash
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/www.divyanshgandhi.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/www.divyanshgandhi.com/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl/
```

2. **Update docker-compose.prod.yml** to use SSL configuration:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/ssl-nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/ssl:/etc/ssl:ro
    - ./nginx/logs:/var/log/nginx
```

3. **Redeploy with SSL**:
```bash
./deploy.sh
```

## 📊 Monitoring & Maintenance

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Update Application
```bash
git pull origin main
./deploy.sh
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Stop Application
```bash
docker-compose -f docker-compose.prod.yml down
```

## 🔧 Troubleshooting

### Common Issues

1. **Containers not starting**:
   - Check logs: `docker-compose -f docker-compose.prod.yml logs`
   - Verify .env file exists and has correct API keys

2. **Frontend not loading**:
   - Check if NGINX is running: `docker-compose -f docker-compose.prod.yml ps`
   - Verify domain DNS points to your VM IP

3. **API requests failing**:
   - Check backend logs: `docker-compose -f docker-compose.prod.yml logs backend`
   - Verify API keys are correct in .env file

4. **Port conflicts**:
   - Check if ports 80/443 are available: `sudo netstat -tlnp | grep :80`
   - Stop conflicting services: `sudo systemctl stop apache2` (if running)

### Health Check Endpoints

- **Application Health**: `http://your-domain/health`
- **Backend API**: `http://your-domain/introspect/api/health`

## 🎯 Performance Optimization

1. **Monitor resource usage**:
```bash
docker stats
```

2. **Scale services if needed**:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=2
```

3. **Clean up unused resources**:
```bash
docker system prune -a
```

## 🌐 Accessing Your Application

Once deployed, your Introspect AI application will be available at:

- **HTTP**: `http://www.divyanshgandhi.com/introspect`
- **HTTPS** (if configured): `https://www.divyanshgandhi.com/introspect`

The application features:
- 📁 File upload (PDF, images, etc.)
- 🎥 YouTube URL processing
- 🤖 AI-powered content extraction
- ✨ Personalized ChatGPT prompt generation

## 🆘 Support

If you encounter issues:

1. Check the logs as shown above
2. Verify all environment variables are set correctly
3. Ensure your domain DNS is configured properly
4. Make sure firewall allows ports 80 and 443

---

🎉 **Congratulations!** Your Introspect AI application is now running in production! 