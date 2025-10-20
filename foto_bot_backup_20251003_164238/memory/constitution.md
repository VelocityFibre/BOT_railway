# Fiber Photo Verification Constitution

## Core Principles

### I. WhatsApp-First Interface
Every interaction must work through WhatsApp interface; Field agents already have WhatsApp installed; No additional apps required; Interface must be intuitive with minimal training; Support for poor connectivity areas with message queuing

### II. Immediate Feedback (NON-NEGOTIABLE)
All photo submissions must receive AI feedback within 30 seconds; Red-Green-Refactor cycle for photos: Submit → Analyze → Feedback → Retake if needed; No manual review required for initial quality checks; Clear, actionable feedback messages

### III. 14-Step Verification Process
Every installation must follow the exact 14-step process; Each step has specific verification criteria; Steps must be completed in order; Photos stored with metadata for audit trail; Progress tracking visible to agents and supervisors

### IV. AI-Driven Quality Assurance
OpenAI Vision API for photo analysis; Step-specific prompts for each installation phase; Confidence scoring for all verifications; Human escalation for edge cases; Continuous model improvement based on feedback

### V. Observability & Compliance
All interactions logged for audit purposes; Structured logging required; Performance metrics tracked (response time, accuracy); Compliance reporting for installation standards; Error handling with retry logic

## Technology Stack Requirements

### Core Technologies
- **Backend**: Python 3.9+ with Flask
- **AI**: OpenAI Vision API (GPT-4 Vision)
- **Messaging**: Twilio WhatsApp Business API
- **Storage**: Local file system with cloud backup option
- **Dashboard**: Streamlit for supervisor interface

### Development Standards
- **Testing**: pytest with 90%+ coverage required
- **Code Quality**: black formatting, flake8 linting
- **Documentation**: All functions documented with docstrings
- **Security**: API keys encrypted, rate limiting implemented
- **Performance**: <30 second response time SLA

## Deployment & Operations

### Environment Requirements
- **Development**: Local testing with ngrok for WhatsApp webhooks
- **Staging**: Full integration testing with test phone numbers
- **Production**: Cloud deployment with monitoring and alerts
- **Backup**: Daily backups of all photos and session data

### Quality Gates
- All new features must pass automated testing
- WhatsApp conversation flows must be manually tested
- Photo verification accuracy must be >90%
- Response time must be <30 seconds for 95% of requests
- Code review required for all changes

## Governance

### Decision Making
- Constitution supersedes all other practices
- Field agent feedback required for major changes
- Technical decisions must not compromise user experience
- All changes must maintain backward compatibility

### Amendment Process
- Amendments require documentation, approval, migration plan
- Changes to 14-step process require field testing
- Technology stack changes require proof of concept
- All amendments must be ratified by project manager

### Compliance Requirements
- All PRs must verify constitutional compliance
- Complexity must be justified with business value
- Use implementation guidance files for runtime development
- Monthly compliance audits required

## Success Metrics

### User Experience
- Field agent adoption rate >95%
- Photo retake reduction >70%
- Installation time reduction >30%
- User satisfaction >4.5/5

### Technical Performance
- API uptime >99.5%
- Response time <30 seconds (95th percentile)
- Verification accuracy >90%
- Zero data loss incidents

---

**Version**: 1.0.0 | **Ratified**: 2025-10-01 | **Last Amended**: 2025-10-01
**Approved By**: Hein (Project Manager) | **Next Review**: 2025-11-01