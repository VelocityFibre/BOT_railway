### Project Overview

This project is a Python-based WhatsApp bot that uses the OpenAI Vision API to verify photos of fiber optic installations. The bot guides field agents through a 12-step process, analyzing the photos they submit to ensure they meet quality standards. The bot is built with Flask, and it uses Twilio for WhatsApp integration.

### Building and Running

**1. Prerequisites:**
- Python 3.8+
- OpenAI API Key
- Twilio Account with WhatsApp Business API
- ngrok (for local development)

**2. Installation:**
```bash
git clone https://github.com/VelocityFibre/foto_bot.git
cd foto_bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configuration:**
- Copy `.env.example` to `.env` and fill in your API keys and other settings.
```bash
cp .env.example .env
```

**4. Running the bot:**
```bash
python app.py
```

**5. Local Development:**
- Use ngrok to expose your local server to the internet.
```bash
ngrok http 5000
```
- Copy the HTTPS URL from ngrok and use it as the webhook URL in your Twilio sandbox.

### Testing

**Unit Tests:**
```bash
python -m pytest tests/ -v
```

**Manual Testing:**
- You can test the photo verification endpoint directly:
```bash
curl -X POST -F "photo=@test_image.jpg" -F "step=1" http://localhost:5000/test
```
- You can also test the bot by sending messages to it on WhatsApp.

### Development Conventions

- The project uses `black` for code formatting and `flake8` for linting.
- The code is structured into several modules: `api`, `bot`, `storage`, and `verifier`.
- The `api` module handles the web-facing parts of the application (Flask routes).
- The `bot` module contains the core bot logic.
- The `storage` module handles session management.
- The `verifier` module handles the AI-powered photo verification.
- Configuration is handled through environment variables, loaded by the `src/config.py` file.
- The bot uses a `SessionManager` to keep track of the state of each user's installation process.
- The `FiberInstallationVerifier` class in `src/verifier.py` is responsible for calling the OpenAI Vision API and parsing the results.
- The bot has a number of admin commands that can be used to control its behavior, such as changing the AI strictness level.
