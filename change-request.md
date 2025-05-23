# 🔗 Main Website Integration - Change Request

This document outlines the changes required in your main personal website (`www.divyanshgandhi.com`) to integrate the Introspect AI microservice.

## 🏗️ **Architecture Overview**

```
Internet → Main Website NGINX (SSL/HTTPS) → Microservices
         www.divyanshgandhi.com
         ├── / → Main Website Content
         ├── /introspect → Introspect AI Frontend (localhost:3000)
         └── /introspect/api → Introspect AI Backend (localhost:8000)
```

## 📋 **Required Changes**

### **1. NGINX Configuration Updates**

Add the following to your main website's nginx configuration file (usually `/etc/nginx/sites-available/www.divyanshgandhi.com` or similar):

```nginx
server {
    listen 443 ssl http2;
    server_name www.divyanshgandhi.com divyanshgandhi.com;

    # Your existing SSL configuration
    ssl_certificate /path/to/your/ssl/certificate.pem;
    ssl_certificate_key /path/to/your/ssl/private.key;
    
    # Your existing SSL settings...

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Your existing main website routes
    location / {
        # Your main website content
        # ... existing configuration ...
    }

    # ============= NEW: Introspect AI Routes =============
    
    # Rate limiting for API requests
    limit_req_zone $binary_remote_addr zone=introspect_api:10m rate=10r/s;

    # Introspect AI Frontend (React SPA)
    location /introspect {
        # Remove /introspect prefix when forwarding to frontend
        rewrite ^/introspect(.*) $1 break;
        
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Path /introspect;
        
        # Handle WebSocket upgrades (if needed for development)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Introspect AI API Backend (FastAPI)
    location /introspect/api {
        # Apply rate limiting
        limit_req zone=introspect_api burst=20 nodelay;
        
        # Remove /introspect prefix when forwarding to backend
        rewrite ^/introspect/api(.*) /api$1 break;
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle file uploads
        client_max_body_size 50M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
        
        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin "https://www.divyanshgandhi.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization" always;
    }

    # Health check endpoint for Introspect AI
    location /introspect/health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        access_log off;
    }
}

# Redirect HTTP to HTTPS (if not already configured)
server {
    listen 80;
    server_name www.divyanshgandhi.com divyanshgandhi.com;
    return 301 https://$server_name$request_uri;
}
```

### **2. Firewall Configuration**

Ensure your firewall allows the microservice ports (only locally accessible):

```bash
# These ports should only be accessible from localhost, not externally
# Verify ports 3000 and 8000 are NOT exposed to the internet
sudo ufw status

# If needed, explicitly block external access to these ports
sudo ufw deny 3000
sudo ufw deny 8000

# Ensure NGINX ports are open
sudo ufw allow 80
sudo ufw allow 443
```

### **3. SSL Certificate Management**

Your existing SSL certificate for `www.divyanshgandhi.com` will automatically cover the `/introspect` paths. No additional certificates needed.

If you're using Let's Encrypt, ensure your certificate covers both domains:

```bash
# Example Let's Encrypt renewal (adjust for your setup)
sudo certbot renew --nginx
```

### **4. System Service Management**

Create a systemd service file for the Introspect AI microservice:

```bash
# Create service file
sudo nano /etc/systemd/system/introspect-ai.service
```

```ini
[Unit]
Description=Introspect AI Microservice
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/introspect-ai
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable introspect-ai.service
sudo systemctl start introspect-ai.service
```

### **5. Monitoring and Logging**

Add log configuration for the new routes:

```nginx
# Add to your nginx configuration
log_format introspect_ai '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for" '
                        'rt=$request_time uct="$upstream_connect_time" '
                        'uht="$upstream_header_time" urt="$upstream_response_time"';

# Update the location blocks to use specific logging
location /introspect {
    # ... existing configuration ...
    access_log /var/log/nginx/introspect-ai-access.log introspect_ai;
    error_log /var/log/nginx/introspect-ai-error.log;
}

location /introspect/api {
    # ... existing configuration ...
    access_log /var/log/nginx/introspect-ai-api-access.log introspect_ai;
    error_log /var/log/nginx/introspect-ai-api-error.log;
}
```

## 🚀 **Deployment Workflow**

### **Step 1: Deploy Introspect AI Microservice**

```bash
# On your server, deploy the microservice
cd /path/to/introspect-ai
git pull origin main
./deploy.sh
```

### **Step 2: Update Main Website NGINX**

