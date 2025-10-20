#!/usr/bin/env python3
"""
Manual webhook test for WhatsApp bot
This simulates a Twilio webhook request to test the bot functionality
"""

import requests
import json

def test_bot_webhook():
    """Test the bot's webhook endpoint with a manual request"""

    # Bot webhook URL (local)
    webhook_url = "http://localhost:5000/webhook"

    # Simulate Twilio webhook data for WhatsApp message
    data = {
        'From': 'whatsapp:+27821234567',  # Test phone number
        'To': 'whatsapp:+14155238886',    # Twilio number
        'Body': 'START',                  # Message content
        'NumMedia': '0'                   # No media in this test
    }

    # Headers to simulate Twilio request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'TwilioProxy/1.1'
    }

    try:
        print("🧪 Testing WhatsApp bot webhook...")
        print(f"📱 Simulating message: {data['Body']}")
        print(f"📞 From: {data['From']}")
        print(f"📞 To: {data['To']}")
        print("=" * 50)

        # Send POST request to webhook
        response = requests.post(webhook_url, data=data, headers=headers, timeout=30)

        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Response Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print("=" * 50)
        print("📋 Response Body:")
        print(response.text)
        print("=" * 50)

        if response.status_code == 200:
            print("🎉 Webhook test successful!")
            if response.headers.get('Content-Type', '').startswith('text/xml'):
                print("✅ Bot responded with TwiML (correct format)")
            else:
                print("⚠️  Bot didn't respond with TwiML format")
        else:
            print(f"❌ Webhook test failed with status {response.status_code}")

        return response.status_code == 200

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server not running on localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Bot took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_photo_simulation():
    """Test bot with a simulated photo message"""

    webhook_url = "http://localhost:5000/webhook"

    # Simulate photo message with step
    data = {
        'From': 'whatsapp:+27821234567',
        'To': 'whatsapp:+14155238886',
        'Body': '1',                    # Step 1
        'NumMedia': '1',               # One media file
        'MediaContentType0': 'image/jpeg',
        'MediaUrl0': 'https://example.com/test.jpg'  # Test URL
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'TwilioProxy/1.1'
    }

    try:
        print("\n🖼️  Testing photo simulation...")
        print(f"📊 Simulating step: {data['Body']}")
        print(f"📎 Media files: {data['NumMedia']}")
        print("=" * 50)

        response = requests.post(webhook_url, data=data, headers=headers, timeout=30)

        print(f"✅ Response Status: {response.status_code}")
        print("=" * 50)
        print("📋 Response Body:")
        print(response.text)

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Photo test error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 WhatsApp Bot Webhook Tester")
    print("=" * 50)

    # Test basic START command
    success1 = test_bot_webhook()

    # Test photo simulation
    success2 = test_photo_simulation()

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"✅ START command: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Photo simulation: {'PASS' if success2 else 'FAIL'}")

    if success1 and success2:
        print("\n🎉 All tests passed! Bot is working correctly.")
        print("💡 Next step: Set up public tunnel (ngrok/localtunnel) for WhatsApp webhook")
    else:
        print("\n❌ Some tests failed. Check bot logs and fix issues.")