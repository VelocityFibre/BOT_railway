#!/usr/bin/env python3
"""Test skip functionality to ensure proper step progression"""

import sys
import os
sys.path.append('.')

from src.bot.bot import FiberInstallationBot
from src.storage.sessions import SessionManager

def test_skip_progression():
    """Test that skip commands work correctly through all steps"""
    
    print("🧪 Testing Skip Functionality...")
    
    # Create bot instance
    bot = FiberInstallationBot()
    test_phone = "+1234567890"
    
    # Clean up any existing session
    if bot.session_manager.get_session(test_phone):
        bot.session_manager.reset_session(test_phone)
    
    print("\n1️⃣ Testing START command...")
    response = bot.process_message(test_phone, "START")
    print(f"Response: {response[:100]}...")
    
    print("\n2️⃣ Testing DR number input...")
    response = bot.process_message(test_phone, "DR0000001")
    print(f"Response: {response[:100]}...")
    
    print("\n3️⃣ Testing location SKIP...")
    response = bot.process_message(test_phone, "SKIP")
    print(f"Response: {response[:100]}...")
    
    # Check session state
    session = bot.session_manager.get_session(test_phone)
    print(f"Current Step: {session.current_step}")
    print(f"Location Verified: {session.location_verified}")
    
    # Test photo step skips
    for step in range(1, 13):
        print(f"\n{step+3}️⃣ Testing SKIP for Step {step}...")
        session = bot.session_manager.get_session(test_phone)
        
        if session.current_step != step:
            print(f"❌ Expected step {step}, but current step is {session.current_step}")
            break
            
        response = bot.process_message(test_phone, "SKIP")
        print(f"Response snippet: {response[:200]}...")
        
        # Check session after skip
        session_after = bot.session_manager.get_session(test_phone)
        expected_next_step = step + 1 if step < 12 else 13
        
        if session_after.current_step == expected_next_step:
            print(f"✅ Step {step} skipped correctly, now on step {session_after.current_step}")
        else:
            print(f"❌ Step {step} skip failed. Expected step {expected_next_step}, got {session_after.current_step}")
            break
            
        print(f"Completed steps: {len(session_after.completed_steps)}")
        
        # Stop if we've completed all steps
        if session_after.current_step > 12:
            print(f"🎉 All steps completed! Status: {session_after.status}")
            break

def test_step_names_consistency():
    """Test that step names are consistent across the system"""
    print("\n📝 Testing Step Names Consistency...")
    
    from src.prompts import STEP_NAMES, STEP_REQUIREMENTS
    from src.verifier import FiberInstallationVerifier
    
    verifier = FiberInstallationVerifier()
    
    print(f"Total STEP_NAMES entries: {len(STEP_NAMES)}")
    print(f"Total STEP_REQUIREMENTS entries: {len(STEP_REQUIREMENTS)}")
    
    # Check that all steps 1-12 have names and requirements
    for step in range(1, 13):
        step_name = STEP_NAMES.get(step, "MISSING")
        step_req = STEP_REQUIREMENTS.get(step, "MISSING")
        
        # Check verifier has matching step
        verifier_step_name = verifier._get_step_name(step)
        
        print(f"Step {step:2d}: {step_name}")
        if step_name == "MISSING" or step_req == "MISSING":
            print(f"❌ Step {step} missing name or requirement")
        elif step_name != verifier_step_name:
            print(f"❌ Step {step} name mismatch: STEP_NAMES='{step_name}' vs VERIFIER='{verifier_step_name}'")
        else:
            print(f"✅ Step {step} consistent")

if __name__ == "__main__":
    try:
        test_step_names_consistency()
        test_skip_progression()
        print("\n🎯 Skip functionality test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()