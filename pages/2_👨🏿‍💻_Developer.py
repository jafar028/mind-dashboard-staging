"""
Developer Dashboard - COMPLETE STANDALONE VERSION
AI Performance, API Analytics & System Debugging
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import plotly.express as px
import plotly.graph_objects as go

# Import auth functions directly
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.auth_handler import require_authentication, show_user_info_sidebar, get_current_user
    from config.auth import can_access_page
    from utils.bigquery import run_query
    from utils.posthog_analytics import (
        fetch_application_logs,
        fetch_error_distribution_by_type,
        fetch_error_free_session_rate,
        fetch_exception_rate_trends,
        fetch_network_connectivity,
        fetch_performance_percentiles,
        fetch_rage_clicks,
        fetch_users_affected_by_errors,
        fetch_web_vitals_metrics,
    )
except Exception:
    st.error("Import error - please check file structure")
    st.stop()

# Page config
st.set_page_config(
    page_title="Developer Dashboard | MIND Platform",
    page_icon="👨🏿‍💻",
    layout="wide"
)

# Authentication
require_authentication()
user = get_current_user()
if not can_access_page(user['role'], 'Developer'):
    st.error("⛔ Access Denied: Developer privileges required")
    st.stop()

# Theme toggle and logo display
try:
    import base64
    
    # Initialize theme in session state if not exists
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'  # Default to dark theme
    
    # Display theme toggle in sidebar
    with st.sidebar:
        col1, col2 = st.columns([3, 1])
        with col2:
            # Theme toggle button
            if st.session_state.theme == 'dark':
                if st.button("☀️", help="Switch to light mode", key="theme_toggle"):
                    st.session_state.theme = 'light'
                    st.rerun()
            else:
                if st.button("🌙", help="Switch to dark mode", key="theme_toggle"):
                    st.session_state.theme = 'dark'
                    st.rerun()
    
    # Select appropriate logo based on theme
    if st.session_state.theme == 'dark':
        LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_light.png"
    else:
        LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_dark.png"
    
    # Display logo
    try:
        with open(LOGO_PATH, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        
        st.sidebar.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
            </div>
        """, unsafe_allow_html=True)
    except:
        pass
    
    # Apply theme CSS
    if st.session_state.theme == 'light':
        st.markdown("""
            <style>
            /* Light theme overrides */
            :root {
                --background-color: #ffffff;
                --secondary-background-color: #f0f2f6;
                --text-color: #262730;
            }
            .stApp {
                background-color: #ffffff;
                color: #262730;
            }
            .stSidebar {
                background-color: #f0f2f6;
            }
            section[data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
            .stMarkdown, .stText {
                color: #262730;
            }
            /* Chart/Plot containers - white backgrounds */
            div[data-testid="stPlotlyChart"] {
                background-color: #ffffff !important;
            }
            .js-plotly-plot {
                background-color: #ffffff !important;
            }
            /* Metric containers */
            div[data-testid="stMetric"] {
                background-color: #ffffff;
            }
            /* Dataframe containers */
            div[data-testid="stDataFrame"] {
                background-color: #ffffff;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            /* Dark theme (default) */
            :root {
                --background-color: #0e1117;
                --secondary-background-color: #262730;
                --text-color: #fafafa;
            }
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stSidebar {
                background-color: #262730;
            }
            section[data-testid="stSidebar"] {
                background-color: #262730;
            }
            </style>
        """, unsafe_allow_html=True)
        
except Exception:
    pass

# Sidebar user info
show_user_info_sidebar()


# Constants
DATASET_ID = "gen-lang-client-0625543859.mind_analytics"

# Chart helper functions
def plot_bar_chart(df, x, y, title, orientation='v', height=400):
    fig = px.bar(df, x=x, y=y, title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), orientation=orientation, height=height)
    fig.update_layout(plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
    return fig

def plot_line_chart(df, x, y, title, height=400):
    fig = px.line(df, x=x, y=y, title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), height=height)
    fig.update_layout(plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')), hovermode='x unified')
    return fig

def create_multi_line_chart(df, x, y_columns, title, height=400):
    fig = go.Figure()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#3498DB']
    for idx, col in enumerate(y_columns):
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=col, mode='lines+markers', 
                                line=dict(color=colors[idx % len(colors)])))
    fig.update_layout(title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), 
                     paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')), 
                     hovermode='x unified', height=height)
    return fig


