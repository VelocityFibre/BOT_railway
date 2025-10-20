# Detailed Implementation Plan - Fiber Photo Verification System

**Project Start:** October 1, 2025
**Timeline:** 4 weeks
**Total Budget:** $50-100 (Phase 1)

## GitHub Spec-Kit Process Integration

**Yes, spec-kit will help structure this project properly:**

✅ **Spec-Kit Benefits for Our Project:**
- **Issue Templates** - For bug reports and feature requests
- **PR Templates** - For code reviews of verification logic
- **Project Boards** - To track 14 installation steps progress
- **Wiki Documentation** - For field agent training materials
- **Branch Protection** - For production deployment safety

**Implementation with Spec-Kit:**
```bash
# Our project will use:
- .github/ISSUE_TEMPLATE/bug_report.md
- .github/ISSUE_TEMPLATE/feature_request.md
- .github/PULL_REQUEST_TEMPLATE.md
- .github/workflows/deploy.yml
- docs/ for field agent guides
- wiki/ for installation procedures
```

## Phase 1: WhatsApp MVP + OpenAI Vision (Week 1)

### Day 1-2: Project Setup & API Integration

**Tasks:**
```bash
# 1. Repository structure
fiber-photo-verification/
├── src/
│   ├── bot.py              # WhatsApp bot logic
│   ├── verifier.py         # OpenAI Vision integration
│   ├── prompts.py          # 14 step verification prompts
│   └── utils.py           # Image processing
├── config/
│   └── settings.py        # API keys & config
├── data/
│   └── sessions.json      # Agent sessions
├── photos/
│   ├── pending/           # New uploads
│   ├── approved/          # Passed photos
│   └── rejected/          # Failed photos
├── requirements.txt
├── .env.example
├── .github/               # Spec-kit templates
└── README.md
```

**API Setup:**
- OpenAI API key
- Twilio WhatsApp sandbox
- ngrok for local testing

### Day 3-4: Core Verification Engine

**OpenAI Vision Prompts (14 Steps):**
```python
# Example prompts structure
STEP_PROMPTS = {
    "step1_frontage": """
    Verify property frontage photo:
    - House/building clearly visible
    - Street number readable
    - Daytime lighting
    - No obstructions

    Return JSON: {passed: bool, score: 0-10, issues: [], confidence: 0-1}
    """,
    # ... 13 more steps
}
```

**Photo Processing Pipeline:**
1. Receive WhatsApp photo
2. Compress/optimize for API
3. Send to OpenAI Vision with step-specific prompt
4. Parse JSON response
5. Generate user-friendly feedback
6. Send WhatsApp response within 30 seconds

### Day 5-7: WhatsApp Bot Logic

**Conversation Flow:**
```
Agent: "START"
Bot: "🔧 New installation: JOB_20251001_001
📷 Step 1: Property Frontage
Send photo with street number visible"

[Agent sends photo]
Bot: "✅ Step 1 PASSED - Great lighting!
📷 Step 2: Wall location (before install)
Send photo of planned installation area"

[Agent sends blurry photo]
Bot: "❌ Step 2 NEEDS RETAKE
Issues:
- Photo too blurry
- Wall area not clearly visible
📸 Please retake with steady hands"
```

## Phase 2: Testing & Refinement (Week 2)

### Day 8-10: Field Testing with Sample Photos

**Test Scenarios:**
- 5 complete installations (70 photos total)
- Test edge cases (blurry, dark, wrong angles)
- Measure response times
- Verify accuracy of feedback

**Success Criteria:**
- 90%+ verification accuracy
- <30 second response time
- Clear, actionable feedback messages

### Day 11-14: Refinement & Bug Fixes

**Common Issues to Address:**
- Handling large photo files
- Processing low-quality images
- Managing conversation state
- Error recovery (API failures)

## Phase 3: Supervisor Dashboard (Week 3)

### Simple Web Dashboard (Streamlit)

**Features:**
```python
# Dashboard Overview:
- Active installations in progress
- Completion rates per agent
- Common failure reasons
- Photo quality trends
- Export reports (CSV/PDF)
```

**Dashboard Pages:**
1. **Live Overview** - Real-time installation status
2. **Agent Performance** - Individual agent metrics
3. **Quality Reports** - Photo quality trends
4. **Installation History** - Completed jobs archive

### Data Storage

**Simple File-based Storage (Phase 1):**
```json
{
  "sessions": {
    "agent_001": {
      "current_job": "JOB_20251001_001",
      "current_step": 3,
      "completed_steps": {"step1": "photo_path.jpg"},
      "start_time": "2025-10-01T09:00:00"
    }
  },
  "jobs": {
    "JOB_20251001_001": {
      "agent_id": "agent_001",
      "status": "in_progress",
      "photos": {...},
      "verifications": {...}
    }
  }
}
```

## Phase 4: Production Deployment (Week 4)

### Deployment Architecture

**Components:**
- **WhatsApp Bot** - Python Flask app on Heroku/Railway
- **OpenAI Integration** - API calls
- **Dashboard** - Streamlit on separate endpoint
- **Storage** - AWS S3 for photos, JSON for sessions

**Environment Setup:**
```bash
# Production requirements
- Python 3.9+
- Redis for session management
- S3 for photo storage
- PostgreSQL (future, for analytics)
```

### Security & Reliability

**Security Measures:**
- API key encryption
- Phone number verification
- Session timeout (24 hours)
- Rate limiting (10 photos/hour)

**Reliability Features:**
- Retry logic for API failures
- Backup storage for photos
- Error logging and monitoring
- Health checks

## Implementation Checklist

### Week 1: MVP Development
- [ ] Set up project repository with spec-kit
- [ ] Configure OpenAI API
- [ ] Set up Twilio WhatsApp sandbox
- [ ] Implement 14 verification prompts
- [ ] Build photo processing pipeline
- [ ] Create WhatsApp conversation flow
- [ ] Test with sample photos

### Week 2: Testing
- [ ] Field testing with 5 installations
- [ ] Measure accuracy and response times
- [ ] Refine prompts based on results
- [ ] Fix bugs and edge cases
- [ ] Document common issues

### Week 3: Dashboard
- [ ] Build Streamlit dashboard
- [ ] Implement data storage
- [ ] Create agent performance metrics
- [ ] Add export functionality
- [ ] User testing with supervisors

### Week 4: Production
- [ ] Deploy to production hosting
- [ ] Set up monitoring and logging
- [ ] Create training materials
- [ ] Train field agents
- [ ] Go-live and support

## Risk Mitigation

**Technical Risks:**
- **API Failure:** Implement retry logic + fallback responses
- **Poor Connectivity:** WhatsApp queueing handles offline scenarios
- **Photo Quality:** Provide specific guidance for retakes

**Operational Risks:**
- **User Adoption:** Zero training approach with familiar WhatsApp
- **Photo Volume:** Start with 5 agents, scale gradually
- **Cost Control:** Monitor API usage, set monthly limits

## Success Metrics

**Week 1 Targets:**
- Bot responds to all photo submissions
- 30-second average response time
- 85%+ verification accuracy

**Week 2 Targets:**
- 5 successful test installations
- 90%+ agent satisfaction
- 70% reduction in photo retakes

**Week 4 Targets:**
- Full production deployment
- 95%+ agent adoption
- 50% reduction in installation time

---

**Ready to begin implementation - October 1, 2025**