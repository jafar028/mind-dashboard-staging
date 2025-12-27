"""
Developer Dashboard
AI Performance, API Analytics & Debugging Tools
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime

# Direct imports from utils modules
from utils.auth_handler import (
    require_authentication, show_user_info_sidebar, get_current_user
)
from utils.chart_components import (
    create_metric_cards, plot_scatter, plot_funnel, plot_bar_chart,
    plot_box_plot, create_multi_line_chart, export_dataframe_to_csv
)
from utils.query_builder import QueryBuilder
from config.database import get_cached_query, run_query, DATASET_ID
from config.auth import can_access_page

# Page config
st.set_page_config(
    page_title="Developer Dashboard | MIND Platform",
    page_icon="👨‍💻",
    layout="wide"
)

# Authentication check
require_authentication()

# Check role permission
user = get_current_user()
if not can_access_page(user['role'], 'Developer'):
    st.error("⛔ Access Denied: Developer privileges required")
    st.stop()

# Sidebar
show_user_info_sidebar()

# Header
st.title("👨‍💻 Developer Dashboard")
st.markdown("### AI Performance, API Analytics & System Debugging")
st.markdown("---")

# Filters
with st.sidebar:
    st.markdown("### 🔧 Developer Tools")
    
    time_window = st.selectbox(
        "Analysis Window",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
        index=2
    )
    
    st.markdown("---")
    st.markdown("### 🐛 Debug Tools")
    
    # Trace lookup
    trace_id = st.text_input("Enter Trace ID", placeholder="trace-xxx-xxx")
    if st.button("🔍 Lookup Trace") and trace_id:
        st.session_state.trace_lookup = trace_id

# Main content
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
    
    # System health metrics
    system_health_df = get_cached_query(QueryBuilder.get_system_health())
    token_usage_df = get_cached_query(QueryBuilder.get_ai_token_usage())
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if system_health_df is not None and not system_health_df.empty:
            st.metric("Total Requests", f"{system_health_df['total_requests'].iloc[0]:,}")
        else:
            st.metric("Total Requests", "N/A")
    
    with col2:
        if system_health_df is not None and not system_health_df.empty:
            success_rate = ((system_health_df['total_requests'].iloc[0] - system_health_df['error_count'].iloc[0]) / 
                          system_health_df['total_requests'].iloc[0] * 100) if system_health_df['total_requests'].iloc[0] > 0 else 0
            st.metric("Success Rate", f"{success_rate:.2f}%")
        else:
            st.metric("Success Rate", "N/A")
    
    with col3:
        if system_health_df is not None and not system_health_df.empty:
            st.metric("Avg Latency", f"{system_health_df['avg_response_time'].iloc[0]:.0f}ms")
        else:
            st.metric("Avg Latency", "N/A")
    
    with col4:
        if token_usage_df is not None and not token_usage_df.empty:
            total_tokens = token_usage_df['total_tokens'].iloc[0] if token_usage_df['total_tokens'].iloc[0] else 0
            st.metric("Total Tokens", f"{total_tokens:,.0f}")
        else:
            st.metric("Total Tokens", "N/A")
    
    with col5:
        if token_usage_df is not None and not token_usage_df.empty:
            models = token_usage_df['models_used'].iloc[0] if token_usage_df['models_used'].iloc[0] else 0
            st.metric("AI Models", f"{models}")
        else:
            st.metric("AI Models", "N/A")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Request Success Rate")
        if system_health_df is not None and not system_health_df.empty:
            success_count = system_health_df['total_requests'].iloc[0] - system_health_df['error_count'].iloc[0]
            error_count = system_health_df['error_count'].iloc[0]
            
            funnel_df = pd.DataFrame({
                'stage': ['Total Requests', 'Successful', 'Errors'],
                'count': [system_health_df['total_requests'].iloc[0], success_count, error_count]
            })
            
            fig = plot_funnel(funnel_df, 'count', 'stage', 
                            'Request Processing Funnel', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No request data available")
    
    with col2:
        st.markdown("### ⚡ Latency Distribution")
        if system_health_df is not None and not system_health_df.empty:
            latency_df = pd.DataFrame({
                'Metric': ['Average', 'P95', 'P99'],
                'Latency (ms)': [
                    system_health_df['avg_response_time'].iloc[0],
                    system_health_df['p95_latency'].iloc[0],
                    system_health_df['p99_latency'].iloc[0]
                ]
            })
            
            fig = plot_bar_chart(latency_df, 'Metric', 'Latency (ms)',
                               'Response Time Metrics', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No latency data available")

# TAB 2: AI PERFORMANCE
with tabs[1]:
    st.markdown("## 🤖 AI Performance Analytics")
    
    # AI Token metrics
    token_usage_df = get_cached_query(QueryBuilder.get_ai_token_usage())
    
    if token_usage_df is not None and not token_usage_df.empty:
        col1, col2, col3 = st.columns(3)
        
        total_tokens = token_usage_df['total_tokens'].iloc[0] if token_usage_df['total_tokens'].iloc[0] else 0
        input_tokens = token_usage_df['input_tokens'].iloc[0] if token_usage_df['input_tokens'].iloc[0] else 0
        output_tokens = token_usage_df['output_tokens'].iloc[0] if token_usage_df['output_tokens'].iloc[0] else 0
        
        with col1:
            st.metric("Input Tokens", f"{input_tokens:,.0f}")
        with col2:
            st.metric("Output Tokens", f"{output_tokens:,.0f}")
        with col3:
            ratio = output_tokens / input_tokens if input_tokens > 0 else 0
            st.metric("Output/Input Ratio", f"{ratio:.2f}x")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Model Distribution")
        model_dist_df = get_cached_query(QueryBuilder.get_ai_model_distribution())
        if model_dist_df is not None and not model_dist_df.empty:
            st.dataframe(model_dist_df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(model_dist_df, 'model', 'request_count',
                               'Requests by Model', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No AI model data available")
    
    with col2:
        st.markdown("### 📊 Token Distribution")
        if model_dist_df is not None and not model_dist_df.empty:
            fig = plot_bar_chart(model_dist_df, 'model', 'total_tokens',
                               'Token Usage by Model', height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Token scatter plot
            st.markdown("### 🔍 Input vs Output Tokens")
            # This would need individual request data
            st.info("Scatter plot of token usage - requires request-level data")
        else:
            st.info("No token distribution data available")
    
    st.markdown("---")
    st.markdown("### 💰 Cost Analysis")
    
    if token_usage_df is not None and not token_usage_df.empty:
        # Cost estimation (example rates)
        cost_data = pd.DataFrame({
            'Model': ['Claude Sonnet', 'Claude Opus', 'Other'],
            'Input Cost ($/1M)': [3.0, 15.0, 5.0],
            'Output Cost ($/1M)': [15.0, 75.0, 15.0]
        })
        
        st.dataframe(cost_data, use_container_width=True)
        
        estimated_cost = (total_tokens / 1_000_000) * 15.0  # Average rate
        st.info(f"**Estimated Total Cost:** ${estimated_cost:,.2f}")

# TAB 3: API ANALYTICS
with tabs[2]:
    st.markdown("## ⚡ API Performance Analytics")
    
    # Response time by route
    route_perf_df = get_cached_query(QueryBuilder.get_response_time_by_route())
    
    if route_perf_df is not None and not route_perf_df.empty:
        st.markdown("### 📊 API Route Performance")
        st.dataframe(route_perf_df, use_container_width=True, height=400)
        export_dataframe_to_csv(route_perf_df, "api_route_performance.csv")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Request Volume by Route")
            fig = plot_bar_chart(route_perf_df.head(10), 'http_route', 'request_count',
                               'Top Routes by Request Count',
                               orientation='h', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ P95 Latency by Route")
            fig = plot_bar_chart(route_perf_df.head(10), 'http_route', 'p95_latency',
                               'P95 Latency by Route',
                               orientation='h', height=400)
            
            # Add SLO line
            fig.add_hline(y=2000, line_dash="dash", line_color="red",
                         annotation_text="SLO: 2000ms")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No API performance data available")
    
    st.markdown("---")
    st.markdown("### 🐛 Error Analysis")
    
    error_log_df = get_cached_query(QueryBuilder.get_error_log(100))
    if error_log_df is not None and not error_log_df.empty:
        # Error rate by route
        error_by_route = error_log_df['http_route'].value_counts().reset_index()
        error_by_route.columns = ['route', 'error_count']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = plot_bar_chart(error_by_route.head(10), 'route', 'error_count',
                               'Errors by Route',
                               orientation='h', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Error rate by status code
            status_dist = error_log_df['http_status_code'].value_counts().reset_index()
            status_dist.columns = ['status_code', 'count']
            
            fig = plot_bar_chart(status_dist, 'status_code', 'count',
                               'Errors by Status Code', height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No errors in the selected time window!")

# TAB 4: TRACE DEBUGGER
with tabs[3]:
    st.markdown("## 🔍 Request Trace Debugger")
    
    # Trace lookup from sidebar
    if 'trace_lookup' in st.session_state:
        trace_id = st.session_state.trace_lookup
        
        st.markdown(f"### 📝 Trace: `{trace_id}`")
        
        trace_df = get_cached_query(QueryBuilder.get_trace_details(trace_id))
        
        if trace_df is not None and not trace_df.empty:
            # Display trace metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Spans", len(trace_df))
            with col2:
                if 'derived_response_time_ms' in trace_df.columns:
                    st.metric("Total Time", f"{trace_df['derived_response_time_ms'].sum():.0f}ms")
            with col3:
                if 'derived_is_error' in trace_df.columns:
                    has_error = trace_df['derived_is_error'].any()
                    st.metric("Status", "❌ Error" if has_error else "✅ Success")
            
            st.markdown("---")
            
            # Detailed trace information
            st.markdown("### 🔬 Trace Details")
            st.dataframe(trace_df, use_container_width=True, height=400)
            export_dataframe_to_csv(trace_df, f"trace_{trace_id}.csv")
            
            # Show attributes if available
            if 'attributes' in trace_df.columns:
                st.markdown("### 📋 Attributes")
                for idx, row in trace_df.iterrows():
                    if row['attributes']:
                        with st.expander(f"Span: {row['span_name']}"):
                            st.json(row['attributes'])
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
        
        # Show recent traces
        st.markdown("### 🕐 Recent Traces")
        recent_traces_query = f"""
        SELECT DISTINCT
            trace_id,
            MIN(created_at) as start_time,
            COUNT(*) as span_count,
            BOOL_OR(derived_is_error) as has_error,
            SUM(derived_response_time_ms) as total_time_ms
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE trace_id IS NOT NULL
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
        GROUP BY trace_id
        ORDER BY start_time DESC
        LIMIT 20
        """
        
        recent_traces_df = get_cached_query(recent_traces_query)
        if recent_traces_df is not None and not recent_traces_df.empty:
            st.dataframe(recent_traces_df, use_container_width=True)
        else:
            st.info("No recent traces found")

# TAB 5: TELEMETRY
with tabs[4]:
    st.markdown("## 📡 Backend Telemetry")
    
    st.markdown("### 📊 Telemetry Statistics")
    
    telemetry_stats_query = f"""
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT trace_id) as unique_traces,
        COUNT(DISTINCT service_name) as services,
        MIN(created_at) as oldest_record,
        MAX(created_at) as newest_record
    FROM `{DATASET_ID}.backend_telemetry`
    """
    
    stats_df = get_cached_query(telemetry_stats_query)
    
    if stats_df is not None and not stats_df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Records", f"{stats_df['total_records'].iloc[0]:,}")
        with col2:
            st.metric("Unique Traces", f"{stats_df['unique_traces'].iloc[0]:,}")
        with col3:
            st.metric("Services", f"{stats_df['services'].iloc[0]:,}")
        with col4:
            oldest = pd.to_datetime(stats_df['oldest_record'].iloc[0])
            st.metric("Oldest Record", oldest.strftime('%Y-%m-%d'))
        with col5:
            newest = pd.to_datetime(stats_df['newest_record'].iloc[0])
            st.metric("Newest Record", newest.strftime('%Y-%m-%d'))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Service Distribution")
        service_query = f"""
        SELECT 
            service_name,
            COUNT(*) as request_count
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE service_name IS NOT NULL
        GROUP BY service_name
        ORDER BY request_count DESC
        """
        
        service_df = get_cached_query(service_query)
        if service_df is not None and not service_df.empty:
            fig = plot_bar_chart(service_df, 'service_name', 'request_count',
                               'Requests by Service', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No service data available")
    
    with col2:
        st.markdown("### 🌍 Environment Distribution")
        env_query = f"""
        SELECT 
            deployment_environment,
            COUNT(*) as request_count
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE deployment_environment IS NOT NULL
        GROUP BY deployment_environment
        ORDER BY request_count DESC
        """
        
        env_df = get_cached_query(env_query)
        if env_df is not None and not env_df.empty:
            fig = plot_bar_chart(env_df, 'deployment_environment', 'request_count',
                               'Requests by Environment', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No environment data available")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developer Dashboard v1.0")
