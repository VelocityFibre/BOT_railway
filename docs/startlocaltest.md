# Start Local Testing Guide

Quick reference for setting up and running the Fiber Photo Verification Bot for local testing with WhatsApp integration.

## Prerequisites

- Python 3.x installed
- Virtual environment set up
- Twilio WhatsApp credentials configured in `.env`
- ngrok for webhook tunneling

## Quick Start Commands

### 1. Create Virtual Environment (One-time setup)
```bash
cd /home/louisdup
python3 -m venv fotos_check_venv
```

### 2. Install Dependencies (One-time setup)
```bash
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601
source /home/louisdup/fotos_check_venv/bin/activate
pip install -r requirements.txt
pip install pyngrok
```

### 3. Create Required Directories (One-time setup)
```bash
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601
mkdir -p data logs data/photos
```

## Starting the Bot for Testing

### Method 1: Interactive Testing (Recommended for development)

#### Terminal 1 - Start Flask App
```bash
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601
source /home/louisdup/fotos_check_venv/bin/activate
export FLASK_ENV=development
python app.py
```
*Keep this terminal open. The bot will run on http://localhost:5000*

#### Terminal 2 - Start Ngrok Tunnel
```bash
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601
source /home/louisdup/fotos_check_venv/bin/activate
python setup_ngrok.py
```
*This will display your public webhook URL. Copy the webhook URL for Twilio configuration.*

### Method 2: Background Mode (For longer testing sessions)

#### Start Flask App in Background
```bash
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601
source /home/louisdup/fotos_check_venv/bin/activate
export FLASK_ENV=development
nohup python app.py > flask_app.log 2>&1 & 
echo "Flask app started with PID: $!"
```

#### Start Ngrok in Background
```bash
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601
source /home/louisdup/fotos_check_venv/bin/activate
nohup python setup_ngrok.py > ngrok.log 2>&1 &
echo "Ngrok started with PID: $!"
```

#### Get the Webhook URL
```bash
grep "Webhook URL:" ngrok.log | tail -1
```

## Twilio WhatsApp Configuration

1. **Login to Twilio Console**: https://console.twilio.com/
2. **Go to WhatsApp Sandbox**: Develop → Messaging → Try it out → Send a WhatsApp message
3. **Update Webhook URL**: 
   - Copy the webhook URL from ngrok output (e.g., `https://abc123.ngrok-free.dev/webhook`)
   - Paste it in the "When a message comes in" field
4. **Save Configuration**

## Current Environment Variables

Your `.env` file should contain:
```
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
WHATSAPP_NUMBER=your-whatsapp-number
FLASK_ENV=development
```

## Testing Steps

1. **Start the bot** using one of the methods above
2. **Configure Twilio webhook** with the ngrok URL
3. **Join WhatsApp Sandbox**:
   - Send the sandbox join code to +1 415 523 8886
   - Follow the instructions provided by Twilio
4. **Send test photos** to the WhatsApp number
5. **Monitor logs**:
   - Flask logs: `tail -f flask_app.log` (if running in background)
   - Ngrok logs: `tail -f ngrok.log` (if running in background)

## Useful Commands

### Check if Services are Running
```bash
# Check Flask app
curl -s http://localhost:5000 > /dev/null && echo "✅ Flask running" || echo "❌ Flask not running"

# Check processes
ps aux | grep -E "(python app.py|ngrok)" | grep -v grep
```

### Stop Services
```bash
# Kill Flask app
pkill -f "python app.py"

# Kill ngrok
pkill -f "ngrok\|setup_ngrok"
```

### View Logs
```bash
# Flask application logs
tail -f flask_app.log

# Ngrok connection logs  
tail -f ngrok.log

# Application logs directory
tail -f logs/verification.log
```

## Troubleshooting

### Common Issues

1. **Virtual environment not found**
   ```bash
   cd /home/louisdup
   python3 -m venv fotos_check_venv
   ```

2. **Dependencies missing**
   ```bash
   source /home/louisdup/fotos_check_venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Port 5000 already in use**
   ```bash
   lsof -ti:5000 | xargs kill -9
   ```

4. **Ngrok authentication issues**
   - Sign up at https://ngrok.com
   - Get your auth token
   - Run: `ngrok authtoken YOUR_TOKEN`

5. **Twilio webhook not receiving messages**
   - Verify webhook URL is accessible: `curl https://your-ngrok-url.ngrok-free.dev/webhook`
   - Check Twilio console for webhook errors
   - Ensure ngrok tunnel is still active

### File Locations

- **Project Directory**: `/media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601`
- **Virtual Environment**: `/home/louisdup/fotos_check_venv`
- **Configuration**: `.env` file in project directory
- **Logs**: `logs/` directory in project directory
- **Data**: `data/` directory for sessions and photos

## Quick Status Check

Run this script to check the status of all components:

```bash
#!/bin/bash
echo "=== Bot Status Check ==="
cd /media/louisdup/FIBREFLOW1/fotos_check_backup_20251006_124601

echo "1. Virtual Environment:"
[ -d "/home/louisdup/fotos_check_venv" ] && echo "✅ Virtual environment exists" || echo "❌ Virtual environment missing"

echo "2. Flask App:"
curl -s http://localhost:5000 > /dev/null && echo "✅ Flask app running on port 5000" || echo "❌ Flask app not running"

echo "3. Required directories:"
[ -d "data" ] && echo "✅ data directory exists" || echo "❌ data directory missing"
[ -d "logs" ] && echo "✅ logs directory exists" || echo "❌ logs directory missing"

echo "4. Environment file:"
[ -f ".env" ] && echo "✅ .env file exists" || echo "❌ .env file missing"

echo "5. Running processes:"
ps aux | grep -E "(python app.py)" | grep -v grep | wc -l | xargs echo "Flask processes:"
ps aux | grep -E "(ngrok|setup_ngrok)" | grep -v grep | wc -l | xargs echo "Ngrok processes:"
```

---

**Last Updated**: October 9, 2025
**Author**: Setup automation for Fiber Photo Verification Bot