```bash
# Test nginx configuration
sudo nginx -t

# If successful, reload nginx
sudo nginx -s reload

# Or restart nginx service
sudo systemctl restart nginx
```

### **Step 3: Verify Integration**

```bash
# Check if microservices are running
curl http://localhost:3000
curl http://localhost:8000/health

# Check external access through main website
curl https://www.divyanshgandhi.com/introspect
curl https://www.divyanshgandhi.com/introspect/api/health
```

## 🔍 **Testing and Validation**

### **Automated Health Checks**

Add health check monitoring to your main website:

```bash
# Create monitoring script
cat << 'EOF' > /opt/scripts/check-introspect-ai.sh
#!/bin/bash

# Check if services are running
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend service down - restarting Introspect AI"
    systemctl restart introspect-ai
fi

if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend service down - restarting Introspect AI"
    systemctl restart introspect-ai
fi
EOF

chmod +x /opt/scripts/check-introspect-ai.sh

# Add to crontab for regular monitoring
echo "*/5 * * * * /opt/scripts/check-introspect-ai.sh" | crontab -
```

### **Manual Testing Checklist**

- [ ] Main website loads correctly: `https://www.divyanshgandhi.com/`
- [ ] Introspect AI loads: `https://www.divyanshgandhi.com/introspect`
- [ ] API health check: `https://www.divyanshgandhi.com/introspect/api/health`
- [ ] File upload works through the interface
- [ ] SSL certificate covers all paths
- [ ] No CORS errors in browser console
- [ ] Response times are acceptable (< 5s for normal requests)

## 🛠️ **Maintenance and Updates**

### **Updating Introspect AI**

```bash
# Standard update process
cd /path/to/introspect-ai
git pull origin main
./deploy.sh

# No changes needed to main website nginx
```

### **Logs and Monitoring**

```bash
# View Introspect AI logs
docker-compose -f /path/to/introspect-ai/docker-compose.prod.yml logs -f

# View NGINX logs for Introspect AI
tail -f /var/log/nginx/introspect-ai-access.log
tail -f /var/log/nginx/introspect-ai-error.log

# Monitor service status
systemctl status introspect-ai
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **502 Bad Gateway**: Service not running
   ```bash
   systemctl status introspect-ai
   systemctl restart introspect-ai
   ```

2. **404 Not Found**: NGINX routing issue
   ```bash
   sudo nginx -t
   sudo nginx -s reload
   ```

3. **CORS Errors**: Check CORS headers in API location block

4. **File Upload Fails**: Check `client_max_body_size` setting

5. **Slow Response**: Check proxy timeout settings

### **Debug Commands**

```bash
# Check if ports are occupied
sudo netstat -tlnp | grep -E ':3000|:8000'

# Test internal connections
curl -v http://localhost:3000
curl -v http://localhost:8000/health

# Check NGINX configuration
sudo nginx -T | grep -A 20 "location /introspect"
```

## 📊 **Performance Considerations**

### **Recommended Settings**

```nginx
# Add to your nginx.conf http block
upstream introspect_frontend {
    server localhost:3000;
    keepalive 32;
}

upstream introspect_backend {
    server localhost:8000;
    keepalive 32;
}

# Update location blocks to use upstreams
location /introspect {
    proxy_pass http://introspect_frontend;
    # ... rest of configuration
}

location /introspect/api {
    proxy_pass http://introspect_backend;
    # ... rest of configuration
}
```

### **Caching Configuration** (Optional)

```nginx
# Cache static assets from frontend
location ~* /introspect/.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    proxy_pass http://introspect_frontend;
    proxy_cache_valid 200 1d;
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

## ✅ **Summary of Changes**

| Component | Change Required | Impact |
|-----------|----------------|--------|
| NGINX Config | Add routing rules for `/introspect` | Routes traffic to microservice |
| Firewall | Verify ports 3000/8000 not exposed | Security |
| SSL Certificate | No change needed | Existing cert covers new paths |
| System Service | Create introspect-ai.service | Auto-start microservice |
| Monitoring | Add health checks | Service reliability |
| Logging | Add specific log files | Debugging and analytics |

## 🎯 **Next Steps**

1. **Review** this change request with your main website codebase
2. **Test** the configuration in a staging environment if available
3. **Deploy** the NGINX changes during a maintenance window
4. **Monitor** the integration for the first 24-48 hours
5. **Document** any additional customizations for your specific setup

---

**📞 Need Help?** 
- Check the troubleshooting section above
- Review logs using the provided commands
- Verify each component individually before testing the full integration