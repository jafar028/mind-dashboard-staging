"""
Faculty Dashboard - COMPLETE STANDALONE VERSION
Academic Insights, Student Performance & Learning Analytics
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
except Exception:
    st.error("Import error - please check file structure")
    st.stop()

# Page config
st.set_page_config(
    page_title="Faculty Dashboard | MIND Platform",
    page_icon="👩‍🏫",
    layout="wide"
)

# Authentication
require_authentication()
user = get_current_user()
if not can_access_page(user['role'], 'Faculty'):
    st.error("⛔ Access Denied: Faculty privileges required")
    st.stop()

# Sidebar
show_user_info_sidebar()

# Display logo if available
try:
    # Direct path to logo (confirmed from diagnostics)
    LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_dark.png"
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=180)
except Exception:
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
def plot_bar_chart(df, x, y, title, orientation='v', height=400):
    fig = px.bar(df, x=x, y=y, title=title, template='plotly_dark', orientation=orientation, height=height)
    fig.update_layout(plot_bgcolor='#262730', paper_bgcolor='#0E1117', font=dict(color='#FAFAFA'))
    return fig

def plot_line_chart(df, x, y, title, height=400):
    fig = px.line(df, x=x, y=y, title=title, template='plotly_dark', height=height)
    fig.update_layout(plot_bgcolor='#262730', paper_bgcolor='#0E1117', font=dict(color='#FAFAFA'), hovermode='x unified')
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
st.title("👩‍🏫 Faculty Dashboard")
st.markdown("### Academic Insights & Learning Analytics")
st.markdown("---")

# Filters in sidebar
with st.sidebar:
    st.markdown("### 📊 Filters")
    
    # Department filter
    dept_df = run_query(f"""
        SELECT DISTINCT department 
        FROM `{DATASET_ID}.user` 
        WHERE department IS NOT NULL 
        ORDER BY department
    """)
    departments = ['All'] + (dept_df['department'].tolist() if dept_df is not None and not dept_df.empty else [])
    selected_dept = st.selectbox("Filter by Department", departments)
    
    # Risk threshold
    st.markdown("---")
    risk_threshold = st.slider("At-Risk Threshold (%)", 0, 100, 60, 
                               help="Students below this score are flagged as at-risk")
    
    # Time range
    st.markdown("---")
    time_range = st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"], index=1)
    
    time_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "All Time": 36500
    }
    days = time_map[time_range]

# Main content tabs
tabs = st.tabs([
    "📊 Overview",
    "👥 Student Performance",
    "📚 Case Study Analytics",
    "⚠️ At-Risk Students",
    "📈 Progress Tracking",
    "🎯 Individual Student"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 Academic Overview")
    
    # Build department filter
    dept_where = f"AND u.department = '{selected_dept}'" if selected_dept != 'All' else ""
    
    # KPIs Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        df = run_query(f"""
            SELECT COUNT(DISTINCT u.user_id) as count
            FROM `{DATASET_ID}.user` u
            JOIN `{DATASET_ID}.grades` g ON u.user_id = g.user
            WHERE 1=1 {dept_where}
        """)
        if df is not None and not df.empty:
            st.metric("Total Students", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Students", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT COUNT(*) as count
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            {dept_where}
        """)
        if df is not None and not df.empty:
            st.metric("Total Submissions", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Submissions", "N/A")
    
    with col3:
        df = run_query(f"""
            SELECT ROUND(AVG(g.final_score), 2) as avg_score
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL {dept_where}
        """)
        if df is not None and not df.empty:
            st.metric("Class Average", f"{df['avg_score'].iloc[0]:.1f}%")
        else:
            st.metric("Class Average", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT COUNT(DISTINCT u.user_id) as at_risk
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL {dept_where}
            GROUP BY u.user_id
            HAVING AVG(g.final_score) < {risk_threshold}
        """)
        if df is not None and not df.empty:
            st.metric("At-Risk Students", f"{df['at_risk'].sum():,}", 
                     delta=f"< {risk_threshold}%", delta_color="inverse")
        else:
            st.metric("At-Risk Students", "0")
    
    with col5:
        df = run_query(f"""
            SELECT COUNT(DISTINCT c.case_study_id) as cases
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE 1=1 {dept_where}
        """)
        if df is not None and not df.empty:
            st.metric("Active Case Studies", f"{df['cases'].iloc[0]}")
        else:
            st.metric("Active Case Studies", "N/A")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Grade Distribution")
        df = run_query(f"""
            SELECT 
                CASE 
                    WHEN final_score >= 90 THEN 'A (90-100)'
                    WHEN final_score >= 80 THEN 'B (80-89)'
                    WHEN final_score >= 70 THEN 'C (70-79)'
                    WHEN final_score >= 60 THEN 'D (60-69)'
                    ELSE 'F (<60)'
                END as grade,
                COUNT(*) as count
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL {dept_where}
            GROUP BY grade
            ORDER BY grade
        """)
        if df is not None and not df.empty:
            # Ensure all grades are present
            all_grades = ['A (90-100)', 'B (80-89)', 'C (70-79)', 'D (60-69)', 'F (<60)']
            for grade in all_grades:
                if grade not in df['grade'].values:
                    df = pd.concat([df, pd.DataFrame({'grade': [grade], 'count': [0]})], ignore_index=True)
            
            df = df.sort_values('grade')
            
            colors = ['#2ecc71', '#3498db', '#f39c12', '#e67e22', '#e74c3c']
            fig = go.Figure(go.Bar(
                x=df['count'],
                y=df['grade'],
                orientation='h',
                marker=dict(color=colors),
                text=df['count'],
                textposition='outside'
            ))
            fig.update_layout(
                title='Distribution of Final Scores',
                xaxis_title='Number of Students',
                yaxis_title='Grade Range',
                template='plotly_dark',
                plot_bgcolor='#262730',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grade data available")
    
    with col2:
        st.markdown("### 📊 Submission Activity")
        df = run_query(f"""
            SELECT 
                DATE(g.timestamp) as date,
                COUNT(*) as submissions,
                ROUND(AVG(g.final_score), 2) as avg_score
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            {dept_where}
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
                title='Daily Submissions & Average Scores',
                xaxis_title='Date',
                yaxis_title='Submissions',
                yaxis2=dict(
                    title='Average Score (%)',
                    overlaying='y',
                    side='right'
                ),
                template='plotly_dark',
                plot_bgcolor='#262730',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No submission data available")
    
    st.markdown("---")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Top Performing Students")
        df = run_query(f"""
            SELECT 
                u.name as student_name,
                u.department,
                ROUND(AVG(g.final_score), 2) as avg_score,
                COUNT(g._id) as attempts
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL {dept_where}
            GROUP BY u.user_id, u.name, u.department
            ORDER BY avg_score DESC
            LIMIT 10
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=350)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "top_performers.csv", "text/csv")
        else:
            st.info("No student data available")
    
    with col2:
        st.markdown("### ⚠️ Students Needing Support")
        df = run_query(f"""
            SELECT 
                u.name as student_name,
                u.department,
                ROUND(AVG(g.final_score), 2) as avg_score,
                COUNT(g._id) as attempts,
                MAX(g.timestamp) as last_activity
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL {dept_where}
            GROUP BY u.user_id, u.name, u.department
            HAVING avg_score < {risk_threshold}
            ORDER BY avg_score ASC
            LIMIT 10
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=350)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "at_risk_preview.csv", "text/csv")
            st.warning(f"**{len(df)}** students shown - See 'At-Risk Students' tab for full list")
        else:
            st.success(f"✅ No students below {risk_threshold}% threshold!")
    
    st.markdown("---")
    
    # Department Performance Summary
    if selected_dept == 'All':
        st.markdown("### 🏢 Department Performance Summary")
        df = run_query(f"""
            SELECT 
                u.department,
                COUNT(DISTINCT u.user_id) as students,
                COUNT(g._id) as total_submissions,
                ROUND(AVG(g.final_score), 2) as avg_score,
                COUNTIF(g.final_score >= 80) / COUNT(*) * 100 as pct_above_80
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL
            GROUP BY u.department
            ORDER BY avg_score DESC
        """)
        if df is not None and not df.empty:
            df['pct_above_80'] = df['pct_above_80'].round(1)
            st.dataframe(df, use_container_width=True, height=300)
        else:
            st.info("No department data available")

# TAB 2: STUDENT PERFORMANCE
with tabs[1]:
    st.markdown("## 👥 Student Performance Analytics")
    
    # Search and filters
    col1, col2 = st.columns(2)
    with col1:
        search_student = st.text_input("🔍 Search by Student Name", "")
    with col2:
        sort_by = st.selectbox("Sort By", ["Average Score (High to Low)", "Average Score (Low to High)", 
                                           "Total Attempts", "Name (A-Z)"])
    
    # Build sort clause
    sort_map = {
        "Average Score (High to Low)": "avg_score DESC",
        "Average Score (Low to High)": "avg_score ASC",
        "Total Attempts": "attempts DESC",
        "Name (A-Z)": "u.name ASC"
    }
    sort_clause = sort_map[sort_by]
    
    # Build search filter
    search_where = f"AND LOWER(u.name) LIKE '%{search_student.lower()}%'" if search_student else ""
    
    df = run_query(f"""
        SELECT 
            u.name as student_name,
            u.department,
            u.role,
            COUNT(g._id) as attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(MIN(g.final_score), 2) as min_score,
            ROUND(MAX(g.final_score), 2) as max_score,
            MAX(g.timestamp) as last_activity
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
        WHERE g.final_score IS NOT NULL {dept_where} {search_where}
        GROUP BY u.user_id, u.name, u.department, u.role
        ORDER BY {sort_clause}
    """)
    
    if df is not None and not df.empty:
        # Color-code by performance
        def highlight_performance(row):
            if row['avg_score'] >= 80:
                return ['background-color: rgba(46, 204, 113, 0.2)'] * len(row)
            elif row['avg_score'] < risk_threshold:
                return ['background-color: rgba(231, 76, 60, 0.2)'] * len(row)
            return [''] * len(row)
        
        st.dataframe(df, use_container_width=True, height=500)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "student_performance.csv", "text/csv")
        with col2:
            st.metric("Total Students", len(df))
        with col3:
            at_risk = len(df[df['avg_score'] < risk_threshold])
            st.metric("At-Risk in This View", at_risk)
    else:
        st.info("No student performance data available")

