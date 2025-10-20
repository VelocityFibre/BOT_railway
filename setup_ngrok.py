#!/usr/bin/env python3
"""Create ngrok tunnel for WhatsApp webhook"""

from pyngrok import ngrok
import os

def create_tunnel():
    """Create ngrok tunnel for Flask app"""

    # Kill existing tunnels
    ngrok.kill()

    # Create tunnel for port 5000
    tunnel = ngrok.connect(5000, "http")

    print(f"🔗 NGROK TUNNEL CREATED")
    print(f"Local URL: http://localhost:5000")
    print(f"Public URL: {tunnel.public_url}")
    print(f"Webhook URL: {tunnel.public_url}/webhook")
    print("=" * 50)
    print("Copy this URL for Twilio WhatsApp webhook:")
    print(f"{tunnel.public_url}/webhook")
    print("=" * 50)
    print("Press Ctrl+C to stop tunnel")

    try:
        # Keep tunnel running
        input("Press Enter to stop tunnel...")
    except KeyboardInterrupt:
        pass
    finally:
        ngrok.kill()

if __name__ == "__main__":
    create_tunnel()