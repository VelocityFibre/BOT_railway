# 🔧 Installation Guide - Fiber Installation Bot

**Updated: October 8, 2025**

This guide will help you set up the Fiber Installation Bot on your server with WhatsApp integration.

## 📋 Prerequisites

Before starting, ensure you have:

- **Server/Computer** running Linux/macOS/Windows
- **Python 3.8+** installed
- **OpenAI API Key** (GPT-4 Vision access)
- **Twilio Account** with WhatsApp Business API
- **Domain/ngrok** for webhook URLs
- **Git** for cloning the repository

## 🚀 Step-by-Step Installation

### 1. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/VelocityFibre/foto_bot.git
cd foto_bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here
WHATSAPP_NUMBER=+14155238886

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secure-random-secret-key-here

# Storage Paths
PHOTO_STORAGE_PATH=./data/photos
SESSION_FILE_PATH=./data/sessions.json

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/verification.log

# Bot Configuration
MAX_PHOTOS_PER_HOUR=10
MAX_SESSION_DURATION_HOURS=24
PASSING_SCORE_THRESHOLD=8
PASSING_COMPLETION_RATE=0.85
```

### 3. Create Required Directories

```bash
# Create data and logs directories
mkdir -p data/photos
mkdir -p logs
```

### 4. Test the Installation

```bash
# Test basic functionality
python -c "from src.bot.bot import FiberInstallationBot; print('✅ Bot imports successfully')"

# Test OpenAI connection
python -c "
import os
from src.verifier import FiberInstallationVerifier
print('✅ OpenAI connection test:', bool(os.getenv('OPENAI_API_KEY')))
"
```

### 5. Start the Bot Server

```bash
# Run the bot
python app.py
```

You should see output like:
```
INFO - Starting Fiber Photo Verification Bot in development mode
* Serving Flask app 'src.api.app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

### 6. Set Up Public Webhook (Development)

#### Option A: Using ngrok (Recommended for development)

```bash
# Install ngrok (if not already installed)
# Visit: https://ngrok.com/download

# In a separate terminal, create tunnel
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

#### Option B: Using a VPS/Cloud Server

If you're running on a server:
```bash
# Make sure port 5000 is open
sudo ufw allow 5000

# Your webhook URL will be: https://your-domain.com:5000/webhook
```

### 7. Configure Twilio WhatsApp

1. **Login to Twilio Console**: https://console.twilio.com/
2. **Navigate to WhatsApp Sandbox**: Messaging > Try it out > Send a WhatsApp message
3. **Configure Webhook**:
   - **When a message comes in**: `https://your-ngrok-url.ngrok.io/webhook`
   - **HTTP Method**: `POST`

### 8. Test WhatsApp Integration

1. **Join the Sandbox**:
   - Send your sandbox code (e.g., "join abc-def") to the Twilio WhatsApp number
   
2. **Test Basic Commands**:
   ```
   START           # Should respond with welcome message
   HELP            # Should show available commands
   STATUS          # Should show current status
   ```

3. **Test Installation Flow**:
   ```
   START           # Begin installation
   DR1234567       # Set DR number
   SKIP            # Skip location (for testing)
   [Upload photo]  # Test photo verification
   LIST            # Show active installations
   ```

## 🎛️ Admin Configuration

### Test Admin Commands

```bash
# Test strictness API
curl http://localhost:5000/admin/strictness

# Test health check
curl http://localhost:5000/health

# Test statistics
curl http://localhost:5000/stats
```

### Configure AI Strictness

Via WhatsApp:
```
STRICTNESS              # View current settings
STRICTNESS LENIENT      # Set to 7/10 for testing
STRICTNESS STANDARD     # Set to 8/10 for production
```

Via API:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"passing_score_threshold": 7.5}' \
  http://localhost:5000/admin/strictness
```

## 🏭 Production Deployment

### 1. Update Environment

```bash
# Set production environment
FLASK_ENV=production
```

### 2. Use Production WSGI Server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. Set Up Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Configure SSL Certificate

```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### 5. Set Up Process Manager

```bash
# Create systemd service
sudo nano /etc/systemd/system/foto-bot.service
```

```ini
[Unit]
Description=Fiber Installation Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/foto_bot
Environment=PATH=/path/to/foto_bot/venv/bin
ExecStart=/path/to/foto_bot/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable foto-bot
sudo systemctl start foto-bot
sudo systemctl status foto-bot
```

## 🔍 Troubleshooting

### Common Issues

**1. Bot doesn't respond to WhatsApp messages**
- Check ngrok tunnel is active
- Verify webhook URL in Twilio console
- Check bot server logs: `tail -f bot.log`

**2. Photo verification fails**
- Verify OpenAI API key is correct
- Check API usage limits
- Test with: `curl -X POST -F "photo=@test.jpg" http://localhost:5000/test`

**3. Session/data issues**
- Check `data/sessions.json` file permissions
- Verify `data` directory is writable
- Clear sessions: `rm data/sessions.json` and restart

**4. Import errors**
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Logs and Monitoring

```bash
# Application logs
tail -f logs/verification.log

# Server logs  
tail -f bot.log

# Check system resources
htop

# Test endpoints
curl http://localhost:5000/health
```

### Performance Optimization

```bash
# Monitor photo storage
du -sh data/photos/

# Check memory usage
ps aux | grep python

# Database sessions count
python -c "
from src.storage.sessions import SessionManager
sm = SessionManager()
print(f'Active sessions: {len(sm.get_active_sessions())}')
"
```

## 📞 Support

If you encounter issues:

1. **Check logs** first: `tail -f bot.log`
2. **Test components** individually using the troubleshooting steps
3. **Review configuration** - ensure all environment variables are set
4. **Check network connectivity** - ensure webhook URL is accessible

For additional help:
- **GitHub Issues**: https://github.com/VelocityFibre/foto_bot/issues
- **Documentation**: Check README.md and wiki
- **Email Support**: support@velocityfibre.com

## 🎯 Next Steps

Once installation is complete:

1. **Train field agents** on WhatsApp commands
2. **Set up monitoring** and alerting
3. **Configure backup** procedures for data/sessions
4. **Plan production deployment** with proper SSL and domain
5. **Apply for WhatsApp Business API** approval (for production)

---

**Installation complete! Your Fiber Installation Bot is ready for use.** 🎉