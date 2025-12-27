"""
Student Dashboard
Personal Learning Journey & Performance Tracking
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    require_authentication, show_user_info_sidebar, get_current_user,
    create_metric_cards, plot_radar_chart, plot_line_chart, plot_bar_chart,
    plot_gauge, QueryBuilder
)
from config.database import get_cached_query, run_query, DATASET_ID
from config.auth import can_access_page

# Page config
st.set_page_config(
    page_title="Student Dashboard | MIND Platform",
    page_icon="🎓",
    layout="wide"
)

# Authentication check
require_authentication()

# Check role permission
user = get_current_user()
if not can_access_page(user['role'], 'Student'):
    st.error("⛔ Access Denied: Student privileges required")
    st.stop()

# Get student user_id from user data
student_user_id = user.get('user_id', None)

# Sidebar
show_user_info_sidebar()

# Header
st.title("🎓 My Learning Journey")
st.markdown(f"### Welcome, {user['name']}!")
st.markdown("---")

# Main content
tabs = st.tabs([
    "📊 Overview",
    "🎯 Performance",
    "📚 Case Studies",
    "💬 Conversations",
    "🏆 Achievements"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 My Performance Overview")
    
    # Get student's performance
    if student_user_id:
        student_perf_df = get_cached_query(QueryBuilder.get_student_performance(student_user_id))
    else:
        # Demo mode - get first student
        student_perf_df = get_cached_query(QueryBuilder.get_student_performance())
    
    # Get class averages
    avg_grade_df = get_cached_query(QueryBuilder.get_average_grade())
    
    if student_perf_df is not None and not student_perf_df.empty:
        my_data = student_perf_df.iloc[0]
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("My Average Score", f"{my_data['avg_score']:.1f}%")
        with col2:
            st.metric("Total Attempts", int(my_data['attempts']))
        with col3:
            if avg_grade_df is not None and not avg_grade_df.empty:
                class_avg = avg_grade_df['avg_grade'].iloc[0]
                delta = my_data['avg_score'] - class_avg
                st.metric("vs Class Average", f"{delta:+.1f}%", delta=f"{delta:+.1f}%")
            else:
                st.metric("Cases Completed", "N/A")
        with col4:
            # Calculate percentile
            all_students_df = get_cached_query(QueryBuilder.get_student_performance())
            if all_students_df is not None and not all_students_df.empty:
                percentile = (all_students_df['avg_score'] < my_data['avg_score']).sum() / len(all_students_df) * 100
                st.metric("Percentile Rank", f"{percentile:.0f}%")
            else:
                st.metric("Percentile Rank", "N/A")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 My Performance Radar")
            
            categories = ['Communication', 'Comprehension', 'Critical Thinking']
            my_values = [
                my_data['avg_communication'],
                my_data['avg_comprehension'],
                my_data['avg_critical_thinking']
            ]
            
            # Class averages
            if avg_grade_df is not None and not avg_grade_df.empty:
                class_avg_values = [
                    avg_grade_df['avg_communication'].iloc[0],
                    avg_grade_df['avg_comprehension'].iloc[0],
                    avg_grade_df['avg_critical_thinking'].iloc[0]
                ]
            else:
                class_avg_values = None
            
            fig = plot_radar_chart(
                categories, my_values, class_avg_values,
                "My Performance vs Class Average",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Rubric Breakdown")
            
            # Individual rubric scores with gauges
            st.markdown("#### Communication")
            fig_comm = plot_gauge(my_data['avg_communication'], "Communication Score", height=200)
            st.plotly_chart(fig_comm, use_container_width=True)
            
            st.markdown("#### Comprehension")
            fig_comp = plot_gauge(my_data['avg_comprehension'], "Comprehension Score", height=200)
            st.plotly_chart(fig_comp, use_container_width=True)
            
            st.markdown("#### Critical Thinking")
            fig_crit = plot_gauge(my_data['avg_critical_thinking'], "Critical Thinking Score", height=200)
            st.plotly_chart(fig_crit, use_container_width=True)
        
        st.markdown("---")
        
        # Strengths and areas for improvement
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💪 My Strengths")
            
            scores = {
                'Communication': my_data['avg_communication'],
                'Comprehension': my_data['avg_comprehension'],
                'Critical Thinking': my_data['avg_critical_thinking']
            }
            
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            for i, (category, score) in enumerate(sorted_scores, 1):
                if i == 1:
                    st.success(f"🥇 **{category}**: {score:.1f}%")
                elif i == 2:
                    st.info(f"🥈 **{category}**: {score:.1f}%")
                else:
                    st.warning(f"🥉 **{category}**: {score:.1f}%")
        
        with col2:
            st.markdown("### 🎯 Areas for Improvement")
            
            # Compare with class averages
            if avg_grade_df is not None and not avg_grade_df.empty:
                improvements = []
                
                if my_data['avg_communication'] < class_avg_values[0]:
                    gap = class_avg_values[0] - my_data['avg_communication']
                    improvements.append(('Communication', gap))
                
                if my_data['avg_comprehension'] < class_avg_values[1]:
                    gap = class_avg_values[1] - my_data['avg_comprehension']
                    improvements.append(('Comprehension', gap))
                
                if my_data['avg_critical_thinking'] < class_avg_values[2]:
                    gap = class_avg_values[2] - my_data['avg_critical_thinking']
                    improvements.append(('Critical Thinking', gap))
                
                if improvements:
                    improvements.sort(key=lambda x: x[1], reverse=True)
                    for category, gap in improvements:
                        st.warning(f"**{category}**: {gap:.1f}% below class average")
                else:
                    st.success("🎉 You're at or above class average in all categories!")
            else:
                st.info("No class comparison data available")
    else:
        st.info("No performance data available yet. Complete a case study to see your progress!")

# TAB 2: PERFORMANCE
with tabs[1]:
    st.markdown("## 🎯 Detailed Performance Metrics")
    
    if student_perf_df is not None and not student_perf_df.empty:
        my_data = student_perf_df.iloc[0]
        
        # Performance over time
        st.markdown("### 📈 My Progress Over Time")
        
        progress_query = f"""
        SELECT 
            timestamp,
            final_score,
            communication,
            comprehension,
            critical_thinking,
            attempt
        FROM `{DATASET_ID}.grades`
        WHERE user_id = '{student_user_id if student_user_id else my_data['student_email']}'
            AND final_score IS NOT NULL
        ORDER BY timestamp
        """
        
        progress_df = get_cached_query(progress_query) if student_user_id else None
        
        if progress_df is not None and not progress_df.empty:
            # Score progression
            from utils import create_multi_line_chart
            
            fig = create_multi_line_chart(
                progress_df, 'timestamp',
                ['final_score', 'communication', 'comprehension', 'critical_thinking'],
                'My Score Progression',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Attempt history table
            st.markdown("### 📋 My Attempt History")
            st.dataframe(progress_df, use_container_width=True, height=300)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Best Score", f"{progress_df['final_score'].max():.1f}%")
            with col2:
                st.metric("Most Recent", f"{progress_df['final_score'].iloc[-1]:.1f}%")
            with col3:
                improvement = progress_df['final_score'].iloc[-1] - progress_df['final_score'].iloc[0]
                st.metric("Improvement", f"{improvement:+.1f}%", delta=f"{improvement:+.1f}%")
            with col4:
                st.metric("Total Attempts", len(progress_df))
        else:
            st.info("Complete more case studies to see your progress over time")
    else:
        st.info("No performance data available")

# TAB 3: CASE STUDIES
with tabs[2]:
    st.markdown("## 📚 My Case Study Performance")
    
    if student_user_id or (student_perf_df is not None and not student_perf_df.empty):
        user_filter = student_user_id if student_user_id else student_perf_df.iloc[0]['student_email']
        
        my_cases_query = f"""
        SELECT 
            c.title as case_study,
            COUNT(*) as attempts,
            ROUND(AVG(g.final_score), 2) as avg_score,
            ROUND(MAX(g.final_score), 2) as best_score,
            MAX(g.timestamp) as last_attempt
        FROM `{DATASET_ID}.grades` g
        JOIN `{DATASET_ID}.casestudy` c ON g.case_study_id = c.case_study_id
        WHERE g.user_id = '{user_filter}'
            AND g.final_score IS NOT NULL
        GROUP BY c.title
        ORDER BY last_attempt DESC
        """
        
        my_cases_df = get_cached_query(my_cases_query) if student_user_id else None
        
        if my_cases_df is not None and not my_cases_df.empty:
            st.markdown("### 📊 My Case Study Summary")
            st.dataframe(my_cases_df, use_container_width=True, height=300)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Average Scores")
                fig = plot_bar_chart(my_cases_df, 'case_study', 'avg_score',
                                   'My Average by Case Study',
                                   orientation='h', height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🏆 Best Scores")
                fig = plot_bar_chart(my_cases_df, 'case_study', 'best_score',
                                   'My Best Score by Case Study',
                                   orientation='h', height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No case study data available")
        
        # Available case studies
        st.markdown("---")
        st.markdown("### 📖 Available Case Studies")
        
        all_cases_query = f"""
        SELECT 
            title,
            description
        FROM `{DATASET_ID}.casestudy`
        ORDER BY title
        """
        
        all_cases_df = get_cached_query(all_cases_query)
        
        if all_cases_df is not None and not all_cases_df.empty:
            for idx, case in all_cases_df.iterrows():
                with st.expander(f"📘 {case['title']}"):
                    st.markdown(case['description'] if case['description'] else "No description available")
                    
                    # Check if student has attempted
                    if my_cases_df is not None and case['title'] in my_cases_df['case_study'].values:
                        case_data = my_cases_df[my_cases_df['case_study'] == case['title']].iloc[0]
                        st.success(f"✅ Completed {case_data['attempts']} times | Best: {case_data['best_score']:.1f}%")
                    else:
                        st.info("📝 Not yet attempted")
    else:
        st.info("No case study data available")

# TAB 4: CONVERSATIONS
with tabs[3]:
    st.markdown("## 💬 My Conversation History")
    
    if student_user_id or (student_perf_df is not None and not student_perf_df.empty):
        user_filter = student_user_id if student_user_id else student_perf_df.iloc[0]['student_email']
        
        conversations_query = f"""
        SELECT 
            conv.conversation_id,
            conv.timestamp,
            c.title as case_study,
            conv.session_attempt,
            g.final_score,
            g.performance_summary
        FROM `{DATASET_ID}.conversation` conv
        JOIN `{DATASET_ID}.casestudy` c ON conv.case_study_id = c.case_study_id
        LEFT JOIN `{DATASET_ID}.grades` g ON conv.conversation_id = g.conversation_id
        WHERE conv.user_id = '{user_filter}'
        ORDER BY conv.timestamp DESC
        LIMIT 50
        """
        
        conversations_df = get_cached_query(conversations_query) if student_user_id else None
        
        if conversations_df is not None and not conversations_df.empty:
            st.markdown(f"### 📝 Recent Conversations ({len(conversations_df)} total)")
            
            # Filter by case study
            case_filter = st.selectbox(
                "Filter by case study",
                ['All'] + conversations_df['case_study'].unique().tolist()
            )
            
            filtered_conv = conversations_df if case_filter == 'All' else conversations_df[conversations_df['case_study'] == case_filter]
            
            # Display conversations
            for idx, conv in filtered_conv.iterrows():
                with st.expander(f"📅 {conv['timestamp'].strftime('%Y-%m-%d %H:%M')} - {conv['case_study']} (Attempt {conv['session_attempt']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if pd.notna(conv['performance_summary']):
                            st.markdown("**Performance Summary:**")
                            st.info(conv['performance_summary'])
                        else:
                            st.info("No performance summary available")
                    
                    with col2:
                        if pd.notna(conv['final_score']):
                            st.metric("Score", f"{conv['final_score']:.1f}%")
                        else:
                            st.metric("Score", "Not graded")
                    
                    # View full transcript button
                    if st.button(f"📖 View Transcript", key=f"transcript_{conv['conversation_id']}"):
                        st.session_state.selected_conversation = conv['conversation_id']
            
            # Show selected transcript
            if 'selected_conversation' in st.session_state:
                st.markdown("---")
                st.markdown("### 📖 Full Transcript")
                
                transcript_df = get_cached_query(
                    QueryBuilder.get_conversation_transcript(st.session_state.selected_conversation)
                )
                
                if transcript_df is not None and not transcript_df.empty:
                    transcript_data = transcript_df.iloc[0]
                    
                    st.markdown(f"**Conversation ID:** `{transcript_data['conversation_id']}`")
                    st.markdown(f"**Timestamp:** {transcript_data['timestamp']}")
                    
                    if pd.notna(transcript_data['transcript']):
                        st.text_area("Transcript", transcript_data['transcript'], height=400)
                    else:
                        st.info("No transcript available")
                    
                    # Grades
                    if pd.notna(transcript_data['final_score']):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Final Score", f"{transcript_data['final_score']:.1f}%")
                        with col2:
                            st.metric("Communication", f"{transcript_data['communication']:.1f}%")
                        with col3:
                            st.metric("Comprehension", f"{transcript_data['comprehension']:.1f}%")
                        with col4:
                            st.metric("Critical Thinking", f"{transcript_data['critical_thinking']:.1f}%")
        else:
            st.info("No conversations yet. Start a case study to begin!")
    else:
        st.info("No conversation data available")

# TAB 5: ACHIEVEMENTS
with tabs[4]:
    st.markdown("## 🏆 My Achievements & Milestones")
    
    if student_perf_df is not None and not student_perf_df.empty:
        my_data = student_perf_df.iloc[0]
        
        # Calculate achievements
        achievements = []
        
        # Score-based achievements
        if my_data['avg_score'] >= 90:
            achievements.append({
                'icon': '🌟',
                'title': 'Excellence',
                'description': 'Maintained 90%+ average',
                'level': 'gold'
            })
        elif my_data['avg_score'] >= 80:
            achievements.append({
                'icon': '⭐',
                'title': 'High Achiever',
                'description': 'Maintained 80%+ average',
                'level': 'silver'
            })
        
        # Attempt-based achievements
        if my_data['attempts'] >= 10:
            achievements.append({
                'icon': '🎓',
                'title': 'Dedicated Learner',
                'description': 'Completed 10+ attempts',
                'level': 'gold'
            })
        elif my_data['attempts'] >= 5:
            achievements.append({
                'icon': '📚',
                'title': 'Active Student',
                'description': 'Completed 5+ attempts',
                'level': 'silver'
            })
        
        # Rubric-based achievements
        if my_data['avg_communication'] >= 90:
            achievements.append({
                'icon': '💬',
                'title': 'Communication Master',
                'description': '90%+ in Communication',
                'level': 'gold'
            })
        
        if my_data['avg_critical_thinking'] >= 90:
            achievements.append({
                'icon': '🧠',
                'title': 'Critical Thinker',
                'description': '90%+ in Critical Thinking',
                'level': 'gold'
            })
        
        # Display achievements
        if achievements:
            st.markdown("### 🎉 Unlocked Achievements")
            
            cols = st.columns(3)
            for idx, achievement in enumerate(achievements):
                with cols[idx % 3]:
                    if achievement['level'] == 'gold':
                        st.success(f"{achievement['icon']} **{achievement['title']}**\n\n{achievement['description']}")
                    else:
                        st.info(f"{achievement['icon']} **{achievement['title']}**\n\n{achievement['description']}")
        else:
            st.info("Keep learning to unlock achievements!")
        
        st.markdown("---")
        
        # Milestones
        st.markdown("### 🎯 Next Milestones")
        
        milestones = []
        
        if my_data['avg_score'] < 90:
            gap = 90 - my_data['avg_score']
            milestones.append(f"📈 {gap:.1f}% away from Excellence (90%+ average)")
        
        if my_data['attempts'] < 10:
            gap = 10 - my_data['attempts']
            milestones.append(f"📚 {gap} more attempts to become a Dedicated Learner")
        
        if my_data['avg_communication'] < 90:
            gap = 90 - my_data['avg_communication']
            milestones.append(f"💬 {gap:.1f}% away from Communication Master")
        
        if my_data['avg_critical_thinking'] < 90:
            gap = 90 - my_data['avg_critical_thinking']
            milestones.append(f"🧠 {gap:.1f}% away from Critical Thinker")
        
        if milestones:
            for milestone in milestones:
                st.info(milestone)
        else:
            st.success("🎉 You've achieved all current milestones! Keep up the excellent work!")
    else:
        st.info("Complete case studies to unlock achievements!")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Student Dashboard v1.0")
