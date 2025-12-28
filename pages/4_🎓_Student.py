"""
Student Dashboard - COMPLETE STANDALONE VERSION
Personal Learning Journey, Performance Tracking & Progress Analytics
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
    page_title="Student Dashboard | MIND Platform",
    page_icon="👨🏿‍🎓",
    layout="wide"
)

# Authentication
require_authentication()
user = get_current_user()
if not can_access_page(user['role'], 'Student'):
    st.error("⛔ Access Denied: Student privileges required")
    st.stop()

# Student selection will be done via dropdown in sidebar
# TODO: When RBAC is fully implemented, uncomment these lines and remove dropdown
# student_user_id = user.get('user_id', None)
# student_name = user.get('name', 'Student')
student_user_id = None  # Will be set by selector
student_name = None     # Will be set by selector

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
def plot_bar_chart(df, x, y, title, orientation='v', height=400, color=None):
    fig = px.bar(df, x=x, y=y, title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), orientation=orientation, 
                 height=height, color=color)
    fig.update_layout(plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
    return fig

def plot_line_chart(df, x, y, title, height=400):
    fig = px.line(df, x=x, y=y, title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), height=height, markers=True)
    fig.update_layout(plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')), 
                     hovermode='x unified')
    return fig

def plot_gauge(value, title, max_value=100, height=300):
    """Create a gauge chart with visible indicator needle"""
    if value is None or pd.isna(value):
        value = 0
    
    # Determine colors based on value
    if value >= 80:
        color = '#2ECC71'
    elif value >= 60:
        color = '#F39C12'
    else:
        color = '#E74C3C'
    
    # Theme-aware colors
    is_light = st.session_state.get('theme') == 'light'
    text_color = '#262730' if is_light else '#FAFAFA'
    bg_color = '#F0F0F0' if is_light else '#1E1E1E'
    border_color = '#262730' if is_light else '#FAFAFA'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': text_color}},
        number={'font': {'size': 40, 'color': text_color}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': text_color},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': bg_color,
            'borderwidth': 2,
            'bordercolor': border_color,
            'steps': [
                {'range': [0, 60], 'color': 'rgba(231, 76, 60, 0.3)'},
                {'range': [60, 80], 'color': 'rgba(243, 156, 18, 0.3)'},
                {'range': [80, max_value], 'color': 'rgba(46, 204, 113, 0.3)'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': float(value)
            }
        }
    ))
    
    fig.update_layout(
        template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), 
        plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), 
        paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), 
        font=dict(color=text_color), 
        height=height,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

# Header
st.title("👨🏿‍🎓 My Learning Journey")

# Student Selector (for demo/admin purposes - will be replaced with RBAC)
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📚 Student Selector")
    st.caption("*For demo/testing - RBAC coming soon*")
    
    # Get all students who have grades
    students_df = run_query(f"""
        SELECT DISTINCT 
            u.user_id,
            u.name,
            u.department,
            COUNT(g._id) as submission_count
        FROM `{DATASET_ID}.user` u
        JOIN `{DATASET_ID}.grades` g ON u.user_id = g.user
        WHERE g.final_score IS NOT NULL
        GROUP BY u.user_id, u.name, u.department
        ORDER BY u.name
    """)
    
    if students_df is not None and not students_df.empty:
        # Create display options with name and submission count
        student_options = [f"{row['name']} ({row['submission_count']} submissions)" 
                          for _, row in students_df.iterrows()]
        
        # Student selector
        selected_idx = st.selectbox(
            "Select Student:",
            range(len(student_options)),
            format_func=lambda i: student_options[i],
            key="student_selector"
        )
        
        # Get selected student details
        selected_student = students_df.iloc[selected_idx]
        student_user_id = selected_student['user_id']
        student_name = selected_student['name']
        
        # Show selected student info
        st.info(f"👤🏿 **{student_name}**  \n📊 {selected_student['department']}")
    else:
        st.error("No student data found in database")
        student_user_id = None
        student_name = "Student"

st.markdown(f"### Welcome back, {student_name}!")
st.markdown("---")

# Remove demo mode check - now always using selected student
if not student_user_id:
    st.error("⚠️ No student data available. Please check database connection.")
    st.stop()

# Main content tabs
tabs = st.tabs([
    "📊 My Overview",
    "📈 Progress Tracker",
    "📚 Case Studies",
    "🎯 My Scores",
    "🏆 Achievements",
    "📅 Study Plan"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 My Performance Overview")
    
    # Get student's data
    my_stats = run_query(f"""
        SELECT 
            COUNT(g._id) as total_attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(MIN(g.final_score), 2) as min_score,
            ROUND(MAX(g.final_score), 2) as max_score,
            COUNT(DISTINCT g.case_study) as cases_attempted
        FROM `{DATASET_ID}.grades` g
        WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
    """)
    
    # Get class average for comparison
    class_avg = run_query(f"""
        SELECT ROUND(AVG(final_score), 2) as class_avg
        FROM `{DATASET_ID}.grades`
        WHERE final_score IS NOT NULL
    """)
    
    # Get percentile rank
    my_rank = run_query(f"""
        WITH student_avgs AS (
            SELECT 
                user,
                AVG(final_score) as avg_score
            FROM `{DATASET_ID}.grades`
            WHERE final_score IS NOT NULL
            GROUP BY user
        ),
        my_avg AS (
            SELECT avg_score as my_score
            FROM student_avgs
            WHERE user = '{student_user_id}'
        )
        SELECT 
            ROUND(SAFE_DIVIDE(COUNTIF(s.avg_score < m.my_score), COUNT(*)) * 100, 0) as percentile
        FROM student_avgs s, my_avg m
    """)
    
    # KPIs Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if my_stats is not None and not my_stats.empty and pd.notna(my_stats['avg_score'].iloc[0]):
        stats = my_stats.iloc[0]
        
        with col1:
            st.metric("My Average", f"{stats['avg_score']:.1f}%")
        
        with col2:
            st.metric("Total Attempts", f"{int(stats['total_attempts'])}")
        
        with col3:
            if class_avg is not None and not class_avg.empty and pd.notna(class_avg['class_avg'].iloc[0]):
                class_score = class_avg['class_avg'].iloc[0]
                delta = stats['avg_score'] - class_score
                if pd.notna(delta):
                    st.metric("vs Class Avg", f"{delta:+.1f}%", 
                             delta=f"{delta:+.1f}%" if abs(delta) > 0.1 else "On par")
                else:
                    st.metric("vs Class Avg", "N/A")
            else:
                st.metric("vs Class Avg", "N/A")
        
        with col4:
            if my_rank is not None and not my_rank.empty and pd.notna(my_rank['percentile'].iloc[0]):
                percentile = my_rank['percentile'].iloc[0]
                st.metric("Class Rank", f"Top {100-percentile:.0f}%")
            else:
                st.metric("Class Rank", "N/A")
        
        with col5:
            st.metric("Cases Attempted", f"{int(stats['cases_attempted'])}")
    else:
        # No data available
        with col1:
            st.metric("My Average", "N/A")
        with col2:
            st.metric("Total Attempts", "0")
        with col3:
            st.metric("vs Class Avg", "N/A")
        with col4:
            st.metric("Class Rank", "N/A")
        with col5:
            st.metric("Cases Attempted", "0")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 My Performance Score")
        if my_stats is not None and not my_stats.empty and pd.notna(my_stats['avg_score'].iloc[0]):
            stats = my_stats.iloc[0]
            fig = plot_gauge(stats['avg_score'], "Current Average", max_value=100, height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance message
            if stats['avg_score'] >= 90:
                st.success("🌟 **Outstanding!** Keep up the excellent work!")
            elif stats['avg_score'] >= 80:
                st.success("✨ **Great job!** You're performing well!")
            elif stats['avg_score'] >= 70:
                st.info("📚 **Good progress!** Keep learning!")
            elif stats['avg_score'] >= 60:
                st.warning("⚠️ **Needs improvement.** Consider reviewing materials.")
            else:
                st.error("🆘 **Needs urgent attention.** Reach out for help!")
        else:
            st.info("🎯 **Complete your first case study to see your performance!**")
            st.markdown("""
            **Get started:**
            1. Choose a case study
            2. Complete the assignment
            3. Submit for grading
            4. Track your progress here!
            """)
    
    with col2:
        st.markdown("### 📈 Score Progression")
        progress_df = run_query(f"""
            SELECT 
                DATE(g.timestamp) as date,
                AVG(g.final_score) as daily_avg
            FROM `{DATASET_ID}.grades` g
            WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
            GROUP BY date
            ORDER BY date
        """)
        
        if progress_df is not None and not progress_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=progress_df['date'],
                y=progress_df['daily_avg'],
                mode='lines+markers',
                name='Daily Average',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.2)'
            ))
            
            # Add goal line at 80%
            fig.add_hline(y=80, line_dash="dash", line_color="green", 
                         annotation_text="Target: 80%", annotation_position="right")
            
            fig.update_layout(
                title='My Daily Performance Trend',
                xaxis_title='Date',
                yaxis_title='Score (%)',
                template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=300,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete more assignments to see trends!")
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 Recent Submissions")
        recent = run_query(f"""
            SELECT 
                c.title as case_study,
                g.final_score as score,
                g.timestamp
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
            WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
            ORDER BY g.timestamp DESC
            LIMIT 5
        """)
        
        if recent is not None and not recent.empty:
            recent['timestamp'] = pd.to_datetime(recent['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(recent, use_container_width=True, height=200)
        else:
            st.info("No submissions yet. Start your first case study!")
    
    with col2:
        st.markdown("### 🏆 My Best Scores")
        best = run_query(f"""
            SELECT 
                c.title as case_study,
                MAX(g.final_score) as best_score,
                MAX(g.timestamp) as achieved_on
            FROM `{DATASET_ID}.grades` g
            JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
            WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
            GROUP BY c.case_study_id, c.title
            ORDER BY best_score DESC
            LIMIT 5
        """)
        
        if best is not None and not best.empty:
            best['achieved_on'] = pd.to_datetime(best['achieved_on']).dt.strftime('%Y-%m-%d')
            st.dataframe(best, use_container_width=True, height=200)
        else:
            st.info("Complete case studies to build your achievement list!")
    
    # TAB 2: PROGRESS TRACKER
with tabs[1]:
    st.markdown("## 📈 My Progress Tracker")
    
    # Time range selector
    time_range = st.selectbox("View Progress For:", 
                             ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
                             index=1)
    
    time_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "All Time": 36500
    }
    days = time_map[time_range]
    
    # Detailed progression
    detailed_progress = run_query(f"""
        SELECT 
            g.timestamp,
            c.title as case_study,
            g.final_score
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        WHERE g.user = '{student_user_id}' 
            AND g.final_score IS NOT NULL
            AND g.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ORDER BY g.timestamp
    """)
    
    if detailed_progress is not None and not detailed_progress.empty:
        # Score over time chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=detailed_progress['timestamp'],
            y=detailed_progress['final_score'],
            mode='lines+markers',
            name='My Scores',
            line=dict(color='#3498db', width=2),
            marker=dict(size=10, color=detailed_progress['final_score'], 
                       colorscale='RdYlGn', showscale=True,
                       colorbar=dict(title="Score")),
            text=detailed_progress['case_study'],
            hovertemplate='<b>%{text}</b><br>Score: %{y:.1f}%<br>Date: %{x}<extra></extra>'
        ))
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=detailed_progress['timestamp'],
            y=detailed_progress['final_score'].rolling(window=3, min_periods=1).mean(),
            mode='lines',
            name='Trend (3-period avg)',
            line=dict(color='#2ecc71', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title='My Score Progression',
            xaxis_title='Date',
            yaxis_title='Score (%)',
            template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
            plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            improvement = detailed_progress['final_score'].iloc[-1] - detailed_progress['final_score'].iloc[0]
            st.metric("Score Change", f"{improvement:+.1f}%", 
                     delta="Improving!" if improvement > 0 else "Keep working!")
        
        with col2:
            best_streak = detailed_progress[detailed_progress['final_score'] >= 80].shape[0]
            st.metric("Scores ≥80%", f"{best_streak}")
        
        with col3:
            avg_recent = detailed_progress['final_score'].tail(5).mean()
            st.metric("Recent 5 Avg", f"{avg_recent:.1f}%")
        
        with col4:
            total_progress = len(detailed_progress)
            st.metric("Total Submissions", f"{total_progress}")
        
        st.markdown("---")
        
        # Detailed table
        st.markdown("### 📋 Detailed Submission History")
        detailed_progress['timestamp'] = pd.to_datetime(detailed_progress['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(detailed_progress, use_container_width=True, height=400)
        
        csv = detailed_progress.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download My Progress", csv, "my_progress.csv", "text/csv")
    else:
        st.info(f"No submissions in the {time_range.lower()}. Keep learning!")

# TAB 3: CASE STUDIES
with tabs[2]:
    st.markdown("## 📚 My Case Study Performance")
    
    case_performance = run_query(f"""
        SELECT 
            c.title as case_study,
            COUNT(g._id) as my_attempts,
            ROUND(AVG(g.final_score), 2) as my_avg,
            ROUND(MAX(g.final_score), 2) as my_best,
            MAX(g.timestamp) as last_attempt
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
        GROUP BY c.case_study_id, c.title
        ORDER BY last_attempt DESC
    """)
    
    if case_performance is not None and not case_performance.empty:
        # Summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cases Attempted", len(case_performance))
        with col2:
            mastered = len(case_performance[case_performance['my_best'] >= 90])
            st.metric("Mastered (≥90%)", mastered)
        with col3:
            need_work = len(case_performance[case_performance['my_avg'] < 70])
            st.metric("Need Review (<70%)", need_work)
        
        st.markdown("---")
        
        # Chart
        st.markdown("### 📊 My Performance by Case Study")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='My Average',
            x=case_performance['case_study'],
            y=case_performance['my_avg'],
            marker=dict(color='#3498db'),
            text=case_performance['my_avg'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        
        fig.add_trace(go.Scatter(
            name='My Best',
            x=case_performance['case_study'],
            y=case_performance['my_best'],
            mode='markers',
            marker=dict(color='#2ecc71', size=15, symbol='star')
        ))
        
        fig.update_layout(
            title='My Scores by Case Study',
            xaxis_title='Case Study',
            yaxis_title='Score (%)',
            template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
            plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed table
        st.markdown("### 📋 Case Study Details")
        case_performance['last_attempt'] = pd.to_datetime(case_performance['last_attempt']).dt.strftime('%Y-%m-%d')
        st.dataframe(case_performance, use_container_width=True, height=400)
        
        csv = case_performance.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report", csv, "my_case_studies.csv", "text/csv")
    else:
        st.info("Start attempting case studies to see your performance!")

# TAB 4: MY SCORES
with tabs[3]:
    st.markdown("## 🎯 All My Scores")
    
    all_scores = run_query(f"""
        SELECT 
            g.timestamp,
            c.title as case_study,
            g.final_score,
            g.performance_summary
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
        ORDER BY g.timestamp DESC
    """)
    
    if all_scores is not None and not all_scores.empty:
        # Search and filter
        col1, col2 = st.columns(2)
        
        with col1:
            search = st.text_input("🔍 Search by case study", "")
        
        with col2:
            min_score = st.slider("Filter by minimum score", 0, 100, 0)
        
        # Apply filters
        filtered = all_scores.copy()
        if search:
            filtered = filtered[filtered['case_study'].str.contains(search, case=False, na=False)]
        filtered = filtered[filtered['final_score'] >= min_score]
        
        # Display
        st.markdown(f"### Showing {len(filtered)} of {len(all_scores)} submissions")
        
        filtered['timestamp'] = pd.to_datetime(filtered['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(filtered, use_container_width=True, height=500)
        
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download All Scores", csv, "all_my_scores.csv", "text/csv")
    else:
        st.info("No scores yet. Complete your first case study!")

# TAB 5: ACHIEVEMENTS
with tabs[4]:
    st.markdown("## 🏆 My Achievements & Milestones")
    
    if my_stats is not None and not my_stats.empty and pd.notna(my_stats['avg_score'].iloc[0]):
        stats = my_stats.iloc[0]
        
        # Achievement calculations
        achievements = []
        
        # Score-based achievements
        if stats['avg_score'] >= 90:
            achievements.append({"badge": "🌟", "title": "Excellence", "desc": "Average score ≥90%"})
        if stats['avg_score'] >= 80:
            achievements.append({"badge": "⭐", "title": "High Performer", "desc": "Average score ≥80%"})
        if pd.notna(stats['max_score']) and stats['max_score'] == 100:
            achievements.append({"badge": "💯", "title": "Perfect Score", "desc": "Achieved 100%"})
        
        # Attempt-based achievements
        if stats['total_attempts'] >= 50:
            achievements.append({"badge": "🔥", "title": "Dedicated Learner", "desc": "50+ submissions"})
        elif stats['total_attempts'] >= 25:
            achievements.append({"badge": "📚", "title": "Active Student", "desc": "25+ submissions"})
        elif stats['total_attempts'] >= 10:
            achievements.append({"badge": "🎯", "title": "Getting Started", "desc": "10+ submissions"})
        
        # Case study achievements
        if stats['cases_attempted'] >= 5:
            achievements.append({"badge": "🗂️", "title": "Explorer", "desc": "5+ cases attempted"})
        
        # Display achievements
        if achievements:
            st.markdown("### 🏅 My Badges")
            cols = st.columns(min(len(achievements), 4))
            for idx, achievement in enumerate(achievements):
                with cols[idx % 4]:
                    st.markdown(f"### {achievement['badge']}")
                    st.markdown(f"**{achievement['title']}**")
                    st.caption(achievement['desc'])
        else:
            st.info("💡 Keep learning to unlock achievements!")
        
        st.markdown("---")
        
        # Progress to next milestone
        st.markdown("### 🎯 Next Milestones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Score Goals**")
            if stats['avg_score'] < 80:
                progress = (stats['avg_score'] / 80) * 100
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{progress:.0f}% to 80% average (⭐ High Performer)")
            elif stats['avg_score'] < 90:
                progress = ((stats['avg_score'] - 80) / 10) * 100
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{progress:.0f}% to 90% average (🌟 Excellence)")
            else:
                st.success("✅ All score milestones achieved!")
        
        with col2:
            st.markdown("**Activity Goals**")
            if stats['total_attempts'] < 10:
                progress = (stats['total_attempts'] / 10) * 100
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{progress:.0f}% to 10 submissions (🎯 Getting Started)")
            elif stats['total_attempts'] < 25:
                progress = ((stats['total_attempts'] - 10) / 15) * 100
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{progress:.0f}% to 25 submissions (📚 Active Student)")
            elif stats['total_attempts'] < 50:
                progress = ((stats['total_attempts'] - 25) / 25) * 100
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{progress:.0f}% to 50 submissions (🔥 Dedicated Learner)")
            else:
                st.success("✅ All activity milestones achieved!")
    else:
        st.info("🎯 **Start your learning journey to earn achievements!**")
        st.markdown("""
        ### Available Achievements:
        
        **Score-Based:**
        - 🌟 Excellence (≥90% average)
        - ⭐ High Performer (≥80% average)
        - 💯 Perfect Score (100% on any assignment)
        
        **Activity-Based:**
        - 🎯 Getting Started (10+ submissions)
        - 📚 Active Student (25+ submissions)
        - 🔥 Dedicated Learner (50+ submissions)
        - 🗂️ Explorer (5+ different cases)
        
        **Complete your first case study to start earning badges!**
        """)

# TAB 6: STUDY PLAN
with tabs[5]:
    st.markdown("## 📅 My Study Recommendations")
    
    # Get cases I haven't mastered
    needs_review = run_query(f"""
        SELECT 
            c.title as case_study,
            ROUND(AVG(g.final_score), 2) as my_avg,
            COUNT(g._id) as attempts,
            MAX(g.timestamp) as last_attempt
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study = c.case_study_id
        WHERE g.user = '{student_user_id}' AND g.final_score IS NOT NULL
        GROUP BY c.case_study_id, c.title
        HAVING AVG(g.final_score) < 80
        ORDER BY my_avg ASC
    """)
    
    if needs_review is not None and not needs_review.empty:
        st.markdown("### 📚 Cases to Review (avg < 80%)")
        st.dataframe(needs_review, use_container_width=True, height=300)
        
        st.info(f"💡 **Tip**: Focus on {needs_review.iloc[0]['case_study']} - your lowest scoring case study")
    else:
        st.success("🎉 Great job! You've mastered all attempted case studies!")
    
    st.markdown("---")
    
    # Study streak
    st.markdown("### 📊 My Activity Pattern")
    
    activity = run_query(f"""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as submissions
        FROM `{DATASET_ID}.grades`
        WHERE user = '{student_user_id}'
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        GROUP BY date
        ORDER BY date
    """)
    
    if activity is not None and not activity.empty:
        fig = go.Figure(go.Bar(
            x=activity['date'],
            y=activity['submissions'],
            marker=dict(color='#3498db')
        ))
        
        fig.update_layout(
            title='My Daily Activity (Last 30 Days)',
            xaxis_title='Date',
            yaxis_title='Submissions',
            template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'),
            plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate streak
        activity['date'] = pd.to_datetime(activity['date'])
        activity = activity.sort_values('date', ascending=False)
        
        streak = 0
        for i, row in activity.iterrows():
            expected_date = datetime.now().date() - timedelta(days=streak)
            if row['date'].date() == expected_date:
                streak += 1
            else:
                break
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Streak", f"{streak} days")
        with col2:
            st.metric("Active Days (30d)", f"{len(activity)}")
        with col3:
            avg_daily = activity['submissions'].mean()
            st.metric("Avg Daily Submissions", f"{avg_daily:.1f}")
    else:
        st.info("Start studying to build your activity streak!")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Keep learning! 👨🏿‍🎓")
