#  **Alerting & Notification Platform**

A comprehensive FastAPI-based alerting system with admin controls, user management, and intelligent notification delivery. Built with clean OOP design patterns, extensible architecture, and production-ready features.

## **Features**

## **Admin Capabilities**

* Create unlimited alerts with configurable severity (Info/Warning/Critical)  
* Define visibility: Organization-wide, Team-specific, or User-specific  
* Set reminder frequency (default: every 2 hours)  
* Configure start and expiry times  
* Comprehensive analytics and reporting  
* Update, archive, and manage all alerts

## **User Experience**

* Receive alerts based on visibility settings  
* Snooze alerts until end of day (resumes next day automatically)  
* Mark alerts as read/unread  
* Personal alert history and status tracking  
* Automatic 2-hour reminder system until acknowledged

## **Technical Excellence**

* Clean OOP architecture with design patterns  
* Extensible notification channels (In-App, Email, SMS ready)  
* Real-time analytics dashboard  
* Future-ready authentication system  
* Production-grade FastAPI implementation

## **Quick Start**

*`# Clone the repository`*  
`git clone https://github.com/shubhamprasad318/Alerting-notification_platform`  
`cd alerting_platform`

*`# Set up virtual environment`*  
`python -m venv venv`  
`source venv/bin/activate  # Linux/Mac`  
*`# or`*  
`venv\Scripts\activate     # Windows`

*`# Install dependencies`*  
`pip install -r requirements.txt`

*`# Create database and seed data`* 
`python dummy_data.py`

*`# Start the server`*  
`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## **📦 Installation**

## **Prerequisites**

* Python 3.11+  
* PostgreSQL (recommended) or SQLite (for development)  
* Virtual environment tool

##  **Install Dependencies**

Create **requirements.txt:**

`fastapi==0.104.1`  
`uvicorn[standard]==0.24.0`  
`sqlalchemy==2.0.23`  
`alembic==1.12.1`  
`pydantic==2.5.0`  
`python-multipart==0.0.6`  
`asyncpg==0.29.0`  
`psycopg2-binary==2.9.9`  
`apscheduler==3.10.4`  
`python-jose[cryptography]==3.3.0`  
`passlib[bcrypt]==1.7.4`

## **Initialize Database**

*`# Create tables and seed initial data`*  
`python dummy_data.py`

## **Admin Endpoints**

## **POST /admin/alerts**

**Create a new alert**

Organization-wide Alert:

curl \-X POST "http://localhost:8000/admin/alerts" \\

\-H "Content-Type: application/json" \\  
\-d '{  
  "title": "System Maintenance Scheduled",   
  "message": "Maintenance window tonight from 2-4 AM EST",  
  "severity": "warning",  
  "visibility\_type": "organization"  
}'

Team-specific Alert:  
curl \-X POST "http://localhost:8000/admin/alerts" \\  
\-H "Content-Type: application/json" \\  
\-d '{  
  "title": "Code Review Required",  
  "message": "Please review pending PRs before EOD",  
  "severity": "info",   
  "visibility\_type": "team",  
  "target\_team\_id": 1,  
  "expiry\_time": "2025-09-25T18:00:00"  
}'

User-specific Alert:  
curl \-X POST "http://localhost:8000/admin/alerts" \\  
\-H "Content-Type: application/json" \\  
\-d '{  
  "title": "Performance Review Due",  
  "message": "Complete quarterly review by Friday",  
  "severity": "warning",  
  "visibility\_type": "user",   
  "target\_user\_id": 2  
}'

Sample Response:  
{  
  "id": 1,  
  "title": "System Maintenance Scheduled",  
  "message": "Maintenance window tonight from 2-4 AM EST",   
  "severity": "warning",  
  "visibility\_type": "organization",  
  "is\_active": true,  
  "created\_at": "2025-09-18T18:30:00",  
  "updated\_at": "2025-09-18T18:30:00"  
}

## **GET /admin/alerts**

Get all alerts created by admin with optional filters

Query Parameters:

* severity: Filter by severity (info, warning, critical)  
* is\_active: Filter by active status (true, false)  
* visibility\_type: Filter by visibility (organization, team, user)

Examples:

*`# Get all admin alerts`*  
`curl -X GET "http://localhost:8000/admin/alerts"`

*`# Get only critical alerts`*  
`curl -X GET "http://localhost:8000/admin/alerts?severity=critical"`

*`# Get active team alerts`*  
`curl -X GET "http://localhost:8000/admin/alerts?visibility_type=team&is_active=true"`

## **PUT /admin/alerts/{alert\_id}**

Update an existing alert

`curl -X PUT "http://localhost:8000/admin/alerts/1" \`  
`-H "Content-Type: application/json" \`  
`-d '{`  
  `"title": "UPDATED: System Maintenance Extended",`  
  `"severity": "critical"`  
`}'`

## **DELETE /admin/alerts/{alert\_id}**

Archive an alert

`curl -X DELETE "http://localhost:8000/admin/alerts/1"`

Response:

`{`  
  `"message": "Alert archived successfully"`  
`}`

## **POST /admin/alerts/trigger-reminders**

Manually trigger reminder processing (useful for testing)

