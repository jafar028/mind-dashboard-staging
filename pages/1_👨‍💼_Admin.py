"""
Admin Dashboard - COMPLETE STANDALONE VERSION
System Health, User Management & Governance Analytics
"""

import streamlit as st
import pandas as pd
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
except:
    st.error("Import error - please check file structure")
    st.stop()

# Page config
st.set_page_config(
    page_title="Admin Dashboard | MIND Platform",
    page_icon="👨‍💼",
    layout="wide"
)

# Authentication
require_authentication()
user = get_current_user()
if not can_access_page(user['role'], 'Admin'):
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

# Sidebar
show_user_info_sidebar()

# Display logo if available
try:
    from utils.logo_handler import display_logo
    display_logo("sidebar", width=180)
except:
    pass

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
def plot_line_chart(df, x, y, title, height=400):
    fig = px.line(df, x=x, y=y, title=title, template='plotly_dark', height=height)
    fig.update_layout(plot_bgcolor='#262730', paper_bgcolor='#0E1117', font=dict(color='#FAFAFA'), hovermode='x unified')
    return fig

def plot_bar_chart(df, x, y, title, orientation='v', height=400):
    fig = px.bar(df, x=x, y=y, title=title, template='plotly_dark', orientation=orientation, height=height)
    fig.update_layout(plot_bgcolor='#262730', paper_bgcolor='#0E1117', font=dict(color='#FAFAFA'))
    return fig

def plot_pie_chart(df, values, names, title, height=400):
    fig = px.pie(df, values=values, names=names, title=title, template='plotly_dark', height=height, hole=0.4)
    fig.update_layout(plot_bgcolor='#262730', paper_bgcolor='#0E1117', font=dict(color='#FAFAFA'))
    return fig

def plot_gauge(value, title, max_value=100, height=300):
    if value >= 80:
        color = '#2ECC71'
    elif value >= 60:
        color = '#F39C12'
    else:
        color = '#E74C3C'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': color},
            'bgcolor': '#262730',
            'steps': [
                {'range': [0, 60], 'color': 'rgba(231, 76, 60, 0.2)'},
                {'range': [60, 80], 'color': 'rgba(243, 156, 18, 0.2)'},
                {'range': [80, max_value], 'color': 'rgba(46, 204, 113, 0.2)'}
            ]
        }
    ))
    fig.update_layout(template='plotly_dark', plot_bgcolor='#262730', paper_bgcolor='#0E1117', 
                     font=dict(color='#FAFAFA'), height=height)
    return fig

def create_multi_line_chart(df, x, y_columns, title, height=400):
    fig = go.Figure()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#3498DB']
    for idx, col in enumerate(y_columns):
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=col, mode='lines+markers', 
                                line=dict(color=colors[idx % len(colors)])))
    fig.update_layout(title=title, template='plotly_dark', plot_bgcolor='#262730', 
                     paper_bgcolor='#0E1117', font=dict(color='#FAFAFA'), 
                     hovermode='x unified', height=height)
    return fig

# Header
st.title("👨‍💼 Admin Dashboard")
st.markdown("### System Health, Governance & Resource Management")
st.markdown("---")

# Filters in sidebar
with st.sidebar:
    st.markdown("### 📊 Filters")
    
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=1
    )
    
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "All Time": 9999
    }
    days = days_map[date_range]
    
    st.markdown("---")
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    if auto_refresh:
        st.rerun()

