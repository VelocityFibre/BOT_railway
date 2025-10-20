# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Fiber Installation Photo Verification System** - An AI-powered WhatsApp bot that verifies fiber optic installation photos in real-time. Field agents submit photos via WhatsApp and receive instant AI feedback for 14 required installation steps.

## Key Architecture

### Core Components
- **Flask API** (`src/api/`): REST endpoints and WhatsApp webhook handling via Twilio
- **Bot Engine** (`src/bot/bot.py`): WhatsApp message processing and conversation flow
- **AI Verifier** (`src/verifier.py`): OpenAI Vision API integration with step-specific prompts
- **Session Manager** (`src/storage/sessions.py`): Agent session tracking and job management
- **Streamlit Dashboard** (`dashboard.py`): Real-time supervisor monitoring interface

### Data Flow
1. Agent sends photo via WhatsApp → Twilio webhook → Flask API
2. Bot downloads/processes image → AI verifier analyzes against step requirements
3. Response generated → Bot sends feedback via WhatsApp → Session updated

### Installation Steps (1-14)
The system verifies specific requirements for each installation step:
- Steps 1-8: Physical installation (frontage, cable routing, entry points, work area)
- Steps 9-12: Equipment verification (ONT barcode, UPS, power readings)  
- Steps 13-14: Service activation (broadband light, customer signature)

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WHATSAPP_NUMBER
```

### Running the Application
```bash
# Start the main WhatsApp bot
python app.py

# Start the supervisor dashboard
streamlit run dashboard.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_verifier.py

# Run with coverage
pytest --cov=src

# Test specific functionality
python test_verifier_simple.py
python test_webhook.py
```

### Development Tools
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# API health check
curl http://localhost:5000/health

# Check bot statistics
curl http://localhost:5000/stats

# Test photo verification (development only)
curl -X POST -F "photo=@test.jpg" -F "step=1" http://localhost:5000/test
```

## Configuration Architecture

### Environment Variables (.env)
- `OPENAI_API_KEY`: GPT-4 Vision API access
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`: WhatsApp Business API
- `WHATSAPP_NUMBER`: Twilio WhatsApp phone number
- `FLASK_ENV`: development/production mode

### Key Configuration (`src/config.py`)
- Photo processing limits (10MB, 1024px max dimension, 85% JPEG quality)
- Session timeouts (24 hours max duration)
- Verification thresholds (8/10 score, 85% completion rate)
- Storage paths for photos (pending/approved/rejected)

## AI Integration Details

### OpenAI Vision API
- Model: `gpt-4o-mini` for cost efficiency
- Each step has specific verification prompts in `src/prompts.py`
- Responses expected in JSON format with: passed, score, issues, confidence, recommendation
- Fallback text parsing if JSON fails

### Photo Processing Pipeline
1. Download from Twilio → Resize if needed → Compress → Base64 encode → Send to OpenAI
2. Response parsing → Generate user-friendly WhatsApp message → Update session
3. Move photo to appropriate storage directory (approved/rejected)

## Session Management

### Session Lifecycle
- Agent sends "START" → New session created with unique Job ID
- Each step tracked in `completed_steps` dictionary
- Session persisted to `./data/sessions.json`
- Auto-cleanup after 24 hours of inactivity

### Job ID Format
`JOB_{YYYYMMDD_HHMMSS}_{agent_id}`

## WhatsApp Bot Commands

### User Commands
- `START`/`NEW`: Begin new installation
- `STATUS`: Check current progress  
- `HELP`: Show command help
- `RESET`: Start over with new job

### Bot Responses
- ✅/❌ Step verification results with specific feedback
- 📊 Progress tracking (X/14 steps completed)
- 📷 Next step instructions with requirements
- 🎉 Completion notifications

## File Structure Insights

### Photo Storage (`./data/photos/`)
- `pending/`: New submissions awaiting verification
- `approved/`: Verified photos (filename format: `{job_id}_step{N}_PASS_{timestamp}.jpg`)
- `rejected/`: Failed photos (filename format: `{job_id}_step{N}_FAIL_{timestamp}.jpg`)

### Critical Files
- `src/prompts.py`: Step-specific AI verification prompts (modify carefully - affects accuracy)
- `src/verifier.py`: Core AI verification logic
- `src/bot/bot.py`: WhatsApp conversation flow
- `dashboard.py`: Supervisor monitoring interface

## Production Considerations

### Webhook Setup
- Twilio webhook URL must point to `/webhook` endpoint
- Use ngrok for local testing: `ngrok http 5000`
- Production requires HTTPS endpoint

### Monitoring
- Logs: `./logs/verification.log` 
- Dashboard: http://localhost:8501 (supervisor interface)
- API stats: http://localhost:5000/stats

### Scaling
- Current setup handles ~10 photos/hour per agent
- Cost: ~$0.25 per complete installation (14 steps)
- 80-90% verification accuracy with OpenAI Vision

## Troubleshooting

### Common Issues
- **Bot not responding**: Check .env API keys, verify Twilio webhook URL
- **Photo analysis failing**: Ensure OpenAI API has GPT-4 Vision access
- **WhatsApp connection issues**: Verify Twilio WhatsApp Business API is active

### Debug Endpoints (Development Only)
- `/config`: View configuration status
- `/sessions`: Active sessions overview
- `/test`: Direct photo verification testing

## Quick Start Reference

See `QUICK_START.md` for 5-minute setup guide.
See `README.md` for complete installation steps and requirements.