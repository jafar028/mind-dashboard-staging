# 🎓 MIND Platform - Educational Analytics Dashboard

> **AI-Enhanced Educational Analytics Dashboard for MIVA Open University**

A comprehensive, role-based business intelligence solution designed for educational institutions using the MIND (Machine Intelligence for Nuanced Dialogue) platform. The dashboard provides real-time analytics, performance tracking, and actionable insights across four distinct user roles.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Features by Role](#features-by-role)
4. [Technical Stack](#technical-stack)
5. [Installation & Deployment](#installation--deployment)
6. [Database Schema](#database-schema)
7. [Dashboard Components](#dashboard-components)
8. [Authentication & Security](#authentication--security)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [Customization](#customization)
12. [Changelog](#changelog)
13. [Future Enhancements](#future-enhancements)

---

## Overview

The MIND Platform Analytics Dashboard is a comprehensive, role-based business intelligence solution designed for educational institutions using the MIND (AI-enhanced educational case study) platform. The dashboard provides real-time analytics, performance tracking, and actionable insights across four distinct user roles: Administrators, Developers, Faculty, and Students.

### Key Objectives

- **Institutional Analytics:** Provide administrators with comprehensive oversight of platform usage, student performance, and system health
- **Developer Insights:** Enable technical teams to monitor API performance, AI resource utilization, and system telemetry
- **Academic Analytics:** Empower faculty with student performance tracking, at-risk identification, and learning analytics
- **Student Engagement:** Give students personalized learning journeys, progress tracking, and achievement systems

### Technology Foundation

Built on Streamlit with Google BigQuery backend, the dashboard delivers institutional-grade analytics with:
- Real-time data synchronization
- Role-based access control (RBAC)
- Responsive UI with light/dark theme support
- Comprehensive data export capabilities
- Production-ready error handling

### Platform Features

- 🎨 **Theme Awareness:** Full light/dark mode support with automatic logo switching
- 🔐 **Role-Based Access Control:** Secure, role-specific dashboards
- 📊 **Real-time Analytics:** Live BigQuery integration for up-to-date insights
- 🎯 **Actionable Insights:** Performance tracking, at-risk identification, and recommendations
- 📱 **Responsive Design:** Works on desktop, tablet, and mobile devices
- 🎨 **Professional Branding:** Theme-aware MIVA logo system

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Cloud (Frontend)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Admin   │  │Developer │  │ Faculty  │  │ Student  │   │
│  │Dashboard │  │Dashboard │  │Dashboard │  │Dashboard │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └─────────────┴─────────────┴─────────────┘           │
│                          │                                   │
│              ┌───────────▼──────────┐                       │
│              │  Authentication      │                       │
│              │  & Session Management│                       │
│              └───────────┬──────────┘                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Google BigQuery  │
                   │   (Data Layer)    │
                   │                   │
                   │  • user           │
                   │  • grades         │
                   │  • casestudy      │
                   │  • sessions       │
                   │  • telemetry      │
                   └───────────────────┘
```

### Component Architecture

```
mind-platform/
├── app.py                          # Main application entry
├── pages/                          # Role-based dashboards
│   ├── 1_👨🏿‍💼_Admin.py            # Administrator dashboard
│   ├── 2_👨🏿‍💻_Developer.py        # Developer dashboard
│   ├── 3_👩🏿‍🏫_Faculty.py          # Faculty dashboard
│   └── 4_👨🏿‍🎓_Student.py          # Student dashboard
├── utils/                          # Shared utilities
│   ├── auth_handler.py            # Authentication & login page
│   ├── chart_components.py        # Visualization components
│   └── query_builder.py           # SQL query templates
├── config/                         # Configuration modules
│   ├── auth.py                    # User credentials & permissions
│   └── database.py                # BigQuery connection
├── assets/                         # Static resources
│   ├── miva_logo_dark.png         # Logo (for light theme)
│   └── miva_logo_light.png        # Logo (for dark theme)
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python version specification
└── .streamlit/
    └── secrets.toml               # Credentials (not in repo)
```

---

## Features by Role

### 👨🏿‍💼 Administrator Dashboard

**Primary Users:** System administrators, institutional leadership

**Tabs:**
1. **Overview** - Key performance indicators and institutional metrics
2. **User Analytics** - User distribution, performance by department/role
3. **Learning Metrics** - Academic performance, at-risk students, score distributions
4. **AI Resources** - Token usage, AI model distribution, cost estimation
5. **System Health** - Uptime monitoring, route performance, error tracking
6. **Settings** - System configuration and user management

**Key Features:**
- 15+ visualization types (line charts, bar charts, heatmaps, gauge charts)
- Real-time KPI tracking (active users, average grades, system uptime)
- Institutional performance analysis with score range visualizations
- Department and role-based performance comparisons
- Weekly growth and retention analytics
- CSV export on all data tables
- Comprehensive filtering (department, time range)

**Unique Capabilities:**
- Platform growth tracking (new signups vs. returning users)
- Case study engagement metrics (total completions by case)
- Weekly activity volume analysis
- At-risk student identification and reporting
- Theme-aware visualizations with automatic color adaptation

---

### 👨🏿‍💻 Developer Dashboard

**Primary Users:** Backend developers, DevOps engineers, technical staff

**Tabs:**
1. **Overview** - System health and performance metrics
2. **AI Performance** - Token usage, model distribution, cost analysis
3. **API Analytics** - Route performance, latency metrics, error tracking
4. **Trace Debugger** - Request tracing and debugging tools
5. **Telemetry** - Backend telemetry and service monitoring

**Key Features:**
- 9 comprehensive KPIs (requests, success rate, latency, tokens, models)
- P50/P95/P99 latency percentile tracking
- Error rate trending with hourly granularity
- HTTP status code distribution analysis
- Service and environment monitoring
- Trace-level debugging with full request lifecycle
- SLA monitoring (2000ms P95 latency threshold)

**Technical Metrics:**
- Request volume trending (hourly aggregation)
- Response time distribution across routes
- Token consumption by AI model
- Cost estimation ($15 per 1M tokens)
- Active user session analytics
- Grade submission correlation with system load

---

### 👩🏿‍🏫 Faculty Dashboard

**Primary Users:** Instructors, academic coordinators, teaching staff

**Tabs:**
1. **Overview** - Academic performance summary
2. **Student Performance** - Comprehensive student analytics
3. **Case Study Analytics** - Case-specific performance metrics
4. **At-Risk Students** - Early intervention identification
5. **Progress Tracking** - Weekly trends and department comparisons
6. **Individual Student** - Detailed student lookup and progression

**Key Features:**
- Adjustable at-risk threshold (configurable via slider)
- Color-coded performance indicators (🟢🟡🔴)
- Grade distribution analysis (A/B/C/D/F breakdown)
- Daily submission tracking with dual-axis charts
- Top performer and at-risk student tables
- Score range visualization (min/avg/max by case study)
- Search and sort capabilities across all tables

**Academic Insights:**
- Student percentile rankings
- Department performance comparisons
- Case study difficulty analysis (via score distributions)
- Trend analysis with moving averages
- Individual student score progression with trend lines
- Inactive student tracking (7+ days without activity)

---

### 👨🏿‍🎓 Student Dashboard

**Primary Users:** Individual learners

**Tabs:**
1. **My Overview** - Personal performance summary
2. **Progress Tracker** - Score progression and trends
3. **Case Studies** - Case-specific performance
4. **My Scores** - Comprehensive submission history
5. **Achievements** - Gamified milestone tracking
6. **Study Plan** - Personalized recommendations

**Key Features:**
- Personalized performance gauge with color-coded feedback
- Class ranking (percentile-based)
- Comparison to class average with delta indicators
- Score progression charts with 80% target line
- Recent submissions and personal best scores
- Interactive scatter plots with color-coded markers
- Achievement badge system (7 unique badges)
- Student selector dropdown (for demo/testing - RBAC coming soon)

**Gamification Elements:**
- Excellence Badge (90%+ average)
- High Performer Badge (80%+ average)
- Perfect Score Badge (100% on any assignment)
- Dedicated Learner Badge (50+ submissions)
- Active Student Badge (25+ submissions)
- Getting Started Badge (10+ submissions)
- Explorer Badge (5+ different cases)

---

## Technical Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend Framework | Streamlit | ≥1.28.0 | Web application framework |
| Database | Google BigQuery | - | Cloud data warehouse |
| Visualization | Plotly | ≥5.17.0 | Interactive charting |
| Data Processing | Pandas | ≥2.0.0 | Data manipulation |
| Authentication | bcrypt | ≥4.0.0 | Password hashing |
| Statistics | SciPy | ≥1.11.0 | Statistical analysis |

### Python Dependencies

```txt
streamlit>=1.28.0
google-cloud-bigquery>=3.11.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
bcrypt>=4.0.0
python-dateutil>=2.8.0
pyarrow>=12.0.0
db-dtypes>=1.1.0
openpyxl>=3.1.0
scipy>=1.11.0
```

### Runtime Environment

- **Python Version:** 3.11
- **Deployment Platform:** Streamlit Cloud
- **Database Location:** europe-west3 (Google Cloud)
- **Authentication Method:** Session-based with bcrypt hashing

---

## Installation & Deployment

### Prerequisites

1. **Google Cloud Project** with BigQuery API enabled
2. **Service Account** with BigQuery Data Viewer permissions
3. **Streamlit Cloud Account** (for deployment)
4. **GitHub Repository** for version control

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd mind-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets
mkdir .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials

# Run application
streamlit run app.py
```

### Streamlit Cloud Deployment

1. **Connect Repository:**
   - Navigate to Streamlit Cloud dashboard
   - Click "New app" → Connect GitHub repository
   - Select `mind-platform` repository
   - Set main file path: `app.py`

2. **Configure Secrets:**
   - In Streamlit Cloud dashboard → App Settings → Secrets
   - Paste GCP service account credentials:

```toml
[gcp_service_account]
type = "service_account"
project_id = "gen-lang-client-0625543859"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

3. **Deploy:**
   - Click "Deploy" button
   - Streamlit Cloud will automatically build and deploy
   - Access at: `https://your-app-name.streamlit.app`

### Adding Logo Assets

```bash
# Create assets directory
mkdir assets

# Add your logo files
cp /path/to/miva_logo_dark.png assets/
cp /path/to/miva_logo_light.png assets/

# Commit and push
git add assets/
git commit -m "Add MIVA branding logos"
git push
```

**Logo Specifications:**
- Format: PNG with transparent background
- Recommended width: 200-300px
- File size: <500KB
- **miva_logo_light.png** - Used in dark theme (light-colored logo)
- **miva_logo_dark.png** - Used in light theme (dark-colored logo)

---

## Database Schema

### Overview

The dashboard connects to the `gen-lang-client-0625543859.mind_analytics` BigQuery dataset in the `europe-west3` region.

### Critical Schema Notes

**Important:** The actual BigQuery schema differs from documentation in several key areas:

| Documented Column | Actual Column | Table | Notes |
|-------------------|---------------|-------|-------|
| `user_id` | `user` | grades | Foreign key reference |
| `case_study_id` | `case_study` | grades | Foreign key reference |
| `student_email` | N/A | user | Column does NOT exist |
| `attempt` | N/A | grades | Column does NOT exist |
| `communication` | N/A | grades | Not stored (calculated only) |
| `comprehension` | N/A | grades | Not stored (calculated only) |
| `critical_thinking` | N/A | grades | Not stored (calculated only) |

### Core Tables

#### user
```sql
user_id         UUID PRIMARY KEY
name            TEXT NOT NULL
department      TEXT
role            TEXT
cohort          TEXT
date_added      TIMESTAMPTZ
```

#### grades
```sql
_id             STRING (MongoDB-style ID)
user            UUID (references user.user_id)
case_study      UUID (references casestudy.case_study_id)
final_score     NUMERIC (0-100)
performance_summary  TEXT
overall_summary TEXT
timestamp       TIMESTAMPTZ
```

**Grading Formula (Documented but not stored):**
```sql
final_score = ROUND(
    0.35 × communication + 
    0.35 × comprehension + 
    0.30 × critical_thinking, 
    2
)
```

**Note:** Individual rubric scores (`communication`, `comprehension`, `critical_thinking`) are calculated during grading but **NOT stored** in BigQuery. Only the weighted `final_score` is available.

#### casestudy
```sql
case_study_id   UUID PRIMARY KEY
title           TEXT NOT NULL
description     TEXT
avatar_id       UUID
```

#### sessions
```sql
session_pk      UUID PRIMARY KEY
user_id         UUID
case_study_id   UUID
start_time      TIMESTAMPTZ
end_time        TIMESTAMPTZ
is_active       BOOLEAN
```

#### session_analytics
```sql
session_id      TEXT PRIMARY KEY
distinct_id     TEXT
start_timestamp TIMESTAMPTZ
session_duration_seconds  NUMERIC
pageview_count  INTEGER
```

#### backend_telemetry
```sql
trace_id        TEXT
service_name    TEXT
http_route      TEXT
http_status_code INTEGER
derived_response_time_ms  NUMERIC
derived_is_error BOOLEAN
derived_ai_model TEXT
derived_ai_total_tokens INTEGER
created_at      TIMESTAMPTZ
```

---

## Dashboard Components

### Theme System

**Implementation:**
- Light/Dark mode toggle (☀️/🌙 button)
- Theme stored in `st.session_state.theme`
- Automatic logo switching based on theme
- Theme-aware chart backgrounds and colors
- Persistent theme across all pages

**Theme Colors:**

**Dark Theme (Default):**
```python
{
    'background': '#0e1117',
    'secondary_bg': '#262730',
    'text': '#fafafa',
    'primary': '#4ECDC4',
    'accent': '#FF6B6B'
}
```

**Light Theme:**
```python
{
    'background': '#ffffff',
    'secondary_bg': '#f0f2f6',
    'text': '#262730',
    'primary': '#3498db',
    'accent': '#e74c3c'
}
```

### Logo Handler

**Location:** Embedded in each dashboard file and `utils/auth_handler.py`

**Implementation:**
- Base64 encoding for reliable display
- Automatic theme-based logo selection
- Graceful fallback if logos not found
- Optimized file size and loading

### Chart Components

**Location:** `utils/chart_components.py`

**Available Charts:**
- Line charts (trend analysis)
- Bar charts (comparisons)
- Pie charts (distributions)
- Scatter plots (correlations)
- Heatmaps (patterns)
- Gauge charts (KPIs)
- Box plots (distributions)
- Funnel charts (conversion)
- Radar charts (multi-dimensional)

**Features:**
- Theme-aware colors
- Interactive hover tooltips
- Export to PNG/SVG
- Responsive sizing
- Custom styling

---

## Authentication & Security

### Role-Based Access Control

| Role | Admin | Developer | Faculty | Student |
|------|-------|-----------|---------|---------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Developer | ✗ | ✓ | ✗ | ✗ |
| Faculty | ✗ | ✗ | ✓ | ✗ |
| Student | ✗ | ✗ | ✗ | ✓ |

### Default User Accounts

**Location:** `config/auth.py`

```python
# Default password for all accounts: mind2026

admin@mind.edu      # Full system access
dev@mind.edu        # Developer metrics
faculty@mind.edu    # Student analytics
student@mind.edu    # Personal performance
```

**⚠️ Security Note:** Change default passwords in production environments.

### Security Best Practices

1. **Password Storage:** bcrypt hashing with salt (cost factor: 12)
2. **Session Management:** Server-side storage, automatic timeout
3. **BigQuery Security:** Service account with read-only permissions
4. **Input Validation:** Parameterized queries prevent SQL injection
5. **Secrets Management:** Never commit `.streamlit/secrets.toml` to repository
6. **HTTPS:** All production traffic encrypted (Streamlit Cloud default)

### Adding New Users

Edit `config/auth.py`:

```python
USERS = {
    "new.user@mind.edu": {
        "name": "New User",
        "role": UserRole.FACULTY,
        "password_hash": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()),
        "departments": ["Computer Science"],
        "cohorts": ["2025"]
    }
}
```

---

## Configuration

### Database Configuration

**Location:** `config/database.py`

```python
PROJECT_ID = "gen-lang-client-0625543859"
DATASET_ID = "gen-lang-client-0625543859.mind_analytics"
LOCATION = "europe-west3"
```

### Theme Configuration

**Default Theme:** Dark mode

**To change default theme:**
Edit `utils/auth_handler.py`:
```python
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Change to 'light'
```

### Page Configuration

Each dashboard file includes:
```python
st.set_page_config(
    page_title="Dashboard Name",
    page_icon="👨🏿‍💼",  # Emoji icon
    layout="wide",
    initial_sidebar_state="expanded"
)
```

---

## Troubleshooting

### Common Issues

#### "Query failed: Name [column] not found"

**Symptom:** BigQuery error about missing column

**Solution:** Verify column names match actual schema:
- Use `grades.user` not `grades.user_id`
- Use `grades.case_study` not `grades.case_study_id`
- Don't reference `student_email`, `attempt`, or rubric columns

**Example Fix:**
```sql
-- WRONG
SELECT u.student_email, g.attempt
FROM grades g
JOIN user u ON g.user_id = u.user_id

-- CORRECT
SELECT u.name, COUNT(g._id) as submissions
FROM grades g
JOIN user u ON g.user = u.user_id
```

#### "division by zero" or NULL Errors

**Solution:** Use `SAFE_DIVIDE` and NULL checks:
```sql
SELECT SAFE_DIVIDE(COUNT(*), NULLIF(SUM(total), 0)) * 100 as percentage
```

```python
if df is not None and not df.empty and pd.notna(df['column'].iloc[0]):
    # Process data
else:
    st.info("No data available")
```

#### "ModuleNotFoundError: scipy"

**Solution:** Ensure all dependencies in requirements.txt:
```bash
echo "scipy>=1.11.0" >> requirements.txt
git add requirements.txt
git commit -m "Add scipy dependency"
git push
```

#### ImportError: Circular import in config/auth.py

**Symptom:** `ImportError` on app startup mentioning `config/auth`

**Solution:** Check line 7-8 of `config/auth.py`:
```python
# WRONG
from config.auth import USERS, get_user_permissions

# CORRECT
from typing import Dict
```

#### Navigation Buttons Failing

**Symptom:** `StreamlitAPIException` when clicking Quick Navigation

**Solution:** Ensure dashboard filenames match exactly (no `_FIXED` or `_STANDALONE` suffixes):
```python
# app.py should reference:
st.switch_page("pages/1_👨🏿‍💼_Admin.py")  # Exact filename
```

#### Theme Toggle Not Working

**Solution:** 
1. Verify both logo files exist in `/assets/` directory
2. Check file names: `miva_logo_light.png` and `miva_logo_dark.png`
3. Clear Streamlit cache: `st.cache_data.clear()`

#### Logo Not Displaying

**Solution:**
1. Verify logo files are in `/assets/` directory
2. Check file paths in code:
   ```python
   logo_path = "/mount/src/mind-platform/assets/miva_logo_light.png"
   ```
3. Ensure logos are committed to GitHub
4. Try base64 encoding fallback (already implemented)

### Debug Mode

Enable detailed error messages:
```python
# Add to top of app.py
import streamlit as st
st.set_option('client.showErrorDetails', True)
```

### Viewing Logs

**Streamlit Cloud:**
1. Go to app dashboard
2. Click "Manage app" (bottom right)
3. View real-time logs
4. Download logs for detailed analysis

**Local Development:**
```bash
streamlit run app.py --logger.level=debug
```

---

## Customization

### Branding

#### Logo Replacement

Replace files in `/assets/`:
- `miva_logo_light.png` - Used in dark theme
- `miva_logo_dark.png` - Used in light theme

**Recommended specs:**
- Format: PNG with transparency
- Size: 200px width (height auto)
- DPI: 72-150
- File size: <500KB

#### Color Scheme

Edit theme colors in each dashboard file's CSS section:

```python
# Dark theme colors
DARK_THEME = {
    'background': '#0e1117',
    'secondary_bg': '#262730',
    'text': '#fafafa',
    'primary': '#4ECDC4',
    'accent': '#FF6B6B'
}

# Light theme colors
LIGHT_THEME = {
    'background': '#ffffff',
    'secondary_bg': '#f0f2f6',
    'text': '#262730',
    'primary': '#3498db',
    'accent': '#e74c3c'
}
```

### Emoji Icons

Current icons reflect diverse representation. To change:

```python
# In filenames:
1_👨🏿‍💼_Admin.py  →  1_👨‍💼_Admin.py  # Different representation

# In page config:
st.set_page_config(
    page_icon="👨🏿‍💼",  # Change this emoji
)
```

### Adding New Dashboards

1. **Create file:** `pages/5_🔧_NewDashboard.py`

2. **Add structure:**
```python
import streamlit as st
from config.database import get_bigquery_client, DATASET_ID

st.set_page_config(
    page_title="New Dashboard",
    page_icon="🔧",
    layout="wide"
)

# Theme-aware logo
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Your dashboard code
st.title("🔧 New Dashboard")
```

3. **Update permissions:** `config/auth.py`
```python
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "pages": ["Admin", "Developer", "Faculty", "Student", "NewDashboard"],
    }
}
```

---

## Changelog

### Version 2.0.0 (December 2024)

**Major Updates:**
- ✅ Complete branding implementation with custom emoji icons
- ✅ Theme-aware MIVA logo system with automatic switching
- ✅ Login page redesign (centered, professional, hidden credentials)
- ✅ Password updated to `mind2026` across all accounts
- ✅ Navigation system fixes (base filenames, proper routing)
- ✅ Removed synthetic/estimated data (rubric scores)
- ✅ Schema corrections (student_email, attempt, rubric columns)
- ✅ Deprecated logo_handler utility (embedded approach)

**Dashboard Improvements:**
- ✅ Student dashboard with real data selector
- ✅ Universal theme toggle across all pages
- ✅ Gauge chart visibility fixes (light mode)
- ✅ Chart background theme awareness
- ✅ Comprehensive error handling

**Technical Fixes:**
- ✅ Circular import resolution in config/auth.py
- ✅ File naming standardization
- ✅ Base64 logo embedding for reliability
- ✅ Session state management improvements
- ✅ NULL value handling in all queries

**Documentation:**
- ✅ Comprehensive troubleshooting guide
- ✅ Theme system documentation
- ✅ Grading parameters explanation
- ✅ Student data access guide
- ✅ Navigation fix instructions

### Version 1.0.0 (Initial Release)

**Core Features:**
- Basic authentication system
- Four role-based dashboards
- BigQuery integration
- Plotly visualizations
- CSV export functionality

---

## Future Enhancements

### Planned Features

**Phase 1 (Q1 2025):**
- [ ] Full RBAC implementation (replace student selector)
- [ ] Add individual rubric scores to BigQuery schema
- [ ] Implement rubric performance visualizations
- [ ] Email notification system for at-risk students
- [ ] Automated weekly reports

**Phase 2 (Q2 2025):**
- [ ] **Predictive Analytics:** ML-based student success prediction
- [ ] **Custom Report Builder:** Drag-and-drop report creation
- [ ] **LMS Integration:** Direct integration with Canvas, Moodle
- [ ] **Mobile App:** Dedicated iOS/Android applications
- [ ] **Advanced Filters:** Multi-dimensional filtering system

**Phase 3 (Q3 2025):**
- [ ] **Real-time Collaboration:** Faculty-student messaging
- [ ] **Video Analytics:** Integration with recorded sessions
- [ ] **Gamification:** Advanced badge and reward systems
- [ ] **API Development:** RESTful API for external systems
- [ ] **Custom Dashboards:** User-created dashboard templates

### Known Limitations

1. **Scalability:** Optimized for institutions with <10,000 students
2. **Data Lag:** 1-hour cache introduces slight delay in metrics
3. **Mobile UX:** Optimized for desktop; limited mobile experience
4. **Browser Support:** Best performance on Chrome/Edge (latest versions)
5. **Rubric Data:** Individual rubric scores not available (only final_score)

---

## Support & Contact

### Getting Help

**Documentation:**
- This README file
- `DEPLOYMENT_GUIDE.md` - Detailed deployment steps
- `THEME_TOGGLE_FEATURE.md` - Theme system guide
- `GRADING_PARAMETERS.md` - Rubric information
- `TROUBLESHOOTING.md` - Common issues

**Issue Reporting:**
Create GitHub issues with:
- Clear description of problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Browser and OS information
- Console error logs

**Contact:**
- Technical Lead: [technical-lead@miva.edu.ng]
- MIVA IT Support: [support@miva.edu.ng]
- GitHub Issues: [repository-url]/issues

---

## License

Copyright © 2024-2025 MIND Platform. A product of MIVA Open University. All rights reserved.

This software is proprietary. Unauthorized copying, distribution, or use is strictly prohibited.

---

## Acknowledgments

- **MIVA Open University** - Project sponsorship and requirements
- **Anthropic** - Claude AI assistance in development
- **Streamlit** - Dashboard framework and hosting
- **Google Cloud** - BigQuery data warehouse infrastructure
- **Plotly** - Interactive visualization library

---

## Quick Reference

### Important URLs
- **Production:** `https://mind-platform.streamlit.app`
- **GitHub:** `https://github.com/your-org/mind-platform`
- **Documentation:** `https://github.com/your-org/mind-platform/wiki`

### Key Files
- `app.py` - Main application entry point
- `config/auth.py` - User management and RBAC
- `config/database.py` - BigQuery configuration
- `utils/auth_handler.py` - Login page implementation

### Default Credentials
```
Admin:     admin@mind.edu    / mind2026
Developer: dev@mind.edu      / mind2026
Faculty:   faculty@mind.edu  / mind2026
Student:   student@mind.edu  / mind2026
```

### Database
- **Project:** `gen-lang-client-0625543859`
- **Dataset:** `mind_analytics`
- **Location:** `europe-west3`

---

**Document Version:** 2.0  
**Last Updated:** December 28, 2025 
**Built and maintained by the Department of Research and Developmt, MIVA Open University, Nigeria**
