#!/usr/bin/env python3
"""
Simple web interface to test the verification engine locally
without WhatsApp costs
"""

import streamlit as st
import sys
import os
from PIL import Image
import io
import json
from datetime import datetime

sys.path.append('.')

from src.verifier import FiberInstallationVerifier
from src.storage.sessions import SessionManager

def main():
    st.title("🔧 Fiber Installation Photo Verification - Local Test")
    st.markdown("---")

    # Initialize components
    verifier = FiberInstallationVerifier()
    session_manager = SessionManager()

    # Sidebar for agent info
    st.sidebar.header("👷 Agent Info")
    agent_phone = st.sidebar.text_input("Phone Number", value="+27821234567")
    agent_id = st.sidebar.text_input("Agent ID", value="TEST_AGENT_001")

    # Get or create session
    session = session_manager.get_or_create_session(agent_phone, agent_id)

    st.sidebar.markdown("---")
    st.sidebar.metric("Current Step", session.current_step)
    st.sidebar.metric("Completed Steps", len(session.completed_steps))

    # Main interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📷 Photo Upload")

        # Step selector
        step = st.selectbox(
            "Select Installation Step",
            options=list(range(1, 15)),
            format_func=lambda x: f"Step {x}: {verifier._get_step_name(x)}",
            index=session.current_step - 1 if session.current_step <= 14 else 0
        )

        # Photo upload
        uploaded_file = st.file_uploader(
            f"Upload photo for Step {step}",
            type=['jpg', 'jpeg', 'png'],
            help=f"Upload a clear photo for: {verifier._get_step_name(step)}"
        )

        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Uploaded: Step {step}", use_column_width=True)

            # Analyze button
            if st.button(f"🔍 Analyze Step {step} Photo", type="primary"):
                with st.spinner("🤖 AI analyzing photo..."):
                    # Save uploaded image temporarily
                    temp_path = f"temp_step{step}_photo.jpg"
                    # Convert to RGB to handle PNG transparency
                    if image.mode in ('RGBA', 'LA', 'P'):
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = rgb_image
                    image.save(temp_path, "JPEG")

                    try:
                        # Verify photo
                        result = verifier.verify_step(temp_path, step)

                        # Display results
                        st.markdown("---")
                        st.header("📊 Analysis Results")

                        # Status
                        if result.passed:
                            st.success(f"✅ Step {step} PASSED")
                        else:
                            st.error(f"❌ Step {step} NEEDS RETAKE")

                        # Metrics
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Score", f"{result.score}/10")
                        with col_b:
                            st.metric("Confidence", f"{result.confidence:.0%}")
                        with col_c:
                            st.metric("Status", "PASS" if result.passed else "FAIL")

                        # Issues
                        if result.issues:
                            st.subheader("🔍 Issues Found:")
                            for issue in result.issues:
                                st.write(f"• {issue}")

                        # Recommendation
                        if result.recommendation:
                            st.subheader("💡 Recommendation:")
                            st.info(result.recommendation)

                        # Update session if passed
                        if result.passed:
                            session_manager.complete_step(agent_phone, step, temp_path)
                            st.success(f"✅ Step {step} marked as completed!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")

                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    with col2:
        st.header("📋 Progress")

        # Progress bar
        progress = len(session.completed_steps) / 14
        st.progress(progress)
        st.write(f"**{len(session.completed_steps)}/14** steps completed")

        # Step checklist
        st.subheader("Completed Steps:")
        for step_num in range(1, 15):
            status = "✅" if step_num in session.completed_steps else "⏳"
            step_name = verifier._get_step_name(step_num)
            st.write(f"{status} Step {step_num}: {step_name}")

        # Session info
        st.subheader("Session Details:")
        st.write(f"**Job ID:** {session.current_job_id}")
        st.write(f"**Agent:** {session.agent_id}")
        st.write(f"**Status:** {session.status}")
        st.write(f"**Started:** {session.session_start.strftime('%Y-%m-%d %H:%M')}")

    # Bottom actions
    st.markdown("---")
    col_reset, col_status = st.columns([1, 2])

    with col_reset:
        if st.button("🔄 Reset Session", type="secondary"):
            session_manager.reset_session(agent_phone)
            st.rerun()

    with col_status:
        if st.button("📊 View Dashboard", type="secondary"):
            st.info("Dashboard running at: http://localhost:8501")

if __name__ == "__main__":
    main()