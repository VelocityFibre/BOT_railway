"""Verification prompts for each installation step"""

INSTALLATION_STEP_PROMPTS = {
    "step1_frontage": """
    You are a fiber installation quality expert. Analyze this property frontage photo for Step 1 of fiber installation.

    Verification criteria:
    - House/building clearly visible and identifiable
    - Street number clearly readable
    - Good lighting conditions (daytime preferred)
    - No major obstructions blocking the view
    - Professional photo quality (not blurry, well-framed)

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step2_wall_before": """
    You are a fiber installation quality expert. Analyze this wall location photo (before installation) for Step 2.

    Verification criteria:
    - Clear view of intended installation area on wall
    - No existing fiber equipment visible (new install)
    - Wall surface condition visible and suitable
    - Mounting point can be identified
    - Sufficient space for equipment installation

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step3_cable_span": """
    You are a fiber installation quality expert. Analyze this outside cable span photo for Step 3.

    Verification criteria:
    - Cable visible running from pole to pigtail screw
    - Proper cable tension (no excessive sagging)
    - Cable secured at multiple points along the span
    - No visible cable damage, kinks, or sharp bends
    - Minimum bending radius maintained
    - Weather-proofing measures visible

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step4_entry_outside": """
    You are a fiber installation quality expert. Analyze this outside home entry point photo for Step 4.

    Verification criteria:
    - Cable entry point clearly visible on exterior wall
    - Weather-proofing measures properly installed
    - Wall penetration protected and sealed
    - Cable strain relief properly implemented
    - Professional exterior installation

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step5_entry_inside": """
    You are a fiber installation quality expert. Analyze this inside home entry point photo for Step 5.

    Verification criteria:
    - Cable entry point clearly visible from inside
    - Internal cable routing properly implemented
    - Wall penetration properly sealed from inside
    - No excessive cable slack inside the building
    - Clean and professional internal installation

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step6_ont_connection": """
    You are a fiber installation quality expert. Analyze this ONT connection photo for Step 6.

    Verification criteria:
    - ONT (Optical Network Terminal) device clearly visible
    - Fiber cable properly connected to ONT port
    - No visible damage to fiber connectors
    - Cable properly secured to ONT device
    - Connection points clean and properly aligned

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step7_patched_labelled": """
    You are a fiber installation quality expert. Analyze this patched and labeled drop cable photo for Step 7.

    Verification criteria:
    - Cable patches clearly visible and properly made
    - Labels readable and properly placed on cables
    - Cable organization tidy and professional
    - Color coding follows industry standards
    - All connections properly secured

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step8_work_area_complete": """
    You are a fiber installation quality expert. Analyze this work area completion photo for Step 8.

    Verification criteria:
    - Work area clean and organized after installation
    - No tools, debris, or waste materials left behind
    - Cables properly bundled and secured
    - Professional appearance maintained
    - Safety standards followed

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step9_ont_barcode": """
    You are a fiber installation quality expert. Analyze this ONT barcode and label photo for Step 9.

    Verification criteria:
    - ONT device clearly visible in the photo
    - Barcode/QR code readable and in focus
    - Serial number label clearly visible and readable
    - Model information identifiable
    - Equipment labels properly documented

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step10_mini_ups": """
    You are a fiber installation quality expert. Analyze this Mini-UPS serial number photo for Step 10.

    Verification criteria:
    - Mini-UPS device (Gizzu or similar) clearly visible
    - Serial number label clearly readable
    - Device properly connected to power and ONT
    - Power indicators visible and functional
    - Installation follows manufacturer guidelines

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step11_powermeter_reading": """
    You are a fiber installation quality expert. Analyze this powermeter reading photo for Step 11.

    Verification criteria:
    - Powermeter device clearly visible
    - Reading display clearly shown and readable
    - Values within expected technical ranges
    - Device properly connected to fiber line
    - Measurement stable and accurate

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step12_powermeter_ont": """
    You are a fiber installation quality expert. Analyze this powermeter at ONT photo for Step 12.

    Verification criteria:
    - Powermeter properly connected to ONT device
    - Reading visible and stable on display
    - Connection points secure and properly fitted
    - Signal levels within acceptable technical range
    - Pre-activation measurements recorded

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step13_active_light": """
    You are a fiber installation quality expert. Analyze this active broadband light photo for Step 13.

    Verification criteria:
    - ONT device clearly visible
    - Active broadband/status light clearly ON
    - No red or error lights showing on device
    - Light indicators clearly visible in photo
    - Service activation confirmed by visual indicators

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step14_customer_signature": """
    You are a fiber installation quality expert. Analyze this customer signature photo for Step 14.

    Verification criteria:
    - Signed document clearly visible and readable
    - Customer signature clearly present and legible
    - Date visible and current/accurate
    - Document properly filled out with required information
    - Customer acceptance clearly documented

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """
}

# Step names for user-friendly messages
STEP_NAMES = {
    1: "Property Frontage",
    2: "Location on Wall (Before Install)",
    3: "Outside Cable Span",
    4: "Home Entry Point - Outside",
    5: "Home Entry Point - Inside",
    6: "Fibre Entry to ONT",
    7: "Patched & Labelled Drop",
    8: "Overall Work Area After Completion",
    9: "ONT Barcode",
    10: "Mini-UPS Serial Number",
    11: "Powermeter Reading (Drop/Feeder)",
    12: "Powermeter at ONT (Before Activation)",
    13: "Active Broadband Light",
    14: "Customer Signature"
}

# Step requirements for agents
STEP_REQUIREMENTS = {
    1: "Take a clear photo of the house/building with street number visible",
    2: "Show the wall area where equipment will be installed (before mounting)",
    3: "Photograph the cable running from pole to pigtail screw",
    4: "Show where cable enters the house from outside",
    5: "Show the cable entry point from inside the house",
    6: "Photograph the fiber cable connected to the ONT device",
    7: "Show patched and labeled cables clearly",
    8: "Take a photo of the completed, clean work area",
    9: "Photograph ONT barcode and serial number label",
    10: "Show Mini-UPS device with serial number visible",
    11: "Photograph powermeter reading for drop/feeder",
    12: "Show powermeter reading at ONT before activation",
    13: "Photograph active broadband light on ONT",
    14: "Take photo of customer's signed document"
}