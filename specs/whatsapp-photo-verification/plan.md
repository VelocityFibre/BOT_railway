---
description: "Implementation plan for WhatsApp photo verification bot"
scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

# Implementation Plan: WhatsApp Photo Verification

**Branch**: `001-whatsapp-photo-verification` | **Date**: 2025-10-01 | **Spec**: [link](../whatsapp-photo-verification.md)
**Input**: Feature specification from `/specs/whatsapp-photo-verification.md`

## Summary
Field agents submit photos of fiber installation steps via WhatsApp and receive immediate AI-powered quality feedback to ensure compliance and reduce rework.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: OpenAI Vision API, Twilio WhatsApp Business API, Flask
**Storage**: Local file system with JSON for sessions, structured photo storage
**Testing**: pytest with 90%+ coverage requirement
**Target Platform**: Linux server (cloud deployment)
**Performance Goals**: <30 second photo analysis response time
**Constraints**: WhatsApp rate limits, OpenAI API rate limits, poor connectivity handling
**Scale/Scope**: 50 concurrent agents, 1000 photos/day initially

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. WhatsApp-First Interface Compliance
- ✅ Planned implementation uses Twilio WhatsApp Business API
- ✅ No additional apps required for field agents
- ✅ Message queuing planned for poor connectivity
- ✅ Minimal training approach with natural conversation flow

### II. Immediate Feedback (NON-NEGOTIABLE)
- ✅ OpenAI Vision API for sub-30-second analysis
- ✅ Red-Green-Refactor cycle: Submit → Analyze → Feedback → Retake
- ✅ Automated quality checks without manual review
- ✅ Clear, actionable feedback messages designed

### III. 14-Step Verification Process
- ✅ Exact 14-step process defined in specification
- ✅ Step-specific verification criteria for each phase
- ✅ Sequential completion requirement enforced
- ✅ Photo metadata storage for audit trail
- ✅ Progress tracking for agents and supervisors

### IV. AI-Driven Quality Assurance
- ✅ OpenAI Vision API integration planned
- ✅ Step-specific prompts for each installation phase
- ✅ Confidence scoring system for all verifications
- ✅ Human escalation workflow for edge cases

### V. Observability & Compliance
- ✅ Structured logging for all interactions
- ✅ Performance metrics tracking (response time, accuracy)
- ✅ Compliance reporting framework
- ✅ Error handling with retry logic

## Project Structure

### Documentation (this feature)
```
specs/001-whatsapp-photo-verification/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── whatsapp-api.yaml
│   └── openai-vision.yaml
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── bot/                 # WhatsApp bot logic
│   ├── __init__.py
│   ├── bot.py          # Main bot conversation flow
│   ├── handlers.py     # Message handlers
│   └── utils.py        # WhatsApp utilities
├── verification/        # Photo verification engine
│   ├── __init__.py
│   ├── verifier.py     # OpenAI Vision integration
│   ├── prompts.py      # Step-specific verification prompts
│   └── models.py       # Verification data models
├── storage/            # Data persistence
│   ├── __init__.py
│   ├── sessions.py     # Agent session management
│   ├── photos.py       # Photo storage and retrieval
│   └── reports.py      # Compliance report generation
├── api/                # Web API endpoints
│   ├── __init__.py
│   ├── app.py          # Flask application
│   ├── routes.py       # API routes
│   └── middleware.py   # Request handling
└── utils/              # Shared utilities
    ├── __init__.py
    ├── config.py       # Configuration management
    ├── logger.py       # Structured logging
    └── errors.py       # Error handling

tests/
├── contract/           # Contract tests
│   ├── test_whatsapp_api.py
│   └── test_openai_vision.py
├── integration/        # Integration tests
│   ├── test_bot_flow.py
│   └── test_verification_pipeline.py
└── unit/               # Unit tests
    ├── test_verifier.py
    ├── test_sessions.py
    └── test_handlers.py

config/
├── development.py      # Development config
├── production.py       # Production config
└── testing.py          # Testing config

data/
├── photos/             # Photo storage
│   ├── pending/        # New submissions
│   ├── approved/       # Passed verifications
│   └── rejected/       # Failed verifications
└── sessions.json       # Agent session data
```

**Structure Decision**: Single project structure chosen for simplicity and rapid development. Clear separation of concerns with dedicated modules for bot logic, verification engine, storage, and API endpoints.

## Phase 0: Outline & Research

### Research Tasks:
1. **Twilio WhatsApp API Best Practices**
   - Rate limiting and message queuing strategies
   - Webhook reliability and error handling
   - Media handling for large photos

2. **OpenAI Vision API Integration**
   - Prompt engineering for consistent results
   - Error handling and rate limiting
   - Cost optimization strategies

3. **Photo Processing Pipeline**
   - Image compression and optimization
   - Format standardization
   - Storage and retrieval patterns

4. **Session Management**
   - WhatsApp conversation state management
   - Multi-job handling per agent
   - Session persistence and recovery

**Output**: research.md with all technical decisions documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Data Model Design** → `data-model.md`:
   - InstallationJob entity with 14-step tracking
   - PhotoSubmission entity with verification results
   - AgentSession entity with conversation state
   - VerificationResult entity with scoring and feedback

2. **API Contracts**:
   - WhatsApp webhook endpoint contract
   - OpenAI Vision API integration contract
   - Internal service contracts for verification pipeline

3. **Contract Tests**:
   - Webhook request/response validation
   - OpenAI API interaction patterns
   - Photo processing pipeline contracts

4. **Integration Test Scenarios**:
   - Complete 14-step installation flow
   - Error recovery and retry scenarios
   - Multi-agent concurrent usage

5. **Agent Configuration Update**:
   - Add WhatsApp bot development patterns
   - Include OpenAI Vision integration guidelines
   - Document testing strategies for conversational AI

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, claude.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- WhatsApp webhook contract → webhook endpoint task [P]
- OpenAI Vision contract → photo verifier task [P]
- Data model entities → model creation tasks [P]
- Integration scenarios → end-to-end test tasks

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models → verification → bot → API
- Mark [P] for parallel execution (independent modules)

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations identified - design aligns with all principles*

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `/memory/constitution.md`*