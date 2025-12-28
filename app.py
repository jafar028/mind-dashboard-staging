"""
MIND Platform - Educational Analytics Dashboard
Main Application Entry Point
"""

import streamlit as st
from utils.auth_handler import initialize_session_state, show_login_page, show_user_info_sidebar
from config.auth import can_access_page

# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="assets/miva_logo_dark.png",  # Will show in browser tab
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
    }
    
    /* Headers */
    h1 {
        color: #FF6B6B;
        padding-bottom: 1rem;
        border-bottom: 2px solid #FF6B6B;
    }
    
    h2 {
        color: #4ECDC4;
        margin-top: 2rem;
    }
    
    h3 {
        color: #45B7D1;
    }
    
    /* Cards and containers */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #FF6B6B;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #FF6B6B;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
    }
    
    /* DataFrames */
    .dataframe {
        border-radius: 8px;
    }
    
    /* Hide hamburger menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #262730;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FF6B6B;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ff5252;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Show login page if not authenticated
if not st.session_state.get('authenticated', False):
    show_login_page()
else:
    # Show sidebar with user info and navigation
    show_user_info_sidebar()
    
    # Main content area
    st.title("MIND Platform")
    st.markdown("### AI-Enhanced Educational Analytics Dashboard")
    
    # Welcome message with role-specific information
    user_role = st.session_state.get('user_role', 'user')
    user_name = st.session_state.get('user_name', 'User')
    
    st.markdown(f"""
    Welcome back, **{user_name}**! 
    
    You are logged in as: **{user_role.title()}**
    """)
    
    # Role-specific guidance
    if user_role == 'admin':
        st.info("""
        **Admin Dashboard Features:**
        - 📊 System health monitoring and KPIs
        - 👥 User management and activity tracking
        - 💰 AI resource consumption and costs
        - ⚙️ Platform configuration and settings
        - 📈 Comprehensive analytics across all users
        """)
    elif user_role == 'developer':
        st.info("""
        **Developer Dashboard Features:**
        - 🔧 API performance metrics and latency analysis
        - 🤖 AI model usage and token distribution
        - 🐛 Error tracking and trace debugging
        - 📡 Backend telemetry and system health
        """)
    elif user_role == 'faculty':
        st.info("""
        **Faculty Dashboard Features:**
        - 📚 Student performance analytics
        - 📊 Case study effectiveness tracking
        - 🎯 Learning outcome assessment
        - ⚠️ At-risk student identification
        - 📈 Cohort and department comparisons
        """)
    elif user_role == 'student':
        st.info("""
        **Student Dashboard Features:**
        - 📖 Personal learning journey tracking
        - 🎯 Performance across rubric categories
        - 📊 Progress comparison with class averages
        - 📝 Past conversation reviews
        - 🏆 Achievement highlights
        """)
    
    st.markdown("---")
    
    # Quick navigation
    st.markdown("### 🚀 Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if can_access_page(user_role, 'Admin'):
            if st.button("👨‍💼 Admin Dashboard", use_container_width=True):
                st.switch_page("pages/1_👨‍💼_Admin.py")
    
    with col2:
        if can_access_page(user_role, 'Developer'):
            if st.button("👨‍💻 Developer Dashboard", use_container_width=True):
                st.switch_page("pages/2_👨‍💻_Developer.py")
    
    with col3:
        if can_access_page(user_role, 'Faculty'):
            if st.button("👩‍🏫 Faculty Dashboard", use_container_width=True):
                st.switch_page("pages/3_👩‍🏫_Faculty.py")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if can_access_page(user_role, 'Student'):
            if st.button("🎓 Student Dashboard", use_container_width=True):
                st.switch_page("pages/4_🎓_Student.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>MIND Platform v1.0 | AI-Enhanced Educational Analytics</p>
            <p>Powered by BigQuery, Streamlit & Plotly</p>
        </div>
    """, unsafe_allow_html=True)
