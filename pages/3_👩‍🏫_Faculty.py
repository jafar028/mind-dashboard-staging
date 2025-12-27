"""
Faculty Dashboard
Academic Insights & Student Performance Analytics
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    require_authentication, show_user_info_sidebar, get_current_user,
    create_metric_cards, plot_heatmap, plot_bar_chart, plot_box_plot,
    plot_radar_chart, create_multi_line_chart, export_dataframe_to_csv,
    export_dataframe_to_excel, QueryBuilder
)
from config.database import get_cached_query, run_query, DATASET_ID
from config.auth import can_access_page

# Page config
st.set_page_config(
    page_title="Faculty Dashboard | MIND Platform",
    page_icon="👩‍🏫",
    layout="wide"
)

# Authentication check
require_authentication()

# Check role permission
user = get_current_user()
if not can_access_page(user['role'], 'Faculty'):
    st.error("⛔ Access Denied: Faculty privileges required")
    st.stop()

# Sidebar
show_user_info_sidebar()

# Header
st.title("👩‍🏫 Faculty Dashboard")
st.markdown("### Academic Insights & Learning Analytics")
st.markdown("---")

# Filters
with st.sidebar:
    st.markdown("### 📊 Filters")
    
    # Get unique cohorts and departments
    cohort_query = f"""
    SELECT DISTINCT cohort 
    FROM `{DATASET_ID}.user` 
    WHERE cohort IS NOT NULL 
    ORDER BY cohort DESC
    """
    cohort_df = get_cached_query(cohort_query)
    cohorts = ['All'] + (cohort_df['cohort'].tolist() if cohort_df is not None and not cohort_df.empty else [])
    
    selected_cohort = st.selectbox("Cohort", cohorts)
    
    dept_query = f"""
    SELECT DISTINCT department 
    FROM `{DATASET_ID}.user` 
    WHERE department IS NOT NULL 
    ORDER BY department
    """
    dept_df = get_cached_query(dept_query)
    departments = ['All'] + (dept_df['department'].tolist() if dept_df is not None and not dept_df.empty else [])
    
    selected_dept = st.selectbox("Department", departments)
    
    st.markdown("---")
    
    # Risk threshold
    risk_threshold = st.slider("At-Risk Threshold (%)", 0, 100, 60)

# Apply filters to queries
cohort_filter = None if selected_cohort == 'All' else selected_cohort
dept_filter = None if selected_dept == 'All' else selected_dept

# Main content
tabs = st.tabs([
    "📊 Overview",
    "👥 Student Performance",
    "📚 Case Studies",
    "⚠️ At-Risk Students",
    "📈 Trends"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 Academic Overview")
    
    # Get filtered data
    avg_grade_df = get_cached_query(QueryBuilder.get_average_grade())
    cohort_perf_df = get_cached_query(QueryBuilder.get_cohort_performance(cohort_filter))
    dept_perf_df = get_cached_query(QueryBuilder.get_department_performance(dept_filter))
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if avg_grade_df is not None and not avg_grade_df.empty:
            st.metric("Class Average", f"{avg_grade_df['avg_grade'].iloc[0]:.1f}%")
        else:
            st.metric("Class Average", "N/A")
    
    with col2:
        if avg_grade_df is not None and not avg_grade_df.empty:
            st.metric("Avg Communication", f"{avg_grade_df['avg_communication'].iloc[0]:.1f}%")
        else:
            st.metric("Avg Communication", "N/A")
    
    with col3:
        if avg_grade_df is not None and not avg_grade_df.empty:
            st.metric("Avg Comprehension", f"{avg_grade_df['avg_comprehension'].iloc[0]:.1f}%")
        else:
            st.metric("Avg Comprehension", "N/A")
    
    with col4:
        if avg_grade_df is not None and not avg_grade_df.empty:
            st.metric("Avg Critical Thinking", f"{avg_grade_df['avg_critical_thinking'].iloc[0]:.1f}%")
        else:
            st.metric("Avg Critical Thinking", "N/A")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Cohort Performance")
        if cohort_perf_df is not None and not cohort_perf_df.empty:
            st.dataframe(cohort_perf_df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(cohort_perf_df, 'cohort', 'avg_score',
                               'Average Score by Cohort', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cohort data available")
    
    with col2:
        st.markdown("### 📊 Department Performance")
        if dept_perf_df is not None and not dept_perf_df.empty:
            st.dataframe(dept_perf_df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(dept_perf_df, 'department', 'avg_score',
                               'Average Score by Department', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No department data available")
    
    st.markdown("---")
    
    # Performance heatmap
    st.markdown("### 🔥 Performance Heatmap: Rubric Categories")
    
    heatmap_query = f"""
    SELECT 
        c.title as case_study,
        ROUND(AVG(g.communication), 1) as communication,
        ROUND(AVG(g.comprehension), 1) as comprehension,
        ROUND(AVG(g.critical_thinking), 1) as critical_thinking
    FROM `{DATASET_ID}.grades` g
    JOIN `{DATASET_ID}.casestudy` c ON g.case_study_id = c.case_study_id
    WHERE g.final_score IS NOT NULL
    GROUP BY c.title
    ORDER BY c.title
    LIMIT 10
    """
    
    heatmap_df = get_cached_query(heatmap_query)
    
    if heatmap_df is not None and not heatmap_df.empty:
        # Prepare data for heatmap
        heatmap_data = heatmap_df.set_index('case_study').T
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn',
            hoverongaps=False,
            text=heatmap_data.values,
            texttemplate='%{text:.1f}',
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title="Rubric Performance Across Case Studies",
            template='plotly_dark',
            plot_bgcolor='#262730',
            paper_bgcolor='#0E1117',
            font=dict(color='#FAFAFA'),
            height=400,
            xaxis_title="Case Study",
            yaxis_title="Rubric Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No heatmap data available")

# TAB 2: STUDENT PERFORMANCE
with tabs[1]:
    st.markdown("## 👥 Student Performance Analytics")
    
    # Get student performance
    student_perf_df = get_cached_query(QueryBuilder.get_student_performance())
    
    if student_perf_df is not None and not student_perf_df.empty:
        # Apply filters if selected
        filtered_df = student_perf_df.copy()
        
        if cohort_filter:
            filtered_df = filtered_df[filtered_df['cohort'] == cohort_filter]
        
        if dept_filter:
            filtered_df = filtered_df[filtered_df['department'] == dept_filter]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", len(filtered_df))
        with col2:
            st.metric("Avg Score", f"{filtered_df['avg_score'].mean():.1f}%")
        with col3:
            top_performers = len(filtered_df[filtered_df['avg_score'] >= 80])
            st.metric("Top Performers (≥80%)", top_performers)
        with col4:
            at_risk = len(filtered_df[filtered_df['avg_score'] < risk_threshold])
            st.metric(f"At Risk (<{risk_threshold}%)", at_risk)
        
        st.markdown("---")
        
        # Search and filter
        search = st.text_input("🔍 Search students", placeholder="Enter name or email")
        
        if search:
            filtered_df = filtered_df[
                filtered_df['student_name'].str.contains(search, case=False, na=False) |
                filtered_df['student_email'].str.contains(search, case=False, na=False)
            ]
        
        # Display table
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            export_dataframe_to_csv(filtered_df, "student_performance.csv")
        with col2:
            export_dataframe_to_excel(filtered_df, "student_performance.xlsx")
        
        st.markdown("---")
        
        # Performance distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Score Distribution")
            grade_dist_df = get_cached_query(QueryBuilder.get_grade_distribution())
            if grade_dist_df is not None and not grade_dist_df.empty:
                fig = plot_bar_chart(grade_dist_df, 'grade_bracket', 'count',
                                   'Grade Distribution', height=350)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Attempts Distribution")
            fig = plot_box_plot(filtered_df, 'department', 'attempts',
                              'Attempts by Department', height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No student performance data available")

# TAB 3: CASE STUDIES
with tabs[2]:
    st.markdown("## 📚 Case Study Analytics")
    
    case_perf_df = get_cached_query(QueryBuilder.get_case_study_performance())
    
    if case_perf_df is not None and not case_perf_df.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Case Studies", len(case_perf_df))
        with col2:
            st.metric("Avg Completion", f"{case_perf_df['students_attempted'].mean():.0f} students")
        with col3:
            st.metric("Highest Avg Score", f"{case_perf_df['avg_score'].max():.1f}%")
        
        st.markdown("---")
        
        # Case study performance table
        st.markdown("### 📋 Case Study Performance Overview")
        st.dataframe(case_perf_df, use_container_width=True, height=400)
        export_dataframe_to_csv(case_perf_df, "case_study_performance.csv")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Student Engagement")
            fig = plot_bar_chart(case_perf_df, 'case_study', 'students_attempted',
                               'Students per Case Study',
                               orientation='h', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Average Scores")
            fig = plot_bar_chart(case_perf_df, 'case_study', 'avg_score',
                               'Average Score by Case Study',
                               orientation='h', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed case study selector
        st.markdown("### 🔍 Case Study Deep Dive")
        
        selected_case = st.selectbox("Select a case study", case_perf_df['case_study'].tolist())
        
        if selected_case:
            case_data = case_perf_df[case_perf_df['case_study'] == selected_case].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Students Attempted", case_data['students_attempted'])
            with col2:
                st.metric("Average Score", f"{case_data['avg_score']:.1f}%")
            with col3:
                st.metric("Communication", f"{case_data['avg_communication']:.1f}%")
            
            # Radar chart for rubric breakdown
            categories = ['Communication', 'Comprehension', 'Critical Thinking']
            values = [
                case_data['avg_communication'],
                case_data['avg_comprehension'],
                case_data['avg_critical_thinking']
            ]
            
            # Get class averages
            if avg_grade_df is not None and not avg_grade_df.empty:
                class_avg = [
                    avg_grade_df['avg_communication'].iloc[0],
                    avg_grade_df['avg_comprehension'].iloc[0],
                    avg_grade_df['avg_critical_thinking'].iloc[0]
                ]
            else:
                class_avg = None
            
            fig = plot_radar_chart(categories, values, class_avg,
                                 f"Rubric Breakdown: {selected_case}", height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No case study data available")

# TAB 4: AT-RISK STUDENTS
with tabs[3]:
    st.markdown("## ⚠️ At-Risk Student Identification")
    
    at_risk_df = get_cached_query(QueryBuilder.get_students_at_risk(risk_threshold))
    
    if at_risk_df is not None and not at_risk_df.empty:
        # Apply filters
        filtered_risk_df = at_risk_df.copy()
        
        if cohort_filter:
            filtered_risk_df = filtered_risk_df[filtered_risk_df['cohort'] == cohort_filter]
        
        if dept_filter:
            filtered_risk_df = filtered_risk_df[filtered_risk_df['department'] == dept_filter]
        
        # Summary
        st.warning(f"**{len(filtered_risk_df)} students** are currently below {risk_threshold}% average")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("At-Risk Students", len(filtered_risk_df))
        with col2:
            st.metric("Average Score", f"{filtered_risk_df['avg_score'].mean():.1f}%")
        with col3:
            st.metric("Lowest Score", f"{filtered_risk_df['avg_score'].min():.1f}%")
        
        st.markdown("---")
        
        # At-risk student table
        st.markdown("### 📋 At-Risk Student List")
        st.dataframe(filtered_risk_df, use_container_width=True, height=400)
        
        # Export
        col1, col2 = st.columns(2)
        with col1:
            export_dataframe_to_csv(filtered_risk_df, "at_risk_students.csv")
        with col2:
            export_dataframe_to_excel(filtered_risk_df, "at_risk_students.xlsx")
        
        st.markdown("---")
        
        # Intervention suggestions
        st.markdown("### 💡 Recommended Interventions")
        
        st.info("""
        **Suggested Actions:**
        1. 📧 **Reach out** to students with <50% average
        2. 🎯 **Schedule 1-on-1** meetings for personalized support
        3. 📚 **Provide additional resources** for struggling topics
        4. 👥 **Pair with peer tutors** for collaborative learning
        5. 🔄 **Monitor progress** weekly and adjust support as needed
        """)
    else:
        st.success(f"✅ No students below {risk_threshold}% threshold!")

# TAB 5: TRENDS
with tabs[4]:
    st.markdown("## 📈 Performance Trends")
    
    # Trend analysis over time
    trends_query = f"""
    SELECT 
        DATE_TRUNC(timestamp, WEEK) as week,
        ROUND(AVG(final_score), 2) as avg_score,
        ROUND(AVG(communication), 2) as avg_communication,
        ROUND(AVG(comprehension), 2) as avg_comprehension,
        ROUND(AVG(critical_thinking), 2) as avg_critical_thinking,
        COUNT(*) as attempts
    FROM `{DATASET_ID}.grades`
    WHERE final_score IS NOT NULL
        AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    GROUP BY week
    ORDER BY week
    """
    
    trends_df = get_cached_query(trends_query)
    
    if trends_df is not None and not trends_df.empty:
        st.markdown("### 📊 Weekly Performance Trends (Last 90 Days)")
        
        fig = create_multi_line_chart(
            trends_df, 'week',
            ['avg_score', 'avg_communication', 'avg_comprehension', 'avg_critical_thinking'],
            'Performance Trends Over Time',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Attempts Over Time")
            fig = plot_bar_chart(trends_df, 'week', 'attempts',
                               'Weekly Attempts', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Trend Data")
            st.dataframe(trends_df, use_container_width=True, height=350)
            export_dataframe_to_csv(trends_df, "performance_trends.csv")
    else:
        st.info("No trend data available")
    
    st.markdown("---")
    
    # Improvement tracking
    st.markdown("### 📈 Student Improvement Tracking")
    
    improvement_query = f"""
    WITH StudentAttempts AS (
        SELECT 
            user_id,
            final_score,
            timestamp,
            ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY timestamp) as attempt_num,
            LAG(final_score) OVER(PARTITION BY user_id ORDER BY timestamp) as prev_score
        FROM `{DATASET_ID}.grades`
        WHERE final_score IS NOT NULL
    )
    SELECT 
        u.name as student_name,
        COUNT(*) as total_attempts,
        ROUND(AVG(sa.final_score), 2) as avg_score,
        ROUND(MAX(sa.final_score) - MIN(sa.final_score), 2) as score_improvement
    FROM StudentAttempts sa
    JOIN `{DATASET_ID}.user` u ON sa.user_id = u.user_id
    WHERE sa.attempt_num > 1
    GROUP BY u.name
    HAVING COUNT(*) > 2
    ORDER BY score_improvement DESC
    LIMIT 20
    """
    
    improvement_df = get_cached_query(improvement_query)
    
    if improvement_df is not None and not improvement_df.empty:
        st.dataframe(improvement_df, use_container_width=True, height=400)
        export_dataframe_to_csv(improvement_df, "student_improvement.csv")
    else:
        st.info("No improvement data available (students need multiple attempts)")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Faculty Dashboard v1.0")
