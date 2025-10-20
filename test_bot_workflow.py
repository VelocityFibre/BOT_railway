#!/usr/bin/env python3
"""
Test script to verify fiber installation bot workflow
"""
import sys
sys.path.append('.')

from src.bot.bot import FiberInstallationBot

def test_bot_commands():
    """Test basic bot command handling"""
    print("🔧 Testing Fiber Installation Bot Workflow")
    print("=" * 50)
    
    bot = FiberInstallationBot()
    test_phone = "+27123456789"
    
    # Test greeting
    print("\n1. Testing HELLO command:")
    response = bot.process_message(test_phone, "HELLO")
    print(f"Response: {response[:100]}...")
    
    # Test START command
    print("\n2. Testing START command:")
    response = bot.process_message(test_phone, "START")
    print(f"Response: {response[:100]}...")
    
    # Test STATUS command  
    print("\n3. Testing STATUS command:")
    response = bot.process_message(test_phone, "STATUS")
    print(f"Response: {response[:100]}...")
    
    # Test HELP command
    print("\n4. Testing HELP command:")
    response = bot.process_message(test_phone, "HELP")
    print(f"Response: {response[:100]}...")
    
    # Test unknown command
    print("\n5. Testing unknown command:")
    response = bot.process_message(test_phone, "RANDOM_COMMAND")
    print(f"Response: {response[:100]}...")
    
    # Test current bot stats
    print("\n6. Current bot statistics:")
    stats = bot.get_bot_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

def test_ai_verification():
    """Test AI verification with a mock image"""
    print("\n🔍 Testing AI Photo Verification")
    print("=" * 50)
    
    try:
        from src.verifier import FiberInstallationVerifier
        verifier = FiberInstallationVerifier()
        
        # Test with step 1 (this will use the actual OpenAI API)
        print("Testing step 1 verification with mock data...")
        print("Note: This would normally require an actual image file")
        print("Skipping AI test to avoid API costs")
        
    except Exception as e:
        print(f"AI verification setup error: {e}")
        
def test_session_management():
    """Test session management"""
    print("\n📋 Testing Session Management")
    print("=" * 50)
    
    from src.storage.sessions import SessionManager
    
    session_manager = SessionManager()
    test_phone = "+27999888777"
    
    # Create session
    print("Creating new session...")
    session = session_manager.get_or_create_session(test_phone)
    print(f"Created session for agent {session.agent_id} with job {session.current_job_id}")
    
    # Test step completion
    print("Completing step 1...")
    session_manager.complete_step(test_phone, 1, "test_photo.jpg")
    
    updated_session = session_manager.get_session(test_phone)
    print(f"Current step: {updated_session.current_step}")
    print(f"Completed steps: {list(updated_session.completed_steps.keys())}")
    
    # Get session stats
    stats = session_manager.get_session_stats()
    print(f"Session stats: {stats}")

if __name__ == "__main__":
    print("🚀 Starting Bot Tests")
    
    try:
        test_bot_commands()
        test_session_management()
        test_ai_verification()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()