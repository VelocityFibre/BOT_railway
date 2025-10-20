#!/usr/bin/env python3
"""
Supervisor Dashboard for Fiber Installation Photo Verification

Streamlit-based dashboard for monitoring installation progress,
agent performance, and system metrics.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuration
st.set_page_config(
    page_title="Fiber Verification Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.status-pass {
    color: #28a745;
    font-weight: bold;
}
.status-fail {
    color: #dc3545;
    font-weight: bold;
}
.status-active {
    color: #ffc107;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def load_sessions():
    """Load session data from file"""
    try:
        if os.path.exists('./data/sessions.json'):
            with open('./data/sessions.json', 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading sessions: {e}")
        return {}

def load_verification_results():
    """Load verification results from photo directories"""
    results = []

    # Load approved photos
    approved_dir = './data/photos/approved'
    if os.path.exists(approved_dir):
        for filename in os.listdir(approved_dir):
            if filename.endswith('.jpg'):
                parts = filename.replace('.jpg', '').split('_')
                if len(parts) >= 4:
                    job_id = parts[0] + '_' + parts[1]
                    step = parts[2].replace('step', '')
                    status = parts[3]
                    results.append({
                        'job_id': job_id,
                        'step': int(step),
                        'status': 'PASS' if status == 'PASS' else 'FAIL',
                        'filename': filename,
                        'timestamp': datetime.fromtimestamp(os.path.getmtime(os.path.join(approved_dir, filename)))
                    })

    return results

def calculate_metrics(sessions, results):
    """Calculate dashboard metrics"""
    # Session metrics
    total_sessions = len(sessions)
    active_sessions = len([s for s in sessions.values() if s.get('status') == 'active'])
    completed_sessions = len([s for s in sessions.values() if s.get('status') == 'completed'])

    # Verification metrics
    total_verifications = len(results)
    passed_verifications = len([r for r in results if r['status'] == 'PASS'])
    pass_rate = (passed_verifications / total_verifications * 100) if total_verifications > 0 else 0

    # Agent metrics
    agents = list(set([s.get('agent_id', 'unknown') for s in sessions.values()]))
    unique_agents = len(agents)

    # Recent activity (last 24 hours)
    cutoff = datetime.now() - timedelta(hours=24)
    recent_activity = len([r for r in results if r['timestamp'] > cutoff])

    return {
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'completed_sessions': completed_sessions,
        'total_verifications': total_verifications,
        'pass_rate': pass_rate,
        'unique_agents': unique_agents,
        'recent_activity': recent_activity
    }

def create_activity_chart(results):
    """Create activity timeline chart"""
    if not results:
        return None

    df = pd.DataFrame(results)
    df['hour'] = df['timestamp'].dt.floor('H')
    hourly_counts = df.groupby('hour').size().reset_index(name='count')

    fig = px.line(
        hourly_counts,
        x='hour',
        y='count',
        title='Verification Activity Over Time',
        labels={'hour': 'Time', 'count': 'Verifications'}
    )
    fig.update_layout(showlegend=False)
    return fig

def create_step_performance_chart(results):
    """Create step performance chart"""
    if not results:
        return None

    df = pd.DataFrame(results)
    step_performance = df.groupby('step').agg({
        'status': lambda x: (x == 'PASS').sum() / len(x) * 100
    }).reset_index()
    step_performance.rename(columns={'status': 'pass_rate'}, inplace=True)

    fig = px.bar(
        step_performance,
        x='step',
        y='pass_rate',
        title='Pass Rate by Installation Step',
        labels={'step': 'Step Number', 'pass_rate': 'Pass Rate (%)'}
    )
    fig.update_layout(yaxis=dict(range=[0, 100]))
    return fig

def create_agent_performance_table(sessions):
    """Create agent performance table"""
    if not sessions:
        return pd.DataFrame()

    agent_data = []
    for phone, session in sessions.items():
        agent_data.append({
            'Agent ID': session.get('agent_id', 'unknown'),
            'Phone': phone,
            'Current Job': session.get('current_job_id', 'none'),
            'Current Step': session.get('current_step', 0),
            'Completed Steps': len(session.get('completed_steps', {})),
            'Status': session.get('status', 'unknown'),
            'Last Activity': session.get('last_activity', 'unknown')
        })

    df = pd.DataFrame(agent_data)
    return df.sort_values('Completed Steps', ascending=False)

def main():
    """Main dashboard application"""
    st.title("🔧 Fiber Installation Photo Verification Dashboard")
    st.markdown("---")

    # Load data
    sessions = load_sessions()
    results = load_verification_results()
    metrics = calculate_metrics(sessions, results)

    # Sidebar filters
    st.sidebar.header("Filters")

    # Time range filter
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
        index=0
    )

    # Status filter
    status_filter = st.sidebar.multiselect(
        "Session Status",
        ["active", "completed", "abandoned"],
        default=["active", "completed"]
    )

    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()

    # Key metrics
    st.header("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Total Sessions</p>
        </div>
        """.format(metrics['total_sessions']), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Active Installations</p>
        </div>
        """.format(metrics['active_sessions']), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>{:.1f}%</h3>
            <p>Pass Rate</p>
        </div>
        """.format(metrics['pass_rate']), unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Unique Agents</p>
        </div>
        """.format(metrics['unique_agents']), unsafe_allow_html=True)

    # Charts section
    st.header("📈 Analytics")

    col1, col2 = st.columns(2)

    with col1:
        activity_chart = create_activity_chart(results)
        if activity_chart:
            st.plotly_chart(activity_chart, use_container_width=True)
        else:
            st.info("No activity data available")

    with col2:
        step_chart = create_step_performance_chart(results)
        if step_chart:
            st.plotly_chart(step_chart, use_container_width=True)
        else:
            st.info("No step performance data available")

    # Recent activity
    st.header("🕐 Recent Activity")

    # Filter results based on time range
    if results:
        df = pd.DataFrame(results)
        if time_range == "Last 24 Hours":
            cutoff = datetime.now() - timedelta(hours=24)
            df = df[df['timestamp'] > cutoff]
        elif time_range == "Last 7 Days":
            cutoff = datetime.now() - timedelta(days=7)
            df = df[df['timestamp'] > cutoff]
        elif time_range == "Last 30 Days":
            cutoff = datetime.now() - timedelta(days=30)
            df = df[df['timestamp'] > cutoff]

        if not df.empty:
            # Format timestamp for display
            df['time'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            display_df = df[['time', 'job_id', 'step', 'status']].sort_values('time', ascending=False)

            # Add status styling
            def highlight_status(val):
                if val == 'PASS':
                    return 'color: #28a745; font-weight: bold'
                elif val == 'FAIL':
                    return 'color: #dc3545; font-weight: bold'
                return ''

            styled_df = display_df.style.applymap(highlight_status, subset=['status'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent activity found")
    else:
        st.info("No verification data available")

    # Agent performance
    st.header("👥 Agent Performance")

    agent_df = create_agent_performance_table(sessions)
    if not agent_df.empty:
        # Filter by status if selected
        if status_filter:
            agent_df = agent_df[agent_df['Status'].isin(status_filter)]

        if not agent_df.empty:
            st.dataframe(agent_df, use_container_width=True, hide_index=True)
        else:
            st.info("No agents match the selected filters")
    else:
        st.info("No agent data available")

    # System health
    st.header("🏥 System Health")

    col1, col2, col3 = st.columns(3)

    with col1:
        # API status
        api_status = "🟢 Healthy" if True else "🔴 Error"  # Could add actual health check
        st.metric("API Status", api_status)

    with col2:
        # Storage status
        storage_used = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk('./data/photos')
                          for filename in filenames) / (1024 * 1024)  # MB
        st.metric("Photo Storage", f"{storage_used:.1f} MB")

    with col3:
        # Recent activity rate
        st.metric("24h Activity", f"{metrics['recent_activity']} verifications")

    # Footer
    st.markdown("---")
    st.markdown("**Fiber Installation Photo Verification System** | Last updated: {}".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

if __name__ == "__main__":
    main()