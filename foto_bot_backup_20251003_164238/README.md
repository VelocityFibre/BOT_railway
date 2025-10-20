# Fiber Installation Photo Verification System

Automated verification system for home fiber optic installation photos submitted by field agents. Ensures compliance with standard installation procedures across 14 required steps.

## Installation Steps & Photo Requirements

**Step 1: Property Frontage** – House, street number visible
**Step 2: Location on Wall (Before Install)** – Installation area photo
**Step 3: Outside Cable Span (Pole → Pigtail screw)** – Cable routing
**Step 4: Home Entry Point – Outside** – External entry point
**Step 5: Home Entry Point – Inside** – Internal entry point
**Step 6: Fibre Entry to ONT (After Install)** – ONT connection
**Step 7: Patched & Labelled Drop** – Cable labeling
**Step 8: Overall Work Area After Completion** – Clean workspace
**Step 9: ONT Barcode – Scan barcode + photo of label** – Equipment verification
**Step 10: Mini-UPS Serial Number (Gizzu)** – Backup power unit
**Step 11: Powermeter Reading (Drop/Feeder)** – Signal strength
**Step 12: Powermeter at ONT (Before Activation)** – Pre-activation readings
**Step 13: Active Broadband Light** – Service activation confirmation
**Step 14: Customer Signature** – Customer acceptance

## Quick Start (OpenAI Vision - Recommended)

**Setup Time:** 30 minutes | **Verification Rate:** 80-90% | **Cost:** ~$0.25 per complete installation

### Installation
```bash
pip install openai requests pillow python-dotenv
```

### Basic Usage
```python
from fiber_verifier import FiberInstallationVerifier

verifier = FiberInstallationVerifier(api_key="your-openai-key")
result = verifier.verify_installation_photos({
    "step1_frontage": "photos/step1.jpg",
    "step2_wall_before": "photos/step2.jpg",
    # ... all 14 steps
})
print(result.compliance_report)
```

## System Features

- ✅ Step-by-step photo validation
- ✅ Automatic missing step detection
- ✅ Quality checks for each photo type
- ✅ Compliance scoring and reporting
- ✅ Field agent feedback generation
- ✅ Batch processing capabilities

## Implementation Phases

1. **Week 1** - OpenAI Vision MVP setup with step-specific prompts
2. **Week 2** - Testing with sample installation photos
3. **Week 3** - Production workflow integration
4. **Week 4** - Custom fine-tuning with your verified photos

See [claude.md](claude.md) for detailed technical implementation and setup instructions.