# Main content tabs
tabs = st.tabs([
    "📊 Overview",
    "👥 User Analytics",
    "🎓 Learning Metrics",
    "🤖 AI Resources",
    "🏥 System Health",
    "⚙️ Settings"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 Executive Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get metrics
    with col1:
        df = run_query(f"SELECT COUNT(DISTINCT user_id) as count FROM `{DATASET_ID}.user`")
        if df is not None and not df.empty:
            st.metric("Total Users", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Users", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT COUNT(DISTINCT user_id) as count 
            FROM `{DATASET_ID}.sessions`
            WHERE start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty:
            st.metric(f"Active Users ({date_range})", f"{df['count'].iloc[0]:,}")
        else:
            st.metric(f"Active Users ({date_range})", "N/A")
    
    with col3:
        df = run_query(f"SELECT COUNT(*) as count FROM `{DATASET_ID}.sessions`")
        if df is not None and not df.empty:
            st.metric("Total Sessions", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Sessions", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT ROUND(AVG(final_score), 1) as avg_score 
            FROM `{DATASET_ID}.grades`
            WHERE final_score IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Average Grade", f"{df['avg_score'].iloc[0]}%")
        else:
            st.metric("Average Grade", "N/A")
    
    with col5:
        df = run_query(f"""
            SELECT 
                COUNT(*) as total_requests,
                COUNTIF(derived_is_error = TRUE) as error_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        """)
        if df is not None and not df.empty and df['total_requests'].iloc[0] > 0:
            error_rate = (df['error_count'].iloc[0] / df['total_requests'].iloc[0] * 100)
            st.metric("Error Rate", f"{error_rate:.2f}%", delta=f"-{error_rate:.1f}%" if error_rate < 5 else None)
        else:
            st.metric("Error Rate", "N/A")
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Daily Active Users Trend")
        df = run_query(f"""
            SELECT 
                DATE(start_time) as date,
                COUNT(DISTINCT user_id) as active_users
            FROM `{DATASET_ID}.sessions`
            WHERE start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY date
            ORDER BY date
        """)
        if df is not None and not df.empty:
            fig = plot_line_chart(df, 'date', 'active_users', 'Daily Active Users', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No user activity data available")
    
    with col2:
        st.markdown("### 📊 Grade Distribution")
        df = run_query(f"""
            SELECT 
                CASE 
                    WHEN final_score >= 90 THEN 'A (90-100)'
                    WHEN final_score >= 80 THEN 'B (80-89)'
                    WHEN final_score >= 70 THEN 'C (70-79)'
                    WHEN final_score >= 60 THEN 'D (60-69)'
                    ELSE 'F (Below 60)'
                END as grade_bracket,
                COUNT(*) as count
            FROM `{DATASET_ID}.grades`
            WHERE final_score IS NOT NULL
            GROUP BY grade_bracket
            ORDER BY grade_bracket
        """)
        if df is not None and not df.empty:
            fig = plot_pie_chart(df, 'count', 'grade_bracket', 'Student Grade Distribution', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grade data available")
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Case Study Performance")
        df = run_query(f"""
            SELECT 
                c.title as case_study,
                ROUND(AVG(g.final_score), 2) as avg_score,
                COUNT(DISTINCT g.user_id) as students
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.casestudy` c ON g.case_study_id = c.case_study_id
            WHERE g.final_score IS NOT NULL
            GROUP BY c.title
            ORDER BY avg_score DESC
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'case_study', 'avg_score', 'Average Score by Case Study', orientation='h', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No case study data available")
    
    with col2:
        st.markdown("### 📱 Session Engagement")
        df = run_query(f"""
            SELECT 
                DATE(start_timestamp) as date,
                ROUND(AVG(session_duration_seconds / 60.0), 2) as avg_duration_minutes,
                ROUND(AVG(pageview_count), 2) as avg_pageviews
            FROM `{DATASET_ID}.session_analytics`
            WHERE start_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date
        """)
        if df is not None and not df.empty:
            fig = create_multi_line_chart(df, 'date', ['avg_duration_minutes', 'avg_pageviews'], 
                                         'Session Engagement Metrics', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No engagement data available")

# TAB 2: USER ANALYTICS
with tabs[1]:
    st.markdown("## 👥 User Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Performance by Cohort")
        df = run_query(f"""
            SELECT 
                u.cohort,
                COUNT(DISTINCT u.user_id) as total_students,
                ROUND(AVG(g.final_score), 2) as avg_score,
                ROUND(AVG(g.communication), 2) as avg_communication
            FROM `{DATASET_ID}.user` u
            LEFT JOIN `{DATASET_ID}.grades` g ON u.user_id = g.user_id
            WHERE u.cohort IS NOT NULL
            GROUP BY u.cohort
            ORDER BY u.cohort
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "cohort_performance.csv", "text/csv")
        else:
            st.info("No cohort data available")
    
    with col2:
        st.markdown("### 📊 Performance by Department")
        df = run_query(f"""
            SELECT 
                u.department,
                COUNT(DISTINCT u.user_id) as total_students,
                ROUND(AVG(g.final_score), 2) as avg_score,
                ROUND(AVG(g.comprehension), 2) as avg_comprehension
            FROM `{DATASET_ID}.user` u
            LEFT JOIN `{DATASET_ID}.grades` g ON u.user_id = g.user_id
            WHERE u.department IS NOT NULL
            GROUP BY u.department
            ORDER BY u.department
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "department_performance.csv", "text/csv")
        else:
            st.info("No department data available")
    
    st.markdown("---")
    st.markdown("### 📋 All Student Performance")
    
    df = run_query(f"""
        SELECT 
            u.name as student_name,
            u.student_email,
            u.department,
            u.cohort,
            COUNT(DISTINCT g.conversation_id) as attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(AVG(g.communication), 2) as avg_communication,
            ROUND(AVG(g.comprehension), 2) as avg_comprehension,
            ROUND(AVG(g.critical_thinking), 2) as avg_critical_thinking
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.user` u ON g.user_id = u.user_id
        WHERE g.final_score IS NOT NULL
        GROUP BY u.name, u.student_email, u.department, u.cohort
        ORDER BY avg_score DESC
    """)
    
    if df is not None and not df.empty:
        search = st.text_input("🔍 Search students", placeholder="Enter name or email")
        
        if search:
            filtered_df = df[
                df['student_name'].str.contains(search, case=False, na=False) |
                df['student_email'].str.contains(search, case=False, na=False)
            ]
        else:
            filtered_df = df
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "student_performance.csv", "text/csv")
    else:
        st.info("No student performance data available")

# TAB 3: LEARNING METRICS
with tabs[2]:
    st.markdown("## 🎓 Learning Analytics")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    df = run_query(f"""
        SELECT 
            ROUND(AVG(final_score), 2) as avg_grade,
            ROUND(AVG(communication), 2) as avg_communication,
            ROUND(AVG(comprehension), 2) as avg_comprehension,
            ROUND(AVG(critical_thinking), 2) as avg_critical_thinking
        FROM `{DATASET_ID}.grades`
        WHERE final_score IS NOT NULL
    """)
    
    if df is not None and not df.empty:
        with col1:
            st.metric("Avg Communication", f"{df['avg_communication'].iloc[0]:.1f}%")
        with col2:
            st.metric("Avg Comprehension", f"{df['avg_comprehension'].iloc[0]:.1f}%")
        with col3:
            st.metric("Avg Critical Thinking", f"{df['avg_critical_thinking'].iloc[0]:.1f}%")
        with col4:
            st.metric("Overall Average", f"{df['avg_grade'].iloc[0]:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ Students at Risk")
        df = run_query(f"""
            SELECT 
                u.name as student_name,
                u.student_email,
                u.department,
                u.cohort,
                ROUND(AVG(g.final_score), 2) as avg_score,
                COUNT(*) as attempts
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user_id = u.user_id
            WHERE g.final_score IS NOT NULL
            GROUP BY u.user_id, u.name, u.student_email, u.department, u.cohort
            HAVING avg_score < 60
            ORDER BY avg_score ASC
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=400)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "students_at_risk.csv", "text/csv")
            st.warning(f"**{len(df)} students** are currently below 60% average")
        else:
            st.success("✅ No students at risk!")
    
    with col2:
        st.markdown("### 🏆 Top Performers")
        df = run_query(f"""
            SELECT 
                u.name as student_name,
                u.student_email,
                ROUND(AVG(g.final_score), 2) as avg_score,
                COUNT(*) as attempts
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user_id = u.user_id
            WHERE g.final_score IS NOT NULL
            GROUP BY u.user_id, u.name, u.student_email
            ORDER BY avg_score DESC
            LIMIT 10
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=400)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "top_performers.csv", "text/csv")
        else:
            st.info("No performance data available")

# TAB 4: AI RESOURCES
with tabs[3]:
    st.markdown("## 🤖 AI Resource Management")
    
    df = run_query(f"""
        SELECT 
            SUM(derived_ai_total_tokens) as total_tokens,
            SUM(derived_ai_input_tokens) as input_tokens,
            SUM(derived_ai_output_tokens) as output_tokens,
            COUNT(DISTINCT derived_ai_model) as models_used
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE derived_ai_total_tokens IS NOT NULL
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    if df is not None and not df.empty and df['total_tokens'].iloc[0]:
        total = df['total_tokens'].iloc[0]
        cost = (total / 1_000_000) * 15.0
        
        with col1:
            st.metric("Total Tokens", f"{total:,.0f}")
        with col2:
            st.metric("Input Tokens", f"{df['input_tokens'].iloc[0]:,.0f}")
        with col3:
            st.metric("Output Tokens", f"{df['output_tokens'].iloc[0]:,.0f}")
        with col4:
            st.metric("Estimated Cost", f"${cost:,.2f}")
    else:
        st.info("No AI usage data available")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 AI Model Distribution")
        df = run_query(f"""
            SELECT 
                derived_ai_model as model,
                COUNT(*) as request_count,
                SUM(derived_ai_total_tokens) as total_tokens
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_model IS NOT NULL
            GROUP BY model
            ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'model', 'request_count', 'Requests by AI Model', height=350)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No AI model data available")
    
    with col2:
        st.markdown("### 💰 Token Usage Over Time")
        st.info("Token usage trending chart - data pending")

# TAB 5: SYSTEM HEALTH
with tabs[4]:
    st.markdown("## 🏥 System Health & Performance")
    
    df = run_query(f"""
        SELECT 
            COUNT(*) as total_requests,
            COUNTIF(derived_is_error = TRUE) as error_count,
            ROUND(AVG(derived_response_time_ms), 2) as avg_response_time,
            ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95_latency,
            ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(99)], 2) as p99_latency
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """)
    
    if df is not None and not df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Requests", f"{df['total_requests'].iloc[0]:,}")
        with col2:
            st.metric("Error Count", f"{df['error_count'].iloc[0]:,}")
        with col3:
            st.metric("Avg Latency", f"{df['avg_response_time'].iloc[0]:.0f}ms")
        with col4:
            st.metric("P95 Latency", f"{df['p95_latency'].iloc[0]:.0f}ms")
        with col5:
            st.metric("P99 Latency", f"{df['p99_latency'].iloc[0]:.0f}ms")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚦 System Uptime")
        if df is not None and not df.empty and df['total_requests'].iloc[0] > 0:
            uptime = ((df['total_requests'].iloc[0] - df['error_count'].iloc[0]) / 
                     df['total_requests'].iloc[0] * 100)
            fig = plot_gauge(uptime, "System Uptime %", max_value=100, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No uptime data available")
    
    with col2:
        st.markdown("### ⚡ Response Time by Route")
        df = run_query(f"""
            SELECT 
                http_route,
                COUNT(*) as request_count,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95_latency
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE http_route IS NOT NULL
                AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            GROUP BY http_route
            ORDER BY request_count DESC
            LIMIT 10
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'http_route', 'p95_latency', 'P95 Latency by API Route', orientation='h', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No route performance data available")
    
    st.markdown("---")
    st.markdown("### 🐛 Recent Errors")
    
    df = run_query(f"""
        SELECT 
            created_at,
            span_name,
            http_route,
            http_status_code,
            derived_response_time_ms,
            service_name
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE derived_is_error = TRUE
        ORDER BY created_at DESC
        LIMIT 50
    """)
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "error_log.csv", "text/csv")
    else:
        st.success("✅ No recent errors!")

# TAB 6: SETTINGS
with tabs[5]:
    st.markdown("## ⚙️ System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Access Control")
        st.info("""
        **User Roles:**
        - Admin: Full system access
        - Developer: Technical metrics & debugging
        - Faculty: Academic analytics
        - Student: Personal performance
        """)
        
        if st.button("👥 Manage Users"):
            st.info("User management interface - Coming soon")
    
    with col2:
        st.markdown("### 📊 Data Settings")
        
        cache_ttl = st.number_input("Cache TTL (seconds)", min_value=60, max_value=3600, value=3600)
        
        if st.button("🔄 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")
        
        st.markdown("### 📥 Data Export")
        if st.button("📦 Export All Data"):
            st.info("Full data export - Coming soon")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Admin Dashboard v1.0")