def apply_theme_layout(fig, title, xaxis_title, yaxis_title, height=400):
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template=("plotly" if st.session_state.get("theme") == "light" else "plotly_dark"),
        plot_bgcolor=("#ffffff" if st.session_state.get("theme") == "light" else "#262730"),
        paper_bgcolor=("#ffffff" if st.session_state.get("theme") == "light" else "#0E1117"),
        font=dict(color=("#262730" if st.session_state.get("theme") == "light" else "#FAFAFA")),
        height=height,
        hovermode="x unified"
    )
    return fig

# Header
st.title("👨🏿‍💻 Developer Dashboard")
st.markdown("### AI Performance, API Analytics & System Debugging")
st.markdown("---")

# Filters in sidebar
with st.sidebar:
    st.markdown("### 🔍 Filters")
    today = datetime.now(timezone.utc).date()
    default_start = today - timedelta(days=30)
    date_range = st.date_input(
        "Date range",
        value=(default_start, today),
        max_value=today
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = date_range
        end_date = date_range

    start_ts = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    end_ts = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)

    st.markdown("---")
    st.markdown("### 🔧 Developer Tools")

    time_window = st.selectbox(
        "Analysis Window",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
        index=3
    )

    time_map = {
        "Last Hour": 1 / 24,
        "Last 6 Hours": 6 / 24,
        "Last 24 Hours": 1,
        "Last 7 Days": 7
    }
    days = time_map[time_window]

    st.markdown("---")
    st.markdown("### 🐛 Debug Tools")

    trace_id = st.text_input("Enter Trace ID", placeholder="trace-xxx-xxx")
    if st.button("🔍 Lookup Trace") and trace_id:
        st.session_state.trace_lookup = trace_id

posthog_params = {
    "start_ts": ("TIMESTAMP", start_ts),
    "end_ts": ("TIMESTAMP", end_ts),
}

