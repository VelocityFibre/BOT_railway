# WhatsApp Fiber Installation Bot - Complete Message Flow

## 🔄 **Complete Message Flow Diagram**

```
📱 Field Agent WhatsApp
      ↓ (sends photo + message)
      ↓
🌐 Twilio WhatsApp API
      ↓ (webhook POST /webhook)
      ↓
🖥️  Your Flask Server (routes.py)
      ↓ (extracts from_number, media_url)
      ↓
🤖 FiberInstallationBot.process_message()
      ↓
   ┌─ Text Message? ─────────────┐
   │  ├─ "START" → New session   │
   │  ├─ "STATUS" → Progress     │
   │  ├─ "HELP" → Instructions   │
   │  └─ Unknown → Help message  │
   └─────────────────────────────┘
      │
   ┌─ Photo Message? ────────────────────────┐
   │  ↓                                      │
   │  📥 MessageHandler.download_photo()     │
   │       ↓ (downloads from Twilio)         │
   │       ↓                                 │
   │  🧠 FiberInstallationVerifier          │
   │       ↓ (encodes image to base64)       │
   │       ↓                                 │
   │  🤖 OpenAI GPT-4o-mini Vision API      │
   │       ↓ (analyzes photo with prompts)   │
   │       ↓                                 │
   │  📊 VerificationResult                  │
   │       ↓ (pass/fail + score + issues)    │
   │       ↓                                 │
   │  💾 SessionManager.complete_step()      │
   │       ↓ (if passed)                     │
   │       └─────────────────────────────────┘
      ↓
🗨️  Response Message Generated
      ↓ (formatted WhatsApp message)
      ↓
🌐 Twilio WhatsApp API
      ↓ (sends response)
      ↓
📱 Field Agent WhatsApp
```

## 🏗️ **Key Components Breakdown**

### 1. **Entry Point**: `src/api/routes.py`
- **Webhook**: Receives POST from Twilio
- **Data Extraction**: Gets phone number, message, media URL
- **Response**: Returns TwiML XML for Twilio

### 2. **Bot Logic**: `src/bot/bot.py`
- **Message Router**: Decides photo vs text handling
- **Session Management**: Tracks installation progress
- **Response Generator**: Creates user-friendly messages

### 3. **AI Engine**: `src/verifier.py`
- **Image Processing**: Resize/compress for API
- **OpenAI Vision**: Send photo + prompt to GPT-4o-mini
- **Result Parsing**: Extract pass/fail, score, issues

### 4. **Data Storage**: `src/storage/sessions.py`
- **Session Persistence**: JSON file storage
- **Progress Tracking**: Current step, completed steps
- **Statistics**: Installation metrics

### 5. **Configuration**: `src/config.py`
- **API Keys**: OpenAI, Twilio credentials
- **Photo Settings**: Max size, compression
- **Thresholds**: Passing scores, timeouts

## 🎯 **When AI Gets Involved**

The AI model is **ONLY** triggered when:

1. ✅ User sends a **photo** (not text)
2. ✅ Session is **active** (current_step ≤ 12)
3. ✅ Photo **downloads successfully**
4. ✅ **Then** → AI analyzes the photo

**AI does NOT get involved for:**
- ❌ Text commands (START, STATUS, HELP)
- ❌ Unknown messages
- ❌ Completed installations
- ❌ Download failures

## 🔍 **Example AI Analysis Process**

### Step 4: Outside Entry Point Photo

**1. User sends photo →**
**2. Bot downloads photo →**
**3. Prompt sent to OpenAI:**

```
You are a fiber installation quality expert. 
Analyze this outside home entry point photo for Step 4.

Verification criteria:
- Cable entry point clearly visible on exterior wall
- Weather-proofing measures properly installed
- Wall penetration protected and sealed
- Cable strain relief properly implemented
- Professional exterior installation

Respond in JSON format only: {
    "passed": true/false,
    "score": 0-10,
    "issues": ["list of problems"],
    "confidence": 0.00-1.00,
    "recommendation": "advice"
}
```

**4. AI analyzes photo and returns:**

```json
{
    "passed": true,
    "score": 8,
    "issues": [],
    "confidence": 0.95,
    "recommendation": "Excellent weatherproofing and clean installation"
}
```

**5. Bot converts to WhatsApp message:**

```
✅ Step 4: Home Entry Point - Outside - PASSED

✨ Good job! Photo meets quality standards.

📊 Progress: 4/12 steps completed (33%)

📷 Next Step: Home Entry Point - Inside
Show the cable entry point from inside the house
```

## 💾 **File Structure During Operation**

```
photos/
├── pending/           # Photos being processed
│   └── JOB_20251008_093930_27123456789_media123_1733654890.jpg
├── approved/          # Passed photos
│   └── JOB_20251008_step4_PASS_media123_1733654890.jpg
└── rejected/          # Failed photos
    └── JOB_20251008_step3_FAIL_media122_1733654870.jpg

data/
└── sessions.json      # Active installation sessions

logs/
└── verification.log   # Bot operation logs
```

## 📊 **Cost & Performance**

**Per Photo Analysis:**
- **API Cost**: ~$0.01-0.03 per photo (OpenAI Vision)
- **Processing Time**: 2-5 seconds
- **Accuracy**: ~85-95% (depending on photo quality)

**Per Complete Installation:**
- **API Cost**: ~$0.12-0.36 (12 photos)
- **Total Time**: 3-8 minutes (including agent response time)
- **Success Rate**: ~80-90% first-pass completion

This architecture allows the bot to handle hundreds of concurrent installations while providing consistent AI-powered quality control! 🚀