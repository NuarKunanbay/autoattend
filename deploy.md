# 🚀 Deployment Guide

This guide covers multiple ways to deploy your attendance server to run 24/7.

## 🐳 Option 1: Docker Deployment (Recommended)

### Local Docker
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Cloud Docker Platforms

#### Railway.app (Free tier available)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Render.com
1. Connect your GitHub repository
2. Select "Docker" as deployment method
3. Set build command: `docker build -t attendance-server .`
4. Set start command: `docker run -p 5000:5000 attendance-server`

#### DigitalOcean App Platform
1. Create new app from GitHub
2. Select Docker deployment
3. Configure environment variables if needed

## ☁️ Option 2: Cloud VPS

### DigitalOcean Droplet ($5/month)
```bash
# Create Ubuntu 22.04 droplet
# SSH into server
ssh root@your-server-ip

# Install dependencies
apt update && apt upgrade -y
apt install python3 python3-pip git curl -y

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt update && apt install google-chrome-stable -y

# Clone and setup
git clone https://github.com/yourusername/autoattend.git
cd autoattend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure credentials (edit main.py)
nano main.py

# Run as systemd service
sudo cp attendance-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable attendance-server
sudo systemctl start attendance-server
```

### AWS EC2 (Free tier available)
```bash
# Launch Ubuntu 22.04 t2.micro instance
# SSH and follow same steps as DigitalOcean
```

### Google Cloud Platform
```bash
# Create Compute Engine instance
# SSH and follow same steps as DigitalOcean
```

## 🎯 Option 3: Platform-as-a-Service

### Heroku (Free tier discontinued, but still works)
```bash
# Install Heroku CLI
# Login and deploy
heroku login
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Set environment variables
heroku config:set USERNAME=your_username
heroku config:set PASSWORD=your_password
```

### Vercel (Serverless)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## 🔧 Option 4: Home Server Setup

### Raspberry Pi
```bash
# Install Raspberry Pi OS
# SSH into Pi
ssh pi@your-pi-ip

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git -y

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=armhf] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install google-chrome-stable -y

# Setup application (same as VPS)
```

## 📊 Monitoring Your Deployment

### Health Checks
```bash
# Check if server is running
curl http://your-server:5000/health

# Get detailed status
curl http://your-server:5000/status
```

### Log Monitoring
```bash
# Docker logs
docker-compose logs -f

# Systemd logs
sudo journalctl -u attendance-server -f

# Application logs
tail -f attendance_server.log
```

## 🔐 Security Considerations

### Environment Variables
Instead of hardcoding credentials, use environment variables:

```python
import os
USERNAME = os.getenv('USERNAME', '')
PASSWORD = os.getenv('PASSWORD', '')
```

### Set in deployment:
```bash
# Docker
docker run -e USERNAME=your_user -e PASSWORD=your_pass your-image

# Systemd service
# Edit service file to include:
Environment=USERNAME=your_username
Environment=PASSWORD=your_password
```

## 💰 Cost Comparison

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| Railway.app | Free tier | Easy deployment | Limited resources |
| Render.com | Free tier | Simple setup | Sleeps after inactivity |
| DigitalOcean | $5/month | Full control | Manual setup |
| AWS EC2 | Free tier | Scalable | Complex setup |
| Heroku | $7/month | Easy deployment | Expensive |
| Home Server | $0 | Full control | Requires maintenance |

## 🚨 Important Notes

1. **Chrome Installation**: Most cloud platforms require Chrome to be installed
2. **Port Configuration**: Ensure port 5000 is open/exposed
3. **Credentials**: Never commit credentials to version control
4. **Monitoring**: Set up alerts for server downtime
5. **Backups**: Regular backups of configuration and logs

## 🆘 Troubleshooting

### Common Issues:
- **Chrome not found**: Install Chrome/Chromium
- **Port conflicts**: Change port in main.py
- **Memory issues**: Increase server resources
- **Network timeouts**: Check firewall settings

### Debug Commands:
```bash
# Check if Chrome is installed
google-chrome --version

# Test Selenium locally
python -c "from selenium import webdriver; print('Selenium works')"

# Check port availability
netstat -tulpn | grep 5000
```
