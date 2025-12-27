"""
Admin Dashboard - FIXED FOR BIGQUERY
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

# Display logo if available (fails silently if not)
try:
    from utils.logo_handler import display_logo
    display_logo("sidebar", width=180)
except Exception:
    # Logo not available - continue without it
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
    
    # Get metrics - Using correct table: "user" not "users"
    with col1:
        df = run_query(f"SELECT COUNT(DISTINCT user_id) as count FROM `{DATASET_ID}.user`")
        if df is not None and not df.empty:
            st.metric("Total Users", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Users", "N/A")
    
    with col2:
        # Note: sessions table might use 'user_email' instead of 'user_id'
        df = run_query(f"""
            SELECT COUNT(DISTINCT user_email) as count 
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
                COUNT(DISTINCT user_email) as active_users
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
    
    # Charts row 2 - Case Study Engagement
    st.markdown("---")
    st.markdown("### 🎯 Case Study Engagement: Total Completions")
    df = run_query(f"""
        SELECT 
            c.title as case_study,
            COUNT(g._id) as completions
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        GROUP BY c.title
        ORDER BY completions DESC
    """)
    if df is not None and not df.empty:
        # Horizontal bar chart with data labels
        fig = go.Figure(go.Bar(
            x=df['completions'],
            y=df['case_study'],
            orientation='h',
            marker=dict(
                color=df['completions'],
                colorscale='Tealgrn',
                showscale=False
            ),
            text=df['completions'],
            textposition='outside',
            textfont=dict(size=12, color='white')
        ))
        
        fig.update_layout(
            title='Case Study Engagement: Total Completions',
            xaxis_title='Number of Graded Attempts',
            yaxis_title='Case Study Title',
            template='plotly_dark',
            plot_bgcolor='#262730',
            paper_bgcolor='#0E1117',
            font=dict(color='#FAFAFA'),
            height=500,
            yaxis={'categoryorder': 'total ascending'}  # Sort by value
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No case study data available")
    
    # Charts row 3 - Session Engagement
    st.markdown("---")
    st.markdown("### 📱 Session Engagement Metrics")
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
                                     'Session Engagement Metrics', height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No engagement data available")
    
    # Charts row 3 - NEW CHARTS FROM NOTEBOOK
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Platform Growth & Retention: Weekly Active Users")
        df = run_query(f"""
            WITH user_first_appearance AS (
                SELECT 
                    distinct_id, 
                    MIN(TIMESTAMP_TRUNC(start_timestamp, WEEK)) as join_week
                FROM `{DATASET_ID}.session_analytics`
                GROUP BY 1
            ),
            weekly_usage AS (
                SELECT 
                    TIMESTAMP_TRUNC(s.start_timestamp, WEEK) as activity_week,
                    s.distinct_id,
                    f.join_week
                FROM `{DATASET_ID}.session_analytics` s
                JOIN user_first_appearance f ON s.distinct_id = f.distinct_id
            ),
            growth_metrics AS (
                SELECT 
                    activity_week,
                    COUNT(DISTINCT CASE WHEN activity_week = join_week THEN distinct_id END) as new_signups,
                    COUNT(DISTINCT CASE WHEN activity_week > join_week THEN distinct_id END) as returning_users
                FROM weekly_usage
                GROUP BY 1
            )
            SELECT * FROM growth_metrics ORDER BY activity_week
        """)
        
        if df is not None and not df.empty:
            fig = go.Figure()
            
            # New Signups line
            fig.add_trace(go.Scatter(
                x=df['activity_week'],
                y=df['new_signups'],
                name='New Signups',
                mode='lines+markers',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8, symbol='circle'),
                fill='tonexty',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ))
            
            # Returning Users line
            fig.add_trace(go.Scatter(
                x=df['activity_week'],
                y=df['returning_users'],
                name='Returning Users',
                mode='lines+markers',
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=8, symbol='square'),
                fill='tonexty',
                fillcolor='rgba(46, 204, 113, 0.1)'
            ))
            
            fig.update_layout(
                title='Platform Growth & Retention: Weekly Active User Breakdown',
                xaxis_title='Week',
                yaxis_title='Number of Unique Users',
                template='plotly_dark',
                plot_bgcolor='#262730',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No growth data available")
    
    with col2:
        st.markdown("### 📊 Case Study Activity: Weekly Volume")
        df = run_query(f"""
            SELECT 
                TIMESTAMP_TRUNC(timestamp, WEEK) as week_start,
                COUNT(*) as attempt_count
            FROM `{DATASET_ID}.grades`
            GROUP BY 1
            ORDER BY week_start ASC
        """)
        
        if df is not None and not df.empty:
            # Add sequential week numbers
            df['week_num'] = range(1, len(df) + 1)
            
            fig = go.Figure(go.Bar(
                x=df['week_num'],
                y=df['attempt_count'],
                marker=dict(color='#3498db'),
                text=df['attempt_count'],
                textposition='outside',
                textfont=dict(size=10, color='#FAFAFA'),
                hovertemplate='<b>Week %{x}</b><br>Attempts: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Case Study Activity: Weekly Volume',
                xaxis_title='Week Number',
                yaxis_title='Total Attempts',
                template='plotly_dark',
                plot_bgcolor='#262730',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                height=400,
                bargap=0.1
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No weekly activity data available")

# TAB 2: USER ANALYTICS
with tabs[1]:
    st.markdown("## 👥 User Analytics")
    
    # User stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        df = run_query(f"SELECT COUNT(*) as count FROM `{DATASET_ID}.user`")
        if df is not None and not df.empty:
            st.metric("Total Users", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Users", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT COUNT(DISTINCT role) as roles 
            FROM `{DATASET_ID}.user` 
            WHERE role IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("User Roles", f"{df['roles'].iloc[0]}")
        else:
            st.metric("User Roles", "N/A")
    
    with col3:
        df = run_query(f"""
            SELECT COUNT(DISTINCT department) as depts 
            FROM `{DATASET_ID}.user` 
            WHERE department IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Departments", f"{df['depts'].iloc[0]}")
        else:
            st.metric("Departments", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT COUNT(DISTINCT u.user_id) as active_students
            FROM `{DATASET_ID}.user` u
            JOIN `{DATASET_ID}.grades` g ON u.user_id = g.user
            WHERE g.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        """)
        if df is not None and not df.empty:
            st.metric("Active Students (30d)", f"{df['active_students'].iloc[0]:,}")
        else:
            st.metric("Active Students (30d)", "N/A")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Performance by Department")
        df = run_query(f"""
            SELECT 
                u.department,
                COUNT(DISTINCT u.user_id) as student_count,
                COUNT(g._id) as total_attempts,
                ROUND(AVG(g.final_score), 2) as avg_score,
                ROUND(MIN(g.final_score), 2) as min_score,
                ROUND(MAX(g.final_score), 2) as max_score
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE u.department IS NOT NULL AND g.final_score IS NOT NULL
            GROUP BY u.department
            ORDER BY avg_score DESC
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(df, 'department', 'avg_score', 
                               'Average Score by Department', height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "department_performance.csv", "text/csv")
        else:
            st.info("No department data available")
    
    with col2:
        st.markdown("### 📊 Performance by Role")
        df = run_query(f"""
            SELECT 
                u.role,
                COUNT(DISTINCT u.user_id) as user_count,
                COUNT(g._id) as total_attempts,
                ROUND(AVG(g.final_score), 2) as avg_score,
                ROUND(MIN(g.final_score), 2) as min_score,
                ROUND(MAX(g.final_score), 2) as max_score
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE u.role IS NOT NULL AND g.final_score IS NOT NULL
            GROUP BY u.role
            ORDER BY avg_score DESC
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(df, 'role', 'avg_score', 
                               'Average Score by Role', height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "role_performance.csv", "text/csv")
        else:
            st.info("No role data available")
    
    st.markdown("---")
    st.markdown("### 📋 All Student Performance")
    
    # Search and filters
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("🔍 Search by Name or Email", "")
    with col2:
        dept_filter = st.selectbox("Filter by Department", ["All"] + [
            dept for dept in run_query(f"SELECT DISTINCT department FROM `{DATASET_ID}.user` WHERE department IS NOT NULL ORDER BY department")['department'].tolist()
        ] if run_query(f"SELECT DISTINCT department FROM `{DATASET_ID}.user` WHERE department IS NOT NULL") is not None else ["All"])
    
    # Build query with filters
    where_clauses = ["g.final_score IS NOT NULL"]
    if search_name:
        where_clauses.append(f"(LOWER(u.name) LIKE '%{search_name.lower()}%' OR LOWER(u.student_email) LIKE '%{search_name.lower()}%')")
    if dept_filter != "All":
        where_clauses.append(f"u.department = '{dept_filter}'")
    
    where_clause = " AND ".join(where_clauses)
    
    df = run_query(f"""
        SELECT 
            u.name as student_name,
            u.student_email,
            u.department,
            u.role,
            COUNT(g._id) as total_attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(MIN(g.final_score), 2) as min_score,
            ROUND(MAX(g.final_score), 2) as max_score,
            MAX(g.timestamp) as last_attempt
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
        WHERE {where_clause}
        GROUP BY u.user_id, u.name, u.student_email, u.department, u.role
        ORDER BY avg_score DESC
    """)
    
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Report", csv, "student_performance.csv", "text/csv")
        
        st.info(f"**{len(df)} students** found")
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
            ROUND(MIN(final_score), 2) as min_grade,
            ROUND(MAX(final_score), 2) as max_grade,
            COUNT(*) as total_grades
        FROM `{DATASET_ID}.grades`
        WHERE final_score IS NOT NULL
    """)
    
    if df is not None and not df.empty:
        with col1:
            st.metric("Average Score", f"{df['avg_grade'].iloc[0]:.1f}%")
        with col2:
            st.metric("Minimum Score", f"{df['min_grade'].iloc[0]:.1f}%")
        with col3:
            st.metric("Maximum Score", f"{df['max_grade'].iloc[0]:.1f}%")
        with col4:
            st.metric("Total Grades", f"{df['total_grades'].iloc[0]:,}")
    
    st.markdown("---")
    
    # NEW CHART: Institutional Performance Score Ranges
    st.markdown("### 📊 Institutional Performance: Effective Score Ranges")
    df = run_query(f"""
        SELECT 
            c.title, 
            MIN(CASE WHEN g.final_score > 0 THEN g.final_score END) as min_score,
            AVG(g.final_score) as avg_score,
            MAX(g.final_score) as max_score
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        GROUP BY 1
        HAVING min_score IS NOT NULL
        ORDER BY avg_score DESC
    """)
    
    if df is not None and not df.empty:
        # Create grouped bar chart with Min, Avg, Max
        fig = go.Figure()
        
        # Add bars for each metric
        fig.add_trace(go.Bar(
            name='Min (Non-Zero)',
            x=df['min_score'],
            y=df['title'],
            orientation='h',
            marker=dict(color='#e67e22'),
            text=df['min_score'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            textfont=dict(size=10)
        ))
        
        fig.add_trace(go.Bar(
            name='Average',
            x=df['avg_score'],
            y=df['title'],
            orientation='h',
            marker=dict(color='#3498db'),
            text=df['avg_score'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            textfont=dict(size=10)
        ))
        
        fig.add_trace(go.Bar(
            name='Maximum',
            x=df['max_score'],
            y=df['title'],
            orientation='h',
            marker=dict(color='#2ecc71'),
            text=df['max_score'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            textfont=dict(size=10)
        ))
        
        fig.update_layout(
            title='Institutional Performance: Effective Score Ranges',
            xaxis_title='Score (%)',
            yaxis_title='Case Study',
            barmode='group',
            template='plotly_dark',
            plot_bgcolor='#262730',
            paper_bgcolor='#0E1117',
            font=dict(color='#FAFAFA'),
            height=max(400, len(df) * 50),  # Dynamic height based on number of case studies
            xaxis=dict(range=[0, 115]),
            yaxis={'categoryorder': 'total ascending'},
            legend=dict(
                title='Score Metric',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        **Chart Explanation:**
        - 🟠 **Min (Non-Zero)**: Lowest passing score achieved
        - 🔵 **Average**: Mean score across all attempts
        - 🟢 **Maximum**: Highest score achieved
        
        This visualization helps identify performance ranges and outliers across case studies.
        """)
    else:
        st.info("No score data available")
    
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
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
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
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
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
    
    # FIXED: Check for None/NaN values properly
    if df is not None and not df.empty and pd.notna(df['total_tokens'].iloc[0]):
        total = float(df['total_tokens'].iloc[0])
        cost = (total / 1_000_000) * 15.0
        
        with col1:
            st.metric("Total Tokens", f"{total:,.0f}")
        with col2:
            st.metric("Input Tokens", f"{float(df['input_tokens'].iloc[0]):,.0f}")
        with col3:
            st.metric("Output Tokens", f"{float(df['output_tokens'].iloc[0]):,.0f}")
        with col4:
            st.metric("Estimated Cost", f"${cost:,.2f}")
    else:
        with col1:
            st.metric("Total Tokens", "N/A")
        with col2:
            st.metric("Input Tokens", "N/A")
        with col3:
            st.metric("Output Tokens", "N/A")
        with col4:
            st.metric("Estimated Cost", "N/A")
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
