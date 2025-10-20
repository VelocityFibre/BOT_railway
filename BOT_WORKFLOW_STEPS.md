# Bot Workflow Steps Configuration

## Overview
This document outlines the complete step-by-step workflow that the Fiber Installation Photo Verification Bot follows when processing field agent installations via WhatsApp.

## Bot Architecture
The bot consists of several key components:
- **`FiberInstallationBot`** - Main bot controller (`src/bot/bot.py`)
- **`MessageHandler`** - Handles WhatsApp media downloads (`src/bot/handlers.py`) 
- **`SessionManager`** - Manages installation sessions (`src/storage/sessions.py`)
- **`FiberInstallationVerifier`** - AI photo verification (`src/verifier.py`)

## Complete Bot Workflow

### 1. **Session Initiation**
```
User sends: "START", "NEW", "HI", "HELLO", "HEY", "HOLA"
Bot responds: Welcome message + Step 1 instructions
Creates new session with unique Job ID
```

**Bot Actions:**
- Normalize phone number
- Create/retrieve session via `SessionManager`
- Generate Job ID and agent ID
- Initialize step counter (starts at Step 1)
- Send welcome message with first step requirements

### 2. **Step-by-Step Photo Processing Loop**
For each of the 12 installation steps, the bot follows this workflow:

#### 2.1 **Photo Reception**
```
User sends: Photo via WhatsApp
Bot receives: media_url, media_id from Twilio
```

#### 2.2 **Photo Download & Processing**
```python
# MessageHandler.download_photo()
1. Download photo from Twilio media URL
2. Process & optimize image (resize, compress)
3. Save to pending/ directory with naming: {job_id}_{media_id}_{timestamp}.jpg
4. Return local file path
```

#### 2.3 **AI Verification**
```python
# FiberInstallationVerifier.verify_step()
1. Load step-specific requirements from prompts.py
2. Send photo + requirements to OpenAI Vision API
3. Parse AI response for pass/fail + issues + score
4. Return VerificationResult object
```

#### 2.4 **Response Generation**
```python
# Bot._format_verification_response()
If PASSED:
  ✅ Success message with score feedback
  📊 Progress update (X/12 steps completed)
  📷 Next step instructions
  
If FAILED:
  ❌ Failure message with specific issues
  📸 Recommendation for retaking
  🔄 Request to resend photo
```

#### 2.5 **Session Update**
```python
If photo passed:
  - Mark step as completed in session
  - Move photo to approved/ directory
  - Increment current_step counter
  - Update session progress

If photo failed:
  - Keep current step unchanged
  - Move photo to rejected/ directory
  - Maintain retry capability
```

### 3. **Command Handling**
The bot responds to these text commands at any time:

#### 3.1 **STATUS Command**
```
User sends: "STATUS"
Bot responds: Current progress report
```
- Shows Job ID and completion percentage
- Lists completed steps
- Shows current step requirements
- Handles completed installations

#### 3.2 **HELP Command**
```
User sends: "HELP" 
Bot responds: Full help message
```
- Lists all available commands
- Explains usage workflow
- Provides photography tips
- Contact information

#### 3.3 **RESET Command**
```
User sends: "RESET"
Bot responds: Starts new installation
```
- Clears current session
- Calls `_handle_start_command()`
- Begins fresh installation

### 4. **Installation Steps Configuration**

The bot processes these 12 specific installation steps:

| Step | Name | Requirement |
|------|------|-------------|
| 1 | Property Frontage | House, street number visible |
| 2 | Location on Wall (Before Install) | Installation area photo |
| 3 | Outside Cable Span (Pole → Pigtail screw) | Cable routing |
| 4 | Home Entry Point - Outside | External entry point |
| 5 | Home Entry Point - Inside | Internal entry point |
| 6 | Fibre Entry to ONT | ONT connection |
| 7 | Powermeter at ONT (Before Activation) | Pre-activation readings |
| 8 | ONT Barcode | Equipment verification - barcode/serial |
| 9 | Mini-UPS Serial Number | Backup power unit (Gizzu) |
| 10 | Overall Work Area After Completion | Clean workspace |
| 11 | Active Broadband Light | Service activation confirmation |
| 12 | Customer Signature | Customer acceptance |

### 5. **Completion Workflow**
```
When step 12 is completed:
1. Session status → "completed"
2. Final success message sent
3. Installation marked ready for activation
4. User can start new installation with "NEW"
```

### 6. **Error Handling**
The bot includes comprehensive error handling:

- **Download errors**: Retry download, fallback message
- **AI API errors**: Generic error response, logging
- **File processing errors**: Image optimization fallbacks
- **Session errors**: Auto-recovery, graceful degradation
- **Unknown commands**: Helpful guidance message

### 7. **Configuration Files**

#### 7.1 **Environment Variables** (`.env`)
```bash
# Required API Keys
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
WHATSAPP_NUMBER=your-whatsapp-number

# Optional Settings
FLASK_ENV=development
PORT=5000
```

#### 7.2 **Photo Processing Config** (`src/config.py`)
```python
MAX_PHOTO_SIZE_MB = 10        # Maximum file size
MAX_PHOTO_DIMENSION = 2048    # Maximum width/height
COMPRESSION_QUALITY = 85      # JPEG quality
PHOTO_STORAGE_PATH = "photos" # Storage directory
```

#### 7.3 **Step Requirements** (`src/prompts.py`)
```python
STEP_NAMES = {
    1: "Property Frontage",
    2: "Location on Wall (Before Install)",
    # ... all 12 steps
}

STEP_REQUIREMENTS = {
    1: "Clear photo showing house/building with street number visible",
    2: "Photo of installation area before work begins",
    # ... detailed requirements for each step
}
```

### 8. **File Structure**
```
photos/
├── pending/     # Newly uploaded photos awaiting verification
├── approved/    # Photos that passed AI verification  
└── rejected/    # Photos that failed verification

logs/           # Bot operation logs
data/           # Session and job data
config/         # Additional configuration files
```

### 9. **API Integration**
- **Twilio WhatsApp API**: Message/media handling
- **OpenAI Vision API**: Photo verification
- **Flask API**: Web dashboard and webhook endpoints

### 10. **Monitoring & Stats**
The bot tracks:
- Total installations processed  
- Success/failure rates per step
- Average completion times
- Active vs completed sessions
- Photo quality metrics

## Running the Bot

### Quick Start:
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Start bot
python app.py

# 4. Start dashboard (optional)
python dashboard.py
```

### Webhook Setup:
The bot expects Twilio webhook calls at:
- `POST /webhook/whatsapp` - Incoming messages
- `GET /webhook/status` - Health check

This workflow ensures reliable, step-by-step verification of fiber installation photos with AI assistance and comprehensive session management.