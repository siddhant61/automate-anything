"""
Streamlit Dashboard for OpenHPI Automation Platform.

This dashboard provides a user-friendly interface for:
- Viewing course analytics and statistics
- Accessing AI-powered insights
- Triggering automation tasks
- Monitoring system status
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="OpenHPI Automation Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")


def check_api_health() -> bool:
    """Check if the API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_ai_health() -> Dict:
    """Check AI service status."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {'enabled': False, 'status': 'error'}
    except Exception:
        return {'enabled': False, 'status': 'error'}


# Sidebar Navigation
st.sidebar.title("📚 OpenHPI Automation")
st.sidebar.markdown("---")

# Check API status
api_status = check_api_health()
if api_status:
    st.sidebar.success("✓ API Connected")
else:
    st.sidebar.error("✗ API Unavailable")
    st.sidebar.info(f"Trying to connect to: {API_BASE_URL}")

# Check AI status
ai_status = get_ai_health()
if ai_status.get('enabled'):
    st.sidebar.success("✓ AI Enabled")
else:
    st.sidebar.warning("⚠ AI Not Configured")

st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "📊 Analytics", "🤖 AI Insights", "⚙️ Automation", "ℹ️ About"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Actions")


# ================== HOME PAGE ==================
if page == "🏠 Dashboard":
    st.title("OpenHPI Automation Dashboard")
    st.markdown("Welcome to the OpenHPI course management and automation platform.")
    
    # Display system status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("API Status", "Online" if api_status else "Offline")
    
    with col2:
        st.metric("AI Service", "Enabled" if ai_status.get('enabled') else "Disabled")
    
    with col3:
        # Get course count
        try:
            response = requests.get(f"{API_BASE_URL}/api/courses/", timeout=5)
            if response.status_code == 200:
                courses = response.json().get('courses', [])
                st.metric("Total Courses", len(courses))
            else:
                st.metric("Total Courses", "N/A")
        except:
            st.metric("Total Courses", "N/A")
    
    with col4:
        st.metric("Environment", "Development")
    
    st.markdown("---")
    
    # Recent Activity / Quick Stats
    st.subheader("Quick Stats")
    
    try:
        # Get categories
        response = requests.get(f"{API_BASE_URL}/api/courses/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json().get('categories', [])
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📚 **{len(categories)} Course Categories**")
            with col2:
                if categories:
                    st.info(f"🏷️ Categories: {', '.join(categories[:5])}")
    except:
        pass
    
    st.markdown("---")
    st.subheader("Getting Started")
    st.markdown("""
    ### Features:
    - **📊 Analytics**: View course statistics, enrollment trends, and performance metrics
    - **🤖 AI Insights**: Get AI-powered course summaries and feedback analysis
    - **⚙️ Automation**: Batch enroll users, monitor helpdesk, and update pages
    
    ### Quick Links:
    - [API Documentation]({}/docs)
    - [Health Check]({}/health)
    """.format(API_BASE_URL, API_BASE_URL))


# ================== ANALYTICS PAGE ==================
elif page == "📊 Analytics":
    st.title("📊 Course Analytics")
    
    # Tab navigation for different analytics
    tab1, tab2, tab3 = st.tabs(["Course Metrics", "Annual Statistics", "Quiz Performance"])
    
    with tab1:
        st.subheader("Course Performance Metrics")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            years = st.multiselect("Select Years", [2023, 2024, 2025], default=[2024])
        with col2:
            categories = st.multiselect("Select Categories", ["Python", "Java", "Web", "AI"])
        
        if st.button("Load Course Metrics"):
            with st.spinner("Loading data..."):
                try:
                    params = {}
                    if years:
                        params['years'] = years
                    if categories:
                        params['categories'] = categories
                    
                    response = requests.get(
                        f"{API_BASE_URL}/api/analysis/course_metrics",
                        params=params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success("✓ Data loaded successfully!")
                        
                        # Display metrics
                        if 'metrics' in data:
                            st.subheader("Key Metrics")
                            metrics = data['metrics']
                            
                            # Create columns for metrics display
                            cols = st.columns(3)
                            for idx, (key, value) in enumerate(metrics.items()):
                                with cols[idx % 3]:
                                    if isinstance(value, (int, float)):
                                        st.metric(key.replace('_', ' ').title(), f"{value:,.0f}")
                        
                        # Display monthly enrollments chart
                        if 'monthly_enrollments' in data and data['monthly_enrollments']:
                            st.subheader("Monthly Enrollment Trends")
                            df = pd.DataFrame(data['monthly_enrollments'])
                            if not df.empty:
                                fig = px.line(df, x=df.index, y=df.columns, 
                                            title="Monthly Enrollments")
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Failed to load data: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Annual Statistics Report")
        
        year = st.selectbox("Select Year", [2023, 2024, 2025], index=1)
        
        if st.button("Generate Annual Report"):
            with st.spinner("Generating report..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/api/analysis/annual_stats/{year}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        report = data.get('report', {})
                        metrics = report.get('metrics', {})
                        
                        st.success(f"✓ Report generated for {year}")
                        
                        # Display metrics in columns
                        st.subheader("Annual Metrics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Enrollments", 
                                    f"{metrics.get('total_enrollments', 0):,}")
                            st.metric("German Enrollments", 
                                    f"{metrics.get('german_enrollments', 0):,}")
                        
                        with col2:
                            st.metric("English Enrollments", 
                                    f"{metrics.get('english_enrollments', 0):,}")
                            st.metric("Total Certificates", 
                                    f"{metrics.get('total_certificates', 0):,}")
                        
                        with col3:
                            st.metric("Overall Completion Rate", 
                                    f"{metrics.get('overall_completion_rate', 0):.1f}%")
                            st.metric("German Completion Rate", 
                                    f"{metrics.get('german_completion_rate', 0):.1f}%")
                    else:
                        st.error(f"Failed to generate report: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("Quiz Performance Analysis")
        
        quiz_type = st.selectbox("Quiz Type", ["All", "graded", "ungraded", "survey"])
        
        if st.button("Load Quiz Performance"):
            with st.spinner("Loading quiz data..."):
                try:
                    params = {}
                    if quiz_type != "All":
                        params['quiz_type'] = quiz_type
                    
                    response = requests.get(
                        f"{API_BASE_URL}/api/analysis/quiz_performance",
                        params=params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success("✓ Quiz data loaded!")
                        
                        # Display overall metrics
                        if 'overall_metrics' in data:
                            st.subheader("Overall Metrics")
                            metrics = data['overall_metrics']
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Submissions", 
                                        f"{metrics.get('total_submissions', 0):,}")
                            with col2:
                                st.metric("Avg Score", 
                                        f"{metrics.get('average_score', 0):.1f}%")
                            with col3:
                                st.metric("Pass Rate", 
                                        f"{metrics.get('pass_rate', 0):.1f}%")
                            with col4:
                                st.metric("Unique Users", 
                                        f"{metrics.get('unique_users', 0):,}")
                    else:
                        st.error(f"Failed to load quiz data: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


# ================== AI INSIGHTS PAGE ==================
elif page == "🤖 AI Insights":
    st.title("🤖 AI-Powered Insights")
    
    if not ai_status.get('enabled'):
        st.warning("⚠️ AI service is not configured. Please set GOOGLE_API_KEY in your environment.")
        st.info("AI features will be available once the API key is configured.")
    else:
        st.success("✓ AI service is enabled and ready to use!")
    
    # Tab navigation for different AI features
    tab1, tab2, tab3 = st.tabs(["Course Summary", "Feedback Analysis", "Course Insights"])
    
    with tab1:
        st.subheader("Generate Course Summary")
        st.markdown("Get an AI-generated one-sentence summary of any course description.")
        
        course_title = st.text_input("Course Title", "Introduction to Python")
        course_description = st.text_area(
            "Course Description",
            "This course covers the fundamentals of Python programming...",
            height=150
        )
        
        if st.button("Generate Summary", disabled=not ai_status.get('enabled')):
            with st.spinner("Generating summary with AI..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/ai/summarize-course",
                        json={
                            "course_title": course_title,
                            "course_description": course_description
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✓ Summary generated!")
                        st.markdown("### Summary:")
                        st.info(result.get('summary', ''))
                    else:
                        st.error(f"Failed to generate summary: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Analyze Survey Feedback")
        st.markdown("Analyze multiple feedback responses to extract insights and sentiment.")
        
        context = st.text_input("Context (optional)", "Teacher feedback for Python Junior course")
        
        feedback_text = st.text_area(
            "Enter Feedback (one per line)",
            "The course was excellent and well-structured.\nI would like more practical examples.\nGreat teaching style!",
            height=200
        )
        
        if st.button("Analyze Feedback", disabled=not ai_status.get('enabled')):
            feedback_list = [line.strip() for line in feedback_text.split('\n') if line.strip()]
            
            if not feedback_list:
                st.warning("Please enter at least one feedback line.")
            else:
                with st.spinner(f"Analyzing {len(feedback_list)} feedback responses..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/ai/analyze-feedback",
                            json={
                                "feedback_texts": feedback_list,
                                "context": context if context else None
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✓ Analyzed {result.get('feedback_count', 0)} responses!")
                            st.markdown("### Analysis:")
                            st.info(result.get('analysis', ''))
                        else:
                            st.error(f"Failed to analyze feedback: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("Get Course Insights")
        st.markdown("Generate comprehensive AI insights for a course from the database.")
        
        # Get list of courses
        try:
            response = requests.get(f"{API_BASE_URL}/api/courses/", timeout=5)
            if response.status_code == 200:
                courses = response.json().get('courses', [])
                course_ids = [c.get('course_id', '') for c in courses if c.get('course_id')]
                
                if course_ids:
                    selected_course = st.selectbox("Select Course", course_ids)
                    
                    if st.button("Generate Insights", disabled=not ai_status.get('enabled')):
                        with st.spinner("Generating insights..."):
                            try:
                                response = requests.get(
                                    f"{API_BASE_URL}/api/ai/course-insights/{selected_course}",
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    st.success("✓ Insights generated!")
                                    
                                    st.markdown(f"### Course: {result.get('course_title', selected_course)}")
                                    
                                    st.markdown("**Summary:**")
                                    st.info(result.get('summary', 'No summary available'))
                                    
                                    st.markdown("**Key Concepts:**")
                                    st.info(result.get('key_concepts', 'No concepts extracted'))
                                else:
                                    st.error(f"Failed to generate insights: {response.status_code}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                else:
                    st.warning("No courses found in database. Please scrape courses first.")
            else:
                st.error("Failed to load courses from API.")
        except Exception as e:
            st.error(f"Error loading courses: {str(e)}")


# ================== AUTOMATION PAGE ==================
elif page == "⚙️ Automation":
    st.title("⚙️ Automation Tasks")
    
    # Tab navigation for different automation tasks
    tab1, tab2, tab3 = st.tabs(["Batch Enrollment", "Helpdesk Monitor", "Page Updates"])
    
    with tab1:
        st.subheader("Batch Enroll Users")
        st.markdown("Enroll multiple users in a course from a list of email addresses.")
        
        course_id = st.text_input("Course ID", "pythonjunior2024")
        
        user_emails = st.text_area(
            "User Emails (one per line)",
            "user1@example.com\nuser2@example.com",
            height=150
        )
        
        headless = st.checkbox("Run in headless mode", value=True)
        
        if st.button("Start Enrollment"):
            email_list = [line.strip() for line in user_emails.split('\n') if line.strip()]
            
            if not email_list:
                st.warning("Please enter at least one email address.")
            else:
                with st.spinner(f"Enrolling {len(email_list)} users..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/automation/enroll",
                            json={
                                "users": email_list,
                                "course_id": course_id,
                                "headless": headless
                            },
                            timeout=300  # 5 minutes timeout for automation
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✓ Enrollment completed!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Enrolled", result.get('enrolled_count', 0))
                            with col2:
                                st.metric("Unregistered", result.get('unregistered_count', 0))
                            
                            if result.get('unregistered'):
                                st.warning("Unregistered users:")
                                for email in result.get('unregistered', []):
                                    st.text(f"- {email}")
                        else:
                            st.error(f"Enrollment failed: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Helpdesk Ticket Monitor")
        st.markdown("Check for new helpdesk tickets and send notifications.")
        
        if st.button("Check Helpdesk"):
            with st.spinner("Checking helpdesk..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/automation/notify-helpdesk",
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✓ Helpdesk check completed!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Tickets", result.get('tickets_count', 0))
                        with col2:
                            status = "✓" if result.get('notification_sent') else "✗"
                            st.metric("Telegram", status)
                        with col3:
                            status = "✓" if result.get('email_sent') else "✗"
                            st.metric("Email", status)
                        
                        if 'analysis' in result:
                            st.subheader("Ticket Analysis")
                            analysis = result['analysis']
                            
                            data = {
                                'Time Period': ['Within 6 hours', 'Within 12 hours', 
                                              'Within 24 hours', 'Within 48 hours'],
                                'Count': [
                                    analysis.get('within_6hrs', 0),
                                    analysis.get('within_12hrs', 0),
                                    analysis.get('within_24hrs', 0),
                                    analysis.get('within_48hrs', 0)
                                ]
                            }
                            df = pd.DataFrame(data)
                            fig = px.bar(df, x='Time Period', y='Count', 
                                       title="Tickets by Response Time")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Helpdesk check failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("Update Page Content")
        st.markdown("Update page content on the OpenHPI platform.")
        
        page_name = st.text_input("Page Name", "course-announcements")
        content = st.text_area("New Content", height=200)
        headless = st.checkbox("Run in headless mode", value=True, key="page_headless")
        
        if st.button("Update Page"):
            if not page_name or not content:
                st.warning("Please provide both page name and content.")
            else:
                with st.spinner("Updating page..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/automation/update-page",
                            json={
                                "page_name": page_name,
                                "content": content,
                                "headless": headless
                            },
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✓ {result.get('message', 'Page updated successfully!')}")
                        else:
                            st.error(f"Page update failed: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


# ================== ABOUT PAGE ==================
elif page == "ℹ️ About":
    st.title("About OpenHPI Automation")
    
    st.markdown("""
    ## OpenHPI Automation Platform
    
    A unified automation and analytics platform for OpenHPI course management.
    
    ### Features
    
    #### 📊 Analytics
    - Course performance metrics and trends
    - Annual statistics reports
    - Quiz performance analysis
    - Enrollment tracking
    
    #### 🤖 AI Insights
    - Course summaries powered by Google Gemini
    - Survey feedback analysis
    - Key concept extraction
    - Automated insights generation
    
    #### ⚙️ Automation
    - Batch user enrollment
    - Helpdesk ticket monitoring
    - Page content updates
    - Automated notifications
    
    ### Technology Stack
    
    - **Backend**: FastAPI + SQLAlchemy
    - **Frontend**: Streamlit
    - **AI**: langfun + Google Generative AI
    - **Database**: SQLite (configurable to PostgreSQL)
    - **Automation**: Selenium WebDriver
    
    ### Architecture
    
    ```
    Dashboard (Streamlit) → API (FastAPI) → Services → Database
    ```
    
    ### API Endpoints
    
    Visit [/docs]({}/docs) for interactive API documentation.
    
    ### Configuration
    
    The platform requires configuration through environment variables:
    - `OPENHPI_USERNAME` and `OPENHPI_PASSWORD` for platform access
    - `GOOGLE_API_KEY` for AI features
    - `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` for notifications
    
    ### Version
    
    **v0.1.0** - Phase 4 Complete
    """.format(API_BASE_URL))
    
    st.markdown("---")
    st.markdown("Made with ❤️ for OpenHPI")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**OpenHPI Automation v0.1.0**")
st.sidebar.markdown("Phase 4: Complete")