# TAB 3: CASE STUDY ANALYTICS
with tabs[2]:
    st.markdown("## 📚 Case Study Analytics")
    
    # Detailed case study performance
    df = run_query(f"""
        SELECT 
            c.title as case_study,
            COUNT(DISTINCT g.user) as unique_students,
            COUNT(g._id) as total_attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(MIN(CASE WHEN g.final_score > 0 THEN g.final_score END), 2) as min_nonzero,
            ROUND(MAX(g.final_score), 2) as max_score,
            ROUND(STDDEV(g.final_score), 2) as std_dev
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
        WHERE g.final_score IS NOT NULL {dept_where}
        GROUP BY c.case_study_id, c.title
        ORDER BY avg_score DESC
    """)
    
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Detailed Report", csv, "case_study_analytics.csv", "text/csv")
        
        st.markdown("---")
        
        # Score ranges visualization
        st.markdown("### 📊 Score Ranges by Case Study")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Min (Non-Zero)',
            x=df['min_nonzero'],
            y=df['case_study'],
            orientation='h',
            marker=dict(color='#e67e22'),
            text=df['min_nonzero'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"),
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Average',
            x=df['avg_score'],
            y=df['case_study'],
            orientation='h',
            marker=dict(color='#3498db'),
            text=df['avg_score'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Maximum',
            x=df['max_score'],
            y=df['case_study'],
            orientation='h',
            marker=dict(color='#2ecc71'),
            text=df['max_score'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Case Study Score Ranges',
            xaxis_title='Score (%)',
            yaxis_title='Case Study',
            barmode='group',
            template='plotly_dark',
            plot_bgcolor='#262730',
            paper_bgcolor='#0E1117',
            font=dict(color='#FAFAFA'),
            height=max(400, len(df) * 50),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No case study data available")

# TAB 4: AT-RISK STUDENTS
with tabs[3]:
    st.markdown("## ⚠️ At-Risk Students")
    st.markdown(f"**Threshold:** Students with average scores below {risk_threshold}%")
    
    df = run_query(f"""
        SELECT 
            u.name as student_name,
            u.department,
            COUNT(g._id) as attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(MIN(g.final_score), 2) as lowest_score,
            MAX(g.timestamp) as last_activity,
            DATE_DIFF(CURRENT_DATE(), DATE(MAX(g.timestamp)), DAY) as days_since_last
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
        WHERE g.final_score IS NOT NULL {dept_where}
        GROUP BY u.user_id, u.name, u.department
        HAVING avg_score < {risk_threshold}
        ORDER BY avg_score ASC
    """)
    
    if df is not None and not df.empty:
        st.warning(f"**{len(df)} students** need intervention")
        
        st.dataframe(df, use_container_width=True, height=500)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download At-Risk Report", csv, "at_risk_students.csv", "text/csv")
        
        with col2:
            inactive = len(df[df['days_since_last'] > 7])
            st.metric("Inactive (7+ days)", inactive, delta="Needs follow-up", delta_color="inverse")
    else:
        st.success(f"✅ No students below {risk_threshold}% threshold!")

# TAB 5: PROGRESS TRACKING
with tabs[4]:
    st.markdown("## 📈 Learning Progress Tracking")
    
    # Weekly progress
    st.markdown("### 📅 Weekly Performance Trends")
    df = run_query(f"""
        SELECT 
            DATE_TRUNC(g.timestamp, WEEK) as week,
            COUNT(DISTINCT g.user) as active_students,
            COUNT(g._id) as total_submissions,
            ROUND(AVG(g.final_score), 2) as avg_score
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
        WHERE g.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        {dept_where}
        GROUP BY week
        ORDER BY week
    """)
    
    if df is not None and not df.empty:
        fig = create_multi_line_chart(
            df, 'week',
            ['active_students', 'total_submissions', 'avg_score'],
            'Weekly Learning Metrics',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No progress data available")
    
    st.markdown("---")
    
    # Department comparison (if viewing all)
    if selected_dept == 'All':
        st.markdown("### 🏢 Department Comparison")
        df = run_query(f"""
            SELECT 
                u.department,
                COUNT(DISTINCT u.user_id) as students,
                COUNT(g._id) as submissions,
                ROUND(AVG(g.final_score), 2) as avg_score
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.user` u ON g.user = u.user_id
            WHERE g.final_score IS NOT NULL
            GROUP BY u.department
            ORDER BY avg_score DESC
        """)
        
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'department', 'avg_score', 
                               'Average Score by Department', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No department data available")

# TAB 6: INDIVIDUAL STUDENT
with tabs[5]:
    st.markdown("## 🎯 Individual Student Lookup")
    
    # Get list of students
    students_df = run_query(f"""
        SELECT DISTINCT u.name, u.user_id
        FROM `{DATASET_ID}.user` u
        JOIN `{DATASET_ID}.grades` g ON u.user_id = g.user
        WHERE 1=1 {dept_where}
        ORDER BY u.name
    """)
    
    if students_df is not None and not students_df.empty:
        student_names = students_df['name'].tolist()
        selected_student = st.selectbox("Select Student", student_names)
        
        if selected_student:
            student_id = students_df[students_df['name'] == selected_student]['user_id'].iloc[0]
            
            # Student overview
            col1, col2, col3, col4 = st.columns(4)
            
            df = run_query(f"""
                SELECT 
                    COUNT(g._id) as attempts,
                    ROUND(AVG(g.final_score), 2) as avg_score,
                    ROUND(MIN(g.final_score), 2) as min_score,
                    ROUND(MAX(g.final_score), 2) as max_score
                FROM `{DATASET_ID}.grades` g
                WHERE g.user = '{student_id}' AND g.final_score IS NOT NULL
            """)
            
            if df is not None and not df.empty:
                with col1:
                    st.metric("Total Attempts", df['attempts'].iloc[0])
                with col2:
                    st.metric("Average Score", f"{df['avg_score'].iloc[0]:.1f}%")
                with col3:
                    st.metric("Lowest Score", f"{df['min_score'].iloc[0]:.1f}%")
                with col4:
                    st.metric("Highest Score", f"{df['max_score'].iloc[0]:.1f}%")
            
            st.markdown("---")
            
            # Performance over time
            st.markdown("### 📈 Score Progression")
            df = run_query(f"""
                SELECT 
                    g.timestamp,
                    c.title as case_study,
                    g.final_score
                FROM `{DATASET_ID}.grades` g
                JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
                WHERE g.user = '{student_id}' AND g.final_score IS NOT NULL
                ORDER BY g.timestamp
            """)
            
            if df is not None and not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['final_score'],
                    mode='lines+markers',
                    name='Score',
                    line=dict(color='#3498db', width=2),
                    marker=dict(size=10),
                    text=df['case_study'],
                    hovertemplate='<b>%{text}</b><br>Score: %{y:.1f}%<br>Date: %{x}<extra></extra>'
                ))
                
                # Add trend line if scipy is available
                try:
                    from scipy import stats
                    x_numeric = list(range(len(df)))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, df['final_score'])
                    trend_line = [slope * x + intercept for x in x_numeric]
                    
                    fig.add_trace(go.Scatter(
                        x=df['timestamp'],
                        y=trend_line,
                        mode='lines',
                        name='Trend',
                        line=dict(color='#2ecc71', width=2, dash='dash')
                    ))
                except ImportError:
                    # Scipy not available - show simple moving average instead
                    if len(df) >= 3:
                        df['ma'] = df['final_score'].rolling(window=3, center=True).mean()
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df['ma'],
                            mode='lines',
                            name='Moving Avg',
                            line=dict(color='#2ecc71', width=2, dash='dash')
                        ))
                
                fig.update_layout(
                    title=f'{selected_student} - Score Progression',
                    xaxis_title='Date',
                    yaxis_title='Score (%)',
                    template='plotly_dark',
                    plot_bgcolor='#262730',
                    paper_bgcolor='#0E1117',
                    font=dict(color='#FAFAFA'),
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed history
                st.markdown("### 📋 Detailed Submission History")
                st.dataframe(df, use_container_width=True, height=300)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download History", csv, f"{selected_student}_history.csv", "text/csv")
            else:
                st.info("No submission history for this student")
    else:
        st.info("No students found")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Faculty Dashboard v1.0")
