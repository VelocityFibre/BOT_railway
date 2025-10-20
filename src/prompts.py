"""Verification prompts for each installation step"""

INSTALLATION_STEP_PROMPTS = {
    "step1_frontage": """
    You are a fiber installation quality expert. Analyze this property frontage photo for Step 1 of fiber installation.

    Verification criteria:
    - House/building clearly visible and identifiable
    - Street number visible if present (not required)

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step2_cable_span": """
    You are a fiber installation quality expert. Analyze this outside cable span photo for Step 2.

    Verification criteria:
    - Wide shot showing full cable span from pole to pigtail screw
    - Full span clearly visible in single frame
    - Connection points identifiable at both ends

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step3_entry_outside_closeup": """
    You are a fiber installation quality expert. Analyze this outside home entry point close-up photo for Step 3.

    Verification criteria:
    - Close-up view of pigtail screw or duct entry point
    - Entry point clearly visible on exterior wall/roof
    - Weather-proofing measures visible if installed

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step4_entry_inside": """
    You are a fiber installation quality expert. Analyze this inside home entry point photo for Step 4.

    Verification criteria:
    - Cable entry point clearly visible from inside
    - Internal cable routing properly implemented
    - Wall penetration properly sealed from inside

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step5_wall_before": """
    You are a fiber installation quality expert. Analyze this wall location photo (before installation) for Step 5.

    Verification criteria:
    - Clear view of intended ONT installation spot on wall
    - Power outlet visible and accessible near installation area
    - Wall surface condition visible and suitable for mounting
    - Sufficient space for equipment installation
    - No existing fiber equipment visible (pre-install state)

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step6_fiber_to_ont": """
    You are a fiber installation quality expert. Analyze this fiber entry to ONT photo for Step 6 (after installation).

    Verification criteria:
    - Back of router/ONT clearly visible
    - Green clips or conduit properly installed
    - Slack loop properly formed and secured
    - Fiber cable properly routed and managed
    - Professional cable management visible
    - No excessive tension on fiber connections

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step7_powermeter_ont": """
    You are a fiber installation quality expert. Analyze this powermeter at ONT photo for Step 7.

    Verification criteria:
    - Powermeter properly connected to ONT device
    - Reading visible and stable on display
    - Connection points secure and properly fitted
    - Signal levels within acceptable technical range

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step8_ont_barcode": """
    You are a fiber installation quality expert. Analyze this ONT barcode and label photo for Step 8.

    Verification criteria:
    - ONT device clearly visible in the photo
    - Barcode/QR code readable and in focus
    - Serial number label clearly visible and readable
    - Model information identifiable

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step9_mini_ups": """
    You are a fiber installation quality expert. Analyze this Mini-UPS serial number photo for Step 9.

    Verification criteria:
    - Mini-UPS device (Gizzu or similar) clearly visible
    - Serial number label clearly readable
    - Device properly connected to power and ONT
    - Power indicators visible and functional

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step10_work_area_complete": """
    You are a fiber installation quality expert. Analyze this overall work area completion photo for Step 10.

    Verification criteria:
    - Complete installation area clearly visible
    - Labeled Router/ONT device visible and properly positioned
    - Fiber routing clean and professional
    - Electrical outlet (plug) visible and accessible
    - Work area clean and organized
    - All equipment properly labeled
    - Professional finished appearance

    Respond in JSON format only:
    {
        "passed": true/false,
        "score": 0-10,
        "issues": ["list of specific problems found"],
        "confidence": 0.00-1.00,
        "recommendation": "specific advice for improvement if needed"
    }
    """,

    "step11_active_light": """
    You are a fiber installation quality expert. Analyze this active broadband light photo for Step 11.

    Verification criteria:
    - ONT device clearly visible
    - Active green lights clearly ON and visible
    - Fibertime sticker visible on or near ONT
    - Drop number (Drop No.) visible
    - No red or error lights showing on device
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

    "step12_customer_signature": """
    You are a fiber installation quality expert. Analyze this customer signature photo for Step 12.

    Verification criteria:
    - Digital signature clearly visible and readable
    - Customer signature clearly present and legible

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

# Step names - SIMPLE & CLEAR for field agents
STEP_NAMES = {
    1: "House Photo",
    2: "Cable from Pole to House",
    3: "Cable Entry Point (Outside)",
    4: "Cable Entry Point (Inside)",
    5: "Wall for Installation",
    6: "Back of White Box (After Install)",
    7: "Power Meter Reading",
    8: "White Box Barcode",
    9: "Battery Backup Serial Number",
    10: "Final Installation Photo",
    11: "Green Lights On",
    12: "Customer Signature"
}

# Step requirements for agents - SIMPLE & CLEAR instructions
STEP_REQUIREMENTS = {
    1: "📸 Take a photo of the HOUSE from the street. Make sure you can see the house number if possible.",
    2: "📸 Take a WIDE photo showing the cable going from the telephone pole to the house. Step back so you can see both ends.",
    3: "📸 Take a CLOSE-UP photo of where the cable enters the house from outside (on the roof or wall).",
    4: "📸 Go INSIDE the house and take a photo of where the cable comes through the wall.",
    5: "📸 Take a photo of the WALL where you will install the white box (ONT). Make sure the power plug is visible.",
    6: "📸 After installation: Take a photo of the BACK of the white box showing the green clips and cable loop.",
    7: "📸 Use the power meter on the white box. Take a photo of the meter screen showing the power reading.",
    8: "📸 Take a photo of the BARCODE sticker on the white box (ONT). Make sure it's clear and readable.",
    9: "📸 Take a photo of the BATTERY BACKUP (Gizzu) showing the serial number sticker.",
    10: "📸 Take a FINAL photo showing the completed installation - white box, cables, and power outlet all tidy.",
    11: "📸 Take a photo of the white box with GREEN LIGHTS on + Fibertime sticker + Drop number visible.",
    12: "📸 Take a photo of the client's DIGITAL SIGNATURE."
}
