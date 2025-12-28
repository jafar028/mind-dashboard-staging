"""
Developer Dashboard - COMPLETE STANDALONE VERSION
AI Performance, API Analytics & System Debugging
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account
import plotly.express as px
import plotly.graph_objects as go

# Import auth functions directly
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.auth_handler import require_authentication, show_user_info_sidebar, get_current_user
    from config.auth import can_access_page
except Exception:
    st.error("Import error - please check file structure")
    st.stop()

# Page config
st.set_page_config(
    page_title="Developer Dashboard | MIND Platform",
    page_icon="👨‍💻",
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


# Database connection
@st.cache_resource
def get_db_client():
    """Get BigQuery client"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return bigquery.Client(
            credentials=credentials,
            project=st.secrets["gcp_service_account"]["project_id"],
            location="europe-west3"
        )
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def run_query(sql):
    """Execute query with caching"""
    client = get_db_client()
    if client is None:
        return None
    try:
        return client.query(sql).to_dataframe()
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return None

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

# Header
st.title("👨‍💻 Developer Dashboard")
st.markdown("### AI Performance, API Analytics & System Debugging")
st.markdown("---")

# Filters in sidebar
with st.sidebar:
    st.markdown("### 🔧 Developer Tools")
    
    time_window = st.selectbox(
        "Analysis Window",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
        index=3
    )
    
    time_map = {
        "Last Hour": 1/24,
        "Last 6 Hours": 6/24,
        "Last 24 Hours": 1,
        "Last 7 Days": 7
    }
    days = time_map[time_window]
    
    st.markdown("---")
    st.markdown("### 🐛 Debug Tools")
    
    trace_id = st.text_input("Enter Trace ID", placeholder="trace-xxx-xxx")
    if st.button("🔍 Lookup Trace") and trace_id:
        st.session_state.trace_lookup = trace_id

# Main content tabs
tabs = st.tabs([
    "📊 Overview",
    "🤖 AI Performance",
    "⚡ API Analytics",
    "🔍 Trace Debugger",
    "📡 Telemetry"
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

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developer Dashboard v1.0")