`curl -X POST "http://localhost:8000/admin/alerts/trigger-reminders"`

## **User Endpoints**

## **GET /user/alerts**

Get alerts visible to the current user

`curl -X GET "http://localhost:8000/user/alerts"`

Response:

`[`  
  `{`  
    `"alert": {`  
      `"id": 1,`  
      `"title": "System Maintenance Scheduled",`  
      `"message": "Maintenance window tonight from 2-4 AM EST",`  
      `"severity": "warning"`  
    `},`  
    `"state": "unread",`  
    `"snoozed_until": null,`  
    `"read_at": null`  
  `}`  
`]`

## **POST /user/alerts/{alert\_id}/read**

Mark an alert as read

`curl -X POST "http://localhost:8000/user/alerts/1/read"`

Response:

`{`

  `"message": "Alert marked as read"`

`}`

## **POST /user/alerts/{alert\_id}/snooze**

Snooze an alert until end of day

`curl -X POST "http://localhost:8000/user/alerts/1/snooze"`

Response:

`{`

  `"message": "Alert snoozed until end of day"`

`}`

---

## **Analytics Endpoints**

## **GET /analytics/system**

Get comprehensive system-wide metrics

`curl -X GET "http://localhost:8000/analytics/system"`

Response:

`{`  
  `"total_alerts_created": 15,`  
  `"active_alerts": 8,`  
  `"alerts_delivered": 45,`  
  `"alerts_read": 23,`  
  `"delivery_success_rate": 100.0,`  
  `"severity_breakdown": {`  
    `"critical": 3,`  
    `"warning": 7,`  
    `"info": 5`  
  `},`  
  `"alert_states": {`  
    `"read": 23,`  
    `"unread": 15,`  
    `"snoozed": 7`  
  `},`  
  `"recent_activity": {`  
    `"alerts_last_7_days": 12`  
  `}`  
`}`

## **GET /analytics/alerts/{alert\_id}**

Get performance metrics for a specific alert

`curl -X GET "http://localhost:8000/analytics/alerts/1"`

Response:

`{`  
  `"alert_id": 1,`  
  `"alert_title": "System Maintenance Scheduled",`  
  `"total_target_users": 10,`  
  `"total_deliveries": 20,`  
  `"state_breakdown": {`  
    `"read": 6,`  
    `"unread": 2,`   
    `"snoozed": 2`  
  `},`  
  `"engagement_rate": 80.0`  
`}`

## **GET /analytics/users/engagement**

Get user engagement metrics

`curl -X GET "http://localhost:8000/analytics/users/engagement"`

Response:

`[`  
  `{`  
    `"user_id": 1,`  
    `"user_name": "John Developer",`  
    `"total_alerts": 15,`  
    `"read_count": 12,`  
    `"read_rate": 80.0`  
  `}`  
`]`

##  **Testing Examples**

## **Complete Testing Workflow**

## **1\. Create Test Alerts**

*`# Critical production alert`*  
`curl -X POST "http://localhost:8000/admin/alerts" \`  
`-H "Content-Type: application/json" \`  
`-d '{`  
  `"title": "CRITICAL: Database Connection Lost",`  
  `"message": "Production database is not responding. Immediate attention required!",`  
  `"severity": "critical",`  
  `"visibility_type": "organization"`  
`}'`  
*`# Team meeting reminder`*

`curl -X POST "http://localhost:8000/admin/alerts" \`  
`-H "Content-Type: application/json" \`  
`-d '{`  
  `"title": "Sprint Planning Meeting",`  
  `"message": "Engineering sprint planning tomorrow at 10 AM",`  
  `"severity": "info",`  
  `"visibility_type": "team",`  
  `"target_team_id": 1`  
`}'`

## **2\. User Interactions**

*`# Check what alerts user sees`*

`curl -X GET "http://localhost:8000/user/alerts"`

*`# Mark critical alert as read`*

`curl -X POST "http://localhost:8000/user/alerts/1/read"`

*`# Snooze meeting reminder`*

`curl -X POST "http://localhost:8000/user/alerts/2/snooze"`

## **3\. Test Reminder System**

*`# Trigger reminders manually (for testing)`*

`curl -X POST "http://localhost:8000/admin/alerts/trigger-reminders"`

*`# Check analytics after interactions`*

`curl -X GET "http://localhost:8000/analytics/system"`

## **4\. Admin Management**

*`# Update alert severity`*

`curl -X PUT "http://localhost:8000/admin/alerts/1" \`

`-H "Content-Type: application/json" \`

`-d '{`

  `"title": "RESOLVED: Database Connection Restored",`

  `"severity": "info"`

`}'`

*`# Archive resolved alert`*

`curl -X DELETE "http://localhost:8000/admin/alerts/1"`

## **Database Schema**

sql

*`-- Core entities`*  
`Users (id, name, email, role)`  
`Teams (id, name, description)`  
`Alerts (id, title, message, severity, visibility_type, target_*)`

*`-- Relationships`*    
`UserTeams (user_id, team_id)`  
`UserAlertPreferences (user_id, alert_id, state, snoozed_until, read_at)`  
`NotificationDeliveries (alert_id, user_id, status, delivered_at)`

