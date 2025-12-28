# MIND Platform Analytics Dashboard

**Version:** 1.0  
**Status:** Production-Ready  
**Last Updated:** December 2025

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
11. [Future Enhancements](#future-enhancements)

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
- Responsive dark-themed UI
- Comprehensive data export capabilities
- Production-ready error handling

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
│   ├── 1_Admin_FIXED.py           # Administrator dashboard
│   ├── 2_Developer_STANDALONE.py  # Developer dashboard
│   ├── 3_Faculty_STANDALONE.py    # Faculty dashboard
│   └── 4_Student_STANDALONE.py    # Student dashboard
├── utils/                          # Shared utilities
│   ├── auth_handler.py            # Authentication logic
│   ├── logo_handler.py            # Branding assets
│   └── chart_components.py        # Visualization components
├── config/                         # Configuration modules
│   ├── auth.py                    # Role permissions
│   └── database.py                # BigQuery connection
├── assets/                         # Static resources
│   ├── miva_logo_dark.png         # Logo (dark mode)
│   └── miva_logo_light.png        # Logo (light mode)
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python version specification
└── .streamlit/
    └── secrets.toml               # Credentials (not in repo)
```

---

## Features by Role

### Administrator Dashboard

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

---

### Developer Dashboard

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

### Faculty Dashboard

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
- Color-coded performance indicators (green/yellow/red)
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

### Student Dashboard

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
   - Paste GCP service account credentials

3. **Deploy:**
   - Click "Deploy" button
   - Streamlit Cloud will automatically build and deploy
   - Access at: `https://your-app-name.streamlit.app`

### Adding Logo Assets (Optional)

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

---

## Database Schema

### Overview

The dashboard connects to the `gen-lang-client-0625543859.mind_analytics` BigQuery dataset in the `europe-west3` region.

### Critical Schema Notes

**Important:** The actual BigQuery schema differs from documentation:

| Documented Column | Actual Column | Table |
|-------------------|---------------|-------|
| `user_id` | `user` | grades |
| `case_study_id` | `case_study` | grades |

### Core Tables

#### user
- `user_id` UUID PRIMARY KEY
- `name` TEXT NOT NULL
- `student_email` TEXT UNIQUE NOT NULL
- `role` TEXT
- `department` TEXT
- `date_added` TIMESTAMPTZ

#### grades
- `grade_id` UUID PRIMARY KEY
- `user` UUID (joins to user.user_id)
- `case_study` UUID (joins to casestudy.case_study_id)
- `final_score` NUMERIC
- `timestamp` TIMESTAMPTZ
- `_id` STRING (for counting)

**Note:** Columns `communication`, `comprehension`, `critical_thinking` do **not exist** in actual table.

#### casestudy
- `case_study_id` UUID PRIMARY KEY
- `title` TEXT NOT NULL
- `description` TEXT

#### session_analytics
- `session_id` TEXT PRIMARY KEY
- `distinct_id` TEXT
- `start_timestamp` TIMESTAMPTZ
- `session_duration_seconds` NUMERIC
- `pageview_count` INTEGER

#### backend_telemetry
- `trace_id` TEXT
- `service_name` TEXT
- `http_route` TEXT
- `http_status_code` INTEGER
- `derived_response_time_ms` NUMERIC
- `derived_is_error` BOOLEAN
- `derived_ai_model` TEXT
- `derived_ai_total_tokens` INTEGER
- `created_at` TIMESTAMPTZ

---

## Authentication & Security

### Role-Based Access Control

| Role | Admin | Developer | Faculty | Student |
|------|-------|-----------|---------|---------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Developer | ✗ | ✓ | ✗ | ✗ |
| Faculty | ✗ | ✗ | ✓ | ✗ |
| Student | ✗ | ✗ | ✗ | ✓ |

### Security Best Practices

1. **Password Storage:** bcrypt hashing with salt (cost factor: 10)
2. **Session Management:** Server-side storage, automatic timeout
3. **BigQuery Security:** Service account with read-only permissions
4. **Input Validation:** Parameterized queries prevent SQL injection

---

## Configuration

### Environment Variables

Configuration managed through `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n"
client_email = "service-account@project.iam.gserviceaccount.com"
# ... (additional GCP fields)
```

---

## Troubleshooting

### Common Issues

#### "Query failed: Name [column] not found"

**Solution:** Verify column names:
- Use `grades.user` not `grades.user_id`
- Use `grades.case_study` not `grades.case_study_id`

#### "division by zero"

**Solution:** Use `SAFE_DIVIDE` in queries:
```sql
SAFE_DIVIDE(COUNT(*), TOTAL) * 100
```

Add NULL checks:
```python
if df is not None and not df.empty and pd.notna(df['column'].iloc[0]):
    # Process data
```

#### "ModuleNotFoundError: scipy"

**Solution:** Add to requirements.txt:
```bash
echo "scipy>=1.11.0" >> requirements.txt
```

---

## Future Enhancements

### Planned Features

- **Predictive Analytics:** ML-based student success prediction
- **Custom Report Builder:** Drag-and-drop report creation
- **LMS Integration:** Direct integration with Canvas, Moodle
- **Automated Reporting:** Scheduled email reports
- **API Development:** RESTful API for external systems

### Known Limitations

1. **Scalability:** Optimized for institutions with <10,000 students
2. **Data Lag:** 1-hour cache introduces slight delay
3. **Mobile:** Optimized for desktop; limited mobile UX
4. **Browser:** Best on Chrome/Edge

---

## Support & Contact

### Issue Reporting

Create GitHub issues with:
- Clear description
- Steps to reproduce
- Screenshots
- Browser/OS information

---

## License

Copyright © 2025 MIND Platform. A product of MIVA open University, All rights reserved.

---

**Document Version:** 2.0  
**Last Updated:** December 2025