# Main content tabs
tabs = st.tabs([
    "📊 Overview",
    "🤖 AI Performance",
    "⚡ API Analytics",
    "🔍 Trace Debugger",
    "📡 Telemetry",
    "📈 Product Analytics"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 Developer Overview")
    
    # System health metrics - Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        df = run_query(f"""
            SELECT COUNT(*) as count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty:
            st.metric("Total Requests", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Requests", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT 
                COUNT(*) as total,
                COUNTIF(derived_is_error = TRUE) as errors
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty and df['total'].iloc[0] > 0:
            success_rate = ((df['total'].iloc[0] - df['errors'].iloc[0]) / df['total'].iloc[0] * 100)
            st.metric("Success Rate", f"{success_rate:.2f}%")
        else:
            st.metric("Success Rate", "N/A")
    
    with col3:
        df = run_query(f"""
            SELECT ROUND(AVG(derived_response_time_ms), 2) as avg_latency
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND derived_response_time_ms IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Avg Latency", f"{df['avg_latency'].iloc[0]:.0f}ms")
        else:
            st.metric("Avg Latency", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT SUM(derived_ai_total_tokens) as total_tokens
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_total_tokens IS NOT NULL
        """)
        if df is not None and not df.empty and pd.notna(df['total_tokens'].iloc[0]):
            st.metric("Total Tokens", f"{float(df['total_tokens'].iloc[0]):,.0f}")
        else:
            st.metric("Total Tokens", "N/A")
    
    with col5:
        df = run_query(f"""
            SELECT COUNT(DISTINCT derived_ai_model) as models
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_model IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("AI Models", f"{df['models'].iloc[0]}")
        else:
            st.metric("AI Models", "N/A")
    
    st.markdown("---")
    
    # Performance metrics - Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        df = run_query(f"""
            SELECT ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND derived_response_time_ms IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("P95 Latency", f"{df['p95'].iloc[0]:.0f}ms", 
                     delta="Target: <2000ms", delta_color="inverse")
        else:
            st.metric("P95 Latency", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT COUNT(DISTINCT trace_id) as traces
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND trace_id IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Unique Traces", f"{df['traces'].iloc[0]:,}")
        else:
            st.metric("Unique Traces", "N/A")
    
    with col3:
        df = run_query(f"""
            SELECT COUNT(DISTINCT service_name) as services
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE service_name IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Active Services", f"{df['services'].iloc[0]}")
        else:
            st.metric("Active Services", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT COUNTIF(derived_is_error = TRUE) as errors
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty:
            st.metric("Total Errors", f"{df['errors'].iloc[0]:,}", 
                     delta="0 is ideal", delta_color="inverse")
        else:
            st.metric("Total Errors", "N/A")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Request Volume Over Time")
        df = run_query(f"""
            SELECT 
                TIMESTAMP_TRUNC(created_at, HOUR) as hour,
                COUNT(*) as request_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY hour
            ORDER BY hour
        """)
        if df is not None and not df.empty:
            fig = plot_line_chart(df, 'hour', 'request_count', 'Hourly Request Volume', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No request data available")
    
    with col2:
        st.markdown("### ⚡ Response Time Distribution")
        df = run_query(f"""
            SELECT 
                ROUND(AVG(derived_response_time_ms), 2) as avg_latency,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(50)], 2) as p50,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(99)], 2) as p99
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND derived_response_time_ms IS NOT NULL
        """)
        if df is not None and not df.empty:
            latency_data = pd.DataFrame({
                'Metric': ['Average', 'P50', 'P95', 'P99'],
                'Latency (ms)': [
                    df['avg_latency'].iloc[0],
                    df['p50'].iloc[0],
                    df['p95'].iloc[0],
                    df['p99'].iloc[0]
                ]
            })
            fig = plot_bar_chart(latency_data, 'Metric', 'Latency (ms)', 
                               'Response Time Metrics', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No latency data available")
    
    st.markdown("---")
    
    # Error and success rate trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐛 Error Rate Trend")
        df = run_query(f"""
            SELECT 
                TIMESTAMP_TRUNC(created_at, HOUR) as hour,
                COUNTIF(derived_is_error = TRUE) as errors,
                COUNT(*) as total,
                ROUND(COUNTIF(derived_is_error = TRUE) / COUNT(*) * 100, 2) as error_rate
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY hour
            ORDER BY hour
        """)
        if df is not None and not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['hour'],
                y=df['error_rate'],
                mode='lines+markers',
                name='Error Rate %',
                line=dict(color='#e74c3c', width=2),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.2)'
            ))
            fig.update_layout(
                title='Hourly Error Rate %',
                xaxis_title='Time',
                yaxis_title='Error Rate (%)',
                template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=350,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No error data available")
    
    with col2:
        st.markdown("### 📊 Request Status Codes")
        df = run_query(f"""
            SELECT 
                http_status_code,
                COUNT(*) as count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND http_status_code IS NOT NULL
            GROUP BY http_status_code
            ORDER BY count DESC
            LIMIT 10
        """)
        if df is not None and not df.empty:
            fig = go.Figure(go.Bar(
                x=df['count'],
                y=df['http_status_code'].astype(str),
                orientation='h',
                marker=dict(
                    color=df['count'],
                    colorscale='Blues',
                    showscale=False
                ),
                text=df['count'],
                textposition='outside'
            ))
            fig.update_layout(
                title='Top HTTP Status Codes',
                xaxis_title='Count',
                yaxis_title='Status Code',
                template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=350,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No status code data available")
    
    st.markdown("---")
    
    # Database & Session Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Active User Sessions")
        df = run_query(f"""
            SELECT 
                DATE(start_timestamp) as date,
                COUNT(DISTINCT distinct_id) as unique_users,
                COUNT(*) as total_sessions,
                ROUND(AVG(session_duration_seconds / 60), 2) as avg_duration_min
            FROM `{DATASET_ID}.session_analytics`
            WHERE start_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date
        """)
        if df is not None and not df.empty:
            fig = create_multi_line_chart(
                df, 'date', 
                ['unique_users', 'total_sessions'], 
                'Daily Session Metrics',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No session data available")
    
    with col2:
        st.markdown("### 📝 Grade Submissions Trend")
        df = run_query(f"""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as submissions,
                ROUND(AVG(final_score), 2) as avg_score
            FROM `{DATASET_ID}.grades`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date
        """)
        if df is not None and not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['submissions'],
                name='Submissions',
                marker=dict(color='#3498db')
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['avg_score'],
                name='Avg Score',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#2ecc71', width=3)
            ))
            fig.update_layout(
                title='Daily Grade Submissions & Average Scores',
                xaxis_title='Date',
                yaxis_title='Submissions',
                yaxis2=dict(
                    title='Average Score',
                    overlaying='y',
                    side='right'
                ),
                template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=350,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grade data available")

# TAB 2: AI PERFORMANCE
with tabs[1]:
    st.markdown("## 🤖 AI Performance Analytics")
    
    # Token metrics
    df = run_query(f"""
        SELECT 
            SUM(derived_ai_total_tokens) as total_tokens,
            SUM(derived_ai_input_tokens) as input_tokens,
            SUM(derived_ai_output_tokens) as output_tokens
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE derived_ai_total_tokens IS NOT NULL
    """)
    
    col1, col2, col3 = st.columns(3)
    
    if df is not None and not df.empty and pd.notna(df['total_tokens'].iloc[0]):
        total = float(df['total_tokens'].iloc[0])
        input_tok = float(df['input_tokens'].iloc[0])
        output_tok = float(df['output_tokens'].iloc[0])
        
        with col1:
            st.metric("Input Tokens", f"{input_tok:,.0f}")
        with col2:
            st.metric("Output Tokens", f"{output_tok:,.0f}")
        with col3:
            ratio = output_tok / input_tok if input_tok > 0 else 0
            st.metric("Output/Input Ratio", f"{ratio:.2f}x")
    else:
        with col1:
            st.metric("Input Tokens", "N/A")
        with col2:
            st.metric("Output Tokens", "N/A")
        with col3:
            st.metric("Output/Input Ratio", "N/A")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Model Distribution")
        df = run_query(f"""
            SELECT 
                derived_ai_model as model,
                COUNT(*) as request_count,
                SUM(derived_ai_total_tokens) as total_tokens,
                ROUND(AVG(derived_ai_total_tokens), 2) as avg_tokens
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_model IS NOT NULL
            GROUP BY model
            ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(df, 'model', 'request_count', 'Requests by Model', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No AI model data available")
    
    with col2:
        st.markdown("### 📊 Token Distribution")
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'model', 'total_tokens', 'Token Usage by Model', height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 💰 Cost Estimation")
            total_cost = (df['total_tokens'].sum() / 1_000_000) * 15.0
            st.metric("Estimated Total Cost", f"${total_cost:,.2f}")
            st.caption("Based on $15 per 1M tokens")
        else:
            st.info("No token distribution data available")

# TAB 3: API ANALYTICS
with tabs[2]:
    st.markdown("## ⚡ API Performance Analytics")
    
    # Response time by route
    st.markdown("### 📊 API Route Performance")
    df = run_query(f"""
        SELECT 
            http_route,
            COUNT(*) as request_count,
            ROUND(AVG(derived_response_time_ms), 2) as avg_latency,
            ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95_latency,
            ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(99)], 2) as p99_latency
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE http_route IS NOT NULL
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY http_route
        ORDER BY request_count DESC
        LIMIT 20
    """)
    
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "api_performance.csv", "text/csv")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Request Volume by Route")
            fig = go.Figure(go.Bar(
                x=df.head(10)['request_count'],
                y=df.head(10)['http_route'],
                orientation='h',
                marker=dict(color='#3498db'),
                text=df.head(10)['request_count'],
                textposition='outside'
            ))
            fig.update_layout(
                title='Top Routes by Request Count',
                xaxis_title='Request Count',
                yaxis_title='Route',
                template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ P95 Latency by Route")
            fig = go.Figure(go.Bar(
                x=df.head(10)['p95_latency'],
                y=df.head(10)['http_route'],
                orientation='h',
                marker=dict(color='#e74c3c'),
                text=df.head(10)['p95_latency'].apply(lambda x: f"{int(x)}ms"),
                textposition='outside'
            ))
            
            # Add SLO line at 2000ms
            fig.add_vline(x=2000, line_dash="dash", line_color="yellow",
                         annotation_text="SLO: 2000ms", annotation_position="top right")
            
            fig.update_layout(
                title='P95 Latency by Route',
                xaxis_title='Latency (ms)',
                yaxis_title='Route',
                template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No API performance data available")
    
    st.markdown("---")
    st.markdown("### 🐛 Error Analysis")
    
    df = run_query(f"""
        SELECT 
            http_route,
            http_status_code,
            COUNT(*) as error_count
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE derived_is_error = TRUE
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY http_route, http_status_code
        ORDER BY error_count DESC
        LIMIT 20
    """)
    
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Errors by Route")
            route_errors = df.groupby('http_route')['error_count'].sum().reset_index()
            route_errors = route_errors.sort_values('error_count', ascending=False).head(10)
            
            fig = plot_bar_chart(route_errors, 'http_route', 'error_count',
                               'Errors by Route', orientation='h', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Errors by Status Code")
            status_errors = df.groupby('http_status_code')['error_count'].sum().reset_index()
            
            fig = plot_bar_chart(status_errors, 'http_status_code', 'error_count',
                               'Errors by Status Code', height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No errors in the selected time window!")

# TAB 4: TRACE DEBUGGER
with tabs[3]:
    st.markdown("## 🔍 Request Trace Debugger")
    
    if 'trace_lookup' in st.session_state:
        trace_id = st.session_state.trace_lookup
        
        st.markdown(f"### 📝 Trace: `{trace_id}`")
        
        df = run_query(f"""
            SELECT *
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE trace_id = '{trace_id}'
            ORDER BY start_timestamp
        """)
        
        if df is not None and not df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Spans", len(df))
            with col2:
                if 'derived_response_time_ms' in df.columns:
                    st.metric("Total Time", f"{df['derived_response_time_ms'].sum():.0f}ms")
            with col3:
                if 'derived_is_error' in df.columns:
                    has_error = df['derived_is_error'].any()
                    st.metric("Status", "❌ Error" if has_error else "✅ Success")
            
            st.markdown("---")
            st.markdown("### 🔬 Trace Details")
            st.dataframe(df, use_container_width=True, height=400)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Trace", csv, f"trace_{trace_id}.csv", "text/csv")
        else:
            st.warning(f"No trace found for ID: {trace_id}")
    else:
        st.info("👈 Enter a Trace ID in the sidebar to begin debugging")
        
        st.markdown("### 📚 How to Use")
        st.markdown("""
        1. Enter a `trace_id` in the sidebar
        2. Click **Lookup Trace** to retrieve details
        3. View full request lifecycle and timing
        4. Analyze errors and performance bottlenecks
        5. Export trace data for further analysis
        """)
        
        st.markdown("### 🕐 Recent Traces")
        df = run_query(f"""
            SELECT DISTINCT
                trace_id,
                MIN(created_at) as start_time,
                COUNT(*) as span_count,
                BOOL_OR(derived_is_error) as has_error
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE trace_id IS NOT NULL
                AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
            GROUP BY trace_id
            ORDER BY start_time DESC
            LIMIT 20
        """)
        
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent traces found")

# TAB 5: TELEMETRY
with tabs[4]:
    st.markdown("## 📡 Backend Telemetry")
    
    st.markdown("### 📊 Telemetry Statistics")
    
    df = run_query(f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT trace_id) as unique_traces,
            COUNT(DISTINCT service_name) as services,
            MIN(created_at) as oldest_record,
            MAX(created_at) as newest_record
        FROM `{DATASET_ID}.backend_telemetry`
    """)
    
    if df is not None and not df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Records", f"{df['total_records'].iloc[0]:,}")
        with col2:
            st.metric("Unique Traces", f"{df['unique_traces'].iloc[0]:,}")
        with col3:
            st.metric("Services", f"{df['services'].iloc[0]:,}")
        with col4:
            oldest = pd.to_datetime(df['oldest_record'].iloc[0])
            st.metric("Oldest Record", oldest.strftime('%Y-%m-%d'))
        with col5:
            newest = pd.to_datetime(df['newest_record'].iloc[0])
            st.metric("Newest Record", newest.strftime('%Y-%m-%d'))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Service Distribution")
        df = run_query(f"""
            SELECT 
                service_name,
                COUNT(*) as request_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE service_name IS NOT NULL
            GROUP BY service_name
            ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'service_name', 'request_count',
                               'Requests by Service', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No service data available")
    
    with col2:
        st.markdown("### 🌍 Environment Distribution")
        df = run_query(f"""
            SELECT 
                deployment_environment,
                COUNT(*) as request_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE deployment_environment IS NOT NULL
            GROUP BY deployment_environment
            ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'deployment_environment', 'request_count',
                               'Requests by Environment', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No environment data available")

# TAB 6: PRODUCT ANALYTICS
with tabs[5]:
    st.markdown("## 📈 Product Analytics")

    st.markdown("### Reliability / Errors")
    with st.spinner("Loading exception rate trends..."):
        df_rates = fetch_exception_rate_trends(posthog_params)

    if df_rates is not None and not df_rates.empty:
        df_rates["date"] = pd.to_datetime(df_rates["date"])
        df_rates = df_rates.sort_values("date")
        for col in ["exception_count", "total_events", "exception_rate_percent", "users_with_errors"]:
            df_rates[col] = pd.to_numeric(df_rates[col], errors="coerce").fillna(0)

        total_events = int(df_rates["total_events"].sum())
        total_exceptions = int(df_rates["exception_count"].sum())
        avg_exception_rate = df_rates["exception_rate_percent"].mean()
        users_with_errors = int(df_rates["users_with_errors"].sum())

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Events", f"{total_events:,}")
        with col2:
            st.metric("Exception Count", f"{total_exceptions:,}")
        with col3:
            st.metric("Avg Exception Rate", f"{avg_exception_rate:.2f}%")
        with col4:
            st.metric("Users With Errors", f"{users_with_errors:,}")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(
                df_rates,
                x="date",
                y="exception_rate_percent",
                markers=True,
                labels={"date": "Date", "exception_rate_percent": "Exception Rate (%)"}
            )
            fig = apply_theme_layout(fig, "Exception Rate (%) by Date", "Date", "Exception Rate (%)", height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(
                df_rates,
                x="date",
                y="exception_count",
                markers=True,
                labels={"date": "Date", "exception_count": "Exception Count"}
            )
            fig = apply_theme_layout(fig, "Exception Count by Date", "Date", "Exception Count", height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("#### Users Affected by Errors")
    with st.spinner("Loading users affected by errors..."):
        df_users = fetch_users_affected_by_errors(posthog_params)

    if df_users is not None and not df_users.empty:
        df_users["exception_count"] = pd.to_numeric(df_users["exception_count"], errors="coerce").fillna(0)
        df_users["user_email"] = df_users["user_email"].fillna("Unknown")
        top_users = df_users.sort_values("exception_count", ascending=False).head(20)

        col1, col2 = st.columns([2, 3])
        with col1:
            fig = px.bar(
                top_users,
                x="exception_count",
                y="user_email",
                orientation="h",
                labels={"exception_count": "Exception Count", "user_email": "User Email"}
            )
            fig = apply_theme_layout(fig, "Top 20 Users by Exception Count", "Exception Count", "User Email", height=450)
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(df_users, use_container_width=True, height=450)
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("#### Error Distribution by Type")
    with st.spinner("Loading error distribution..."):
        df_errors = fetch_error_distribution_by_type(posthog_params)

    if df_errors is not None and not df_errors.empty:
        df_errors["occurrence_count"] = pd.to_numeric(df_errors["occurrence_count"], errors="coerce").fillna(0)
        error_summary = (
            df_errors.groupby("error_type", dropna=False)["occurrence_count"]
            .sum()
            .reset_index()
        )
        error_summary["error_type"] = error_summary["error_type"].fillna("Unknown")
        error_summary = error_summary.sort_values("occurrence_count", ascending=False).head(15)

        col1, col2 = st.columns([2, 3])
        with col1:
            fig = px.bar(
                error_summary,
                x="occurrence_count",
                y="error_type",
                orientation="h",
                labels={"occurrence_count": "Occurrences", "error_type": "Error Type"}
            )
            fig = apply_theme_layout(fig, "Top Error Types", "Occurrences", "Error Type", height=450)
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(df_errors, use_container_width=True, height=450)
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("### Performance / Web Vitals")
    with st.spinner("Loading web vitals metrics..."):
        df_vitals = fetch_web_vitals_metrics(posthog_params)

    if df_vitals is not None and not df_vitals.empty:
        df_vitals["date"] = pd.to_datetime(df_vitals["date"])
        df_vitals = df_vitals.sort_values("date")
        numeric_cols = [
            "avg_lcp_seconds",
            "avg_fcp_seconds",
            "avg_inp_ms",
            "avg_cls_score",
            "lcp_good",
            "lcp_needs_improvement",
            "lcp_poor",
            "inp_good",
            "inp_needs_improvement",
            "inp_poor",
        ]
        for col in numeric_cols:
            if col in df_vitals.columns:
                df_vitals[col] = pd.to_numeric(df_vitals[col], errors="coerce").fillna(0)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(
                df_vitals,
                x="date",
                y=["avg_lcp_seconds", "avg_fcp_seconds"],
                markers=True,
                labels={
                    "date": "Date",
                    "value": "Seconds",
                    "variable": "Metric"
                }
            )
            fig = apply_theme_layout(fig, "Average LCP & FCP (Seconds)", "Date", "Seconds", height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(
                df_vitals,
                x="date",
                y=["avg_inp_ms", "avg_cls_score"],
                markers=True,
                labels={
                    "date": "Date",
                    "value": "Value",
                    "variable": "Metric"
                }
            )
            fig = apply_theme_layout(fig, "Average INP (ms) & CLS (score)", "Date", "Value", height=350)
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            lcp_dist = df_vitals.melt(
                id_vars=["date"],
                value_vars=["lcp_good", "lcp_needs_improvement", "lcp_poor"],
                var_name="bucket",
                value_name="count"
            )
            lcp_dist["bucket"] = lcp_dist["bucket"].str.replace("_", " ").str.title()
            fig = px.bar(
                lcp_dist,
                x="date",
                y="count",
                color="bucket",
                barmode="stack",
                labels={"date": "Date", "count": "Events", "bucket": "LCP Bucket"}
            )
            fig = apply_theme_layout(fig, "LCP Distribution by Date", "Date", "Events", height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            inp_dist = df_vitals.melt(
                id_vars=["date"],
                value_vars=["inp_good", "inp_needs_improvement", "inp_poor"],
                var_name="bucket",
                value_name="count"
            )
            inp_dist["bucket"] = inp_dist["bucket"].str.replace("_", " ").str.title()
            fig = px.bar(
                inp_dist,
                x="date",
                y="count",
                color="bucket",
                barmode="stack",
                labels={"date": "Date", "count": "Events", "bucket": "INP Bucket"}
            )
            fig = apply_theme_layout(fig, "INP Distribution by Date", "Date", "Events", height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found for the selected period.")

    st.markdown("#### Performance Percentiles")
    with st.spinner("Loading performance percentiles..."):
        df_percentiles = fetch_performance_percentiles(posthog_params)

    if df_percentiles is not None and not df_percentiles.empty:
        col1, col2 = st.columns([2, 3])
        with col1:
            fig = px.bar(
                df_percentiles,
                x="metric_name",
                y="p95",
                labels={"metric_name": "Metric", "p95": "P95"}
            )
            fig = apply_theme_layout(fig, "P95 by Metric", "Metric", "P95", height=350)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(df_percentiles, use_container_width=True, height=350)
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("### Sessions Quality")
    with st.spinner("Loading error-free session rate..."):
        df_sessions = fetch_error_free_session_rate(posthog_params)

    if df_sessions is not None and not df_sessions.empty:
        row = df_sessions.iloc[0]
        total_sessions = int(row.get("total_sessions", 0))
        sessions_with_errors = int(row.get("sessions_with_errors", 0))
        error_free_sessions = int(row.get("error_free_sessions", 0))
        error_free_rate = float(row.get("error_free_rate_percent", 0))

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Error-Free Rate", f"{error_free_rate:.2f}%")
        with col2:
            st.metric("Total Sessions", f"{total_sessions:,}")
        with col3:
            st.metric("Sessions With Errors", f"{sessions_with_errors:,}")
        with col4:
            st.metric("Error-Free Sessions", f"{error_free_sessions:,}")

        fig = px.pie(
            names=["Error-Free", "With Errors"],
            values=[error_free_sessions, sessions_with_errors],
            hole=0.5
        )
        fig = apply_theme_layout(fig, "Session Error Split", "Session Type", "Sessions", height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("### UX Frustration")
    with st.spinner("Loading rage clicks..."):
        df_rage = fetch_rage_clicks(posthog_params)

    if df_rage is not None and not df_rage.empty:
        df_rage["date"] = pd.to_datetime(df_rage["date"])
        df_rage["rageclick_count"] = pd.to_numeric(df_rage["rageclick_count"], errors="coerce").fillna(0)

        col1, col2 = st.columns([2, 3])
        with col1:
            top_pages = (
                df_rage.groupby("page_url")["rageclick_count"]
                .sum()
                .reset_index()
                .sort_values("rageclick_count", ascending=False)
                .head(20)
            )
            fig = px.bar(
                top_pages,
                x="rageclick_count",
                y="page_url",
                orientation="h",
                labels={"rageclick_count": "Rage Clicks", "page_url": "Page URL"}
            )
            fig = apply_theme_layout(fig, "Top 20 Pages by Rage Clicks", "Rage Clicks", "Page URL", height=450)
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(
                df_rage.sort_values("rageclick_count", ascending=False),
                use_container_width=True,
                height=450
            )

        rage_daily = (
            df_rage.groupby("date")["rageclick_count"]
            .sum()
            .reset_index()
            .sort_values("date")
        )
        fig = px.line(
            rage_daily,
            x="date",
            y="rageclick_count",
            markers=True,
            labels={"date": "Date", "rageclick_count": "Rage Clicks"}
        )
        fig = apply_theme_layout(fig, "Daily Rage Clicks", "Date", "Rage Clicks", height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("### Network")
    with st.spinner("Loading network connectivity issues..."):
        df_network = fetch_network_connectivity(posthog_params)

    if df_network is not None and not df_network.empty:
        df_network["date"] = pd.to_datetime(df_network["date"])
        df_network["status_change_count"] = pd.to_numeric(
            df_network["status_change_count"], errors="coerce"
        ).fillna(0)

        status_trend = (
            df_network.groupby(["date", "network_status"])["status_change_count"]
            .sum()
            .reset_index()
            .sort_values("date")
        )
        fig = px.bar(
            status_trend,
            x="date",
            y="status_change_count",
            color="network_status",
            barmode="stack",
            labels={
                "date": "Date",
                "status_change_count": "Status Changes",
                "network_status": "Network Status"
            }
        )
        fig = apply_theme_layout(fig, "Network Status Changes by Date", "Date", "Status Changes", height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            df_network.sort_values(["date", "status_change_count"], ascending=[True, False]),
            use_container_width=True,
            height=350
        )
    else:
        st.info("No data found for the selected period.")

    st.markdown("---")
    st.markdown("### Logs")
    with st.spinner("Loading application logs..."):
        df_logs = fetch_application_logs(posthog_params)

    if df_logs is not None and not df_logs.empty:
        df_logs["date"] = pd.to_datetime(df_logs["date"])
        df_logs["log_count"] = pd.to_numeric(df_logs["log_count"], errors="coerce").fillna(0)

        log_level_summary = (
            df_logs.groupby("log_level")["log_count"]
            .sum()
            .reset_index()
            .sort_values("log_count", ascending=False)
        )
        fig = px.bar(
            log_level_summary,
            x="log_level",
            y="log_count",
            labels={"log_level": "Log Level", "log_count": "Log Count"}
        )
        fig = apply_theme_layout(fig, "Log Count by Level", "Log Level", "Log Count", height=350)
        st.plotly_chart(fig, use_container_width=True)

        log_trend = (
            df_logs.groupby("date")["log_count"]
            .sum()
            .reset_index()
            .sort_values("date")
        )
        fig = px.line(
            log_trend,
            x="date",
            y="log_count",
            markers=True,
            labels={"date": "Date", "log_count": "Log Count"}
        )
        fig = apply_theme_layout(fig, "Daily Log Volume", "Date", "Log Count", height=300)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            df_logs.sort_values(["date", "log_count"], ascending=[True, False]),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No data found for the selected period.")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developer Dashboard v1.0")
