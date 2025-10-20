# 📸 Fiber Installation Bot - WhatsApp Photo Verification System

**Version 2.0** | **Updated: October 8, 2025** | **Production Ready**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-API-25D366)](https://www.whatsapp.com/business/api)

## 🎯 **Overview**

An intelligent WhatsApp bot that guides field agents through fiber installation photo verification using AI-powered quality analysis. Designed for telecommunications companies to ensure installation quality and compliance.

### ✨ **Key Features**

- 📱 **WhatsApp Integration** - Agents use familiar WhatsApp interface
- 🤖 **AI Photo Verification** - OpenAI GPT-4 Vision analyzes photos in real-time
- 📋 **12-Step Process** - Complete installation workflow matching industry standards
- 🏢 **Multi-Installation Support** - Agents can manage up to 10 concurrent installations
- 🎛️ **Admin Controls** - Adjustable AI strictness and comprehensive monitoring
- 🌍 **Field-Agent Friendly** - Simple instructions in plain language
- 📊 **Progress Tracking** - Real-time status and completion monitoring

## 🚀 **Quick Start**

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Twilio Account with WhatsApp Business API
- ngrok (for local development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/VelocityFibre/foto_bot.git
cd foto_bot
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. **Run the bot**
```bash
python app.py
```

5. **Set up ngrok tunnel** (for development)
```bash
ngrok http 5000
# Copy the HTTPS URL to your Twilio webhook
```

## 📋 **Installation Steps**

The bot guides agents through 12 standardized installation steps:

| Step | Name | Description |
|------|------|-------------|
| 1 | House Photo | Wide shot of house with street number visible |
| 2 | Cable from Pole to House | Full cable span from telephone pole to house |
| 3 | Cable Entry Point (Outside) | Close-up of where cable enters house exterior |
| 4 | Cable Entry Point (Inside) | Interior view of cable entry point |
| 5 | Wall for Installation | Wall area where ONT will be installed + power outlet |
| 6 | Back of White Box (After Install) | ONT rear showing green clips and cable management |
| 7 | Power Meter Reading | Power meter screen showing dBm reading (-25 to -10 acceptable) |
| 8 | White Box Barcode | Clear photo of ONT barcode/serial number |
| 9 | Battery Backup Serial | Gizzu UPS device with serial number visible |
| 10 | Final Installation Photo | Complete setup showing all components tidy |
| 11 | Green Lights On | Active ONT with green lights + Fibertime sticker + Drop number |
| 12 | Customer Signature | Photo of signed completion document |

## 💬 **Agent Commands**

### Basic Commands
```
START           - Begin new installation
STATUS          - Check current progress  
LIST            - Show all active installations
HELP            - Display available commands
RESET           - Start over with new installation
```

### Admin Commands
```
SKIP                    - Skip current step (testing)
STRICTNESS              - View AI evaluation settings
STRICTNESS STRICT       - Set to 9/10 (very strict)
STRICTNESS STANDARD     - Set to 8/10 (standard)  
STRICTNESS LENIENT      - Set to 7/10 (more lenient)
STRICTNESS TESTING      - Set to 5/10 (testing mode)
STRICTNESS SET 7.5      - Custom threshold
```

### Multi-Installation
```
DR1234567       - Switch to or create installation with DR number
LIST            - Show all active installations with progress
```

## 🎛️ **Admin Features**

### API Endpoints

- `GET /health` - Health check
- `GET /stats` - Bot statistics
- `GET /admin/strictness` - View AI strictness settings
- `POST /admin/strictness` - Update AI strictness
- `GET /config` - System configuration
- `GET /sessions` - Active sessions (development)

### Strictness Control

Adjust AI evaluation strictness:
- **9/10** - Very Strict (only excellent photos pass)
- **8/10** - Standard (good quality photos pass)
- **7/10** - Lenient (acceptable photos pass)
- **5/10** - Testing (most photos pass)

## 🏗️ **Architecture**

```
WhatsApp ↔ Twilio ↔ Flask Webhook ↔ Bot Engine
                                      ├── Session Manager
                                      ├── AI Verifier (OpenAI)  
                                      ├── Multi-Installation Support
                                      └── Admin Controls
```

### Key Components

- **`FiberInstallationBot`** - Main bot logic and message handling
- **`SessionManager`** - Multi-installation state management
- **`FiberInstallationVerifier`** - AI-powered photo analysis
- **`MessageHandler`** - Photo download and processing

## 🔧 **Configuration**

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Twilio WhatsApp Configuration  
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
WHATSAPP_NUMBER=+14155238886

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Storage Configuration
PHOTO_STORAGE_PATH=./data/photos
SESSION_FILE_PATH=./data/sessions.json

# AI Strictness (configurable at runtime)
PASSING_SCORE_THRESHOLD=8
PASSING_COMPLETION_RATE=0.85
```

## 📱 **WhatsApp Setup**

1. **Twilio Console Setup**
   - Create Twilio account
   - Enable WhatsApp sandbox
   - Configure webhook URL: `https://your-server.com/webhook`

2. **Agent Onboarding**
   - Send `join your-sandbox-code` to Twilio WhatsApp number
   - Test with `START` command

3. **Production Deployment**
   - Apply for WhatsApp Business API approval
   - Configure production webhook
   - Update environment to `production`

## 🧪 **Testing**

### Unit Tests
```bash
python -m pytest tests/ -v
```

### Manual Testing
```bash
# Test photo verification
curl -X POST -F "photo=@test_image.jpg" -F "step=1" \
  http://localhost:5000/test

# Test strictness API
curl http://localhost:5000/admin/strictness
```

### WhatsApp Testing
1. Join Twilio sandbox
2. Send `START` to bot
3. Follow installation workflow
4. Test admin commands

## 📊 **Monitoring**

### Health Checks
```bash
curl http://localhost:5000/health
```

### Statistics
```bash  
curl http://localhost:5000/stats
```

### Logs
- Application logs: `./logs/verification.log`
- Server logs: `bot.log`

## 🚀 **Deployment**

### Production Deployment
1. Set `FLASK_ENV=production`
2. Use production WSGI server (gunicorn)
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure monitoring and alerts

### Docker Deployment
```bash
docker build -t fiber-bot .
docker run -p 5000:5000 --env-file .env fiber-bot
```

## 📈 **Performance**

- **Response Time**: <2 seconds for commands, <30 seconds for photo analysis
- **Concurrent Users**: Supports 100+ simultaneous agents
- **Photo Processing**: Handles up to 1000 photos/hour
- **Storage**: ~50MB per 1000 photos (compressed)

## 🔐 **Security**

- API key encryption
- Rate limiting (10 photos/hour per agent)
- Session timeout (24 hours)
- Input validation and sanitization
- HTTPS required for webhooks

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/VelocityFibre/foto_bot/issues)
- **Documentation**: [Wiki](https://github.com/VelocityFibre/foto_bot/wiki)
- **Email**: support@velocityfibre.com

## 🏆 **Acknowledgments**

- **VelocityFibre Team** - Product requirements and testing
- **Field Agents** - User feedback and real-world testing
- **OpenAI** - AI-powered photo verification capabilities
- **Twilio** - WhatsApp Business API integration

---

**Built with ❤️ for reliable fiber installations | VelocityFibre © 2025**
