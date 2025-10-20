# Quick Start Guide - Fiber Photo Verification System

Get your WhatsApp bot running in 5 minutes!

## Prerequisites
- Python 3.9+
- OpenAI API key
- Twilio account with WhatsApp Business API

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Configure API Keys
Edit `.env` file with your credentials:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
WHATSAPP_NUMBER=+14155238886
```

## Step 3: Start the Bot
```bash
python app.py
```

## Step 4: Test with WhatsApp
1. Send a WhatsApp message to your Twilio number
2. Type "START" to begin installation
3. Send a test photo
4. Receive AI feedback within 30 seconds

## Step 5: Monitor Dashboard
Open new terminal and run:
```bash
streamlit run dashboard.py
```
Visit http://localhost:8501 to see the supervisor dashboard.

## Troubleshooting

**Bot not responding?**
- Check your .env file has correct API keys
- Verify ngrok is running (for local testing)
- Check logs at `./logs/verification.log`

**Photo analysis not working?**
- Verify OpenAI API key has GPT-4 Vision access
- Check photo size < 10MB
- Ensure image format is JPG/JPEG

**WhatsApp not connecting?**
- Verify Twilio webhook URL is correct
- Check phone number format includes country code
- Ensure WhatsApp Business API is active

## Need Help?
- Check `README.md` for detailed documentation
- Review `IMPLEMENTATION_PLAN.md` for technical details
- Check logs in `./logs/` directory

You're all set! Your field agents can now submit photos via WhatsApp and receive immediate AI feedback. 🚀