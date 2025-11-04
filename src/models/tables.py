"""
Database models for OpenHPI automation platform.

These models represent the data currently stored in various CSV files:
- Course data (from course_scraper.py, data_scraper.py)
- User enrollment data (from batch_enroll.py)
- Quiz results (from quiz_analysis.py, quiz_comparison.py)
- Analytics data (from course_analytics.py, annual_stats.Rmd)
- Helpdesk tickets (from helpdesk_notifier.py)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, Date, JSON
)
from sqlalchemy.orm import relationship

from .database import Base


class Course(Base):
    """Course information."""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    url = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    language = Column(String)
    category = Column(String)  # e.g., "Java", "Python", "Quantum Computing"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stats = relationship("CourseStats", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="course", cascade="all, delete-orphan")


class CourseStats(Base):
    """Course statistics and KPIs."""
    __tablename__ = "course_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, ForeignKey("courses.course_id"), nullable=False)
    
    # Statistics
    total_enrollments = Column(Integer)
    active_users = Column(Integer)
    certificates_issued = Column(Integer)
    completion_rate = Column(Float)
    average_progress = Column(Float)
    average_session_duration = Column(Float)
    items_visited_percentage = Column(Float)
    graded_quiz_performance = Column(Float)
    ungraded_quiz_performance = Column(Float)
    
    # Metadata
    recorded_at = Column(DateTime, default=datetime.utcnow)
    year = Column(Integer)
    
    # Raw data from scraper (flexible for additional fields)
    raw_data = Column(JSON)
    
    # Relationship
    course = relationship("Course", back_populates="stats")


class User(Base):
    """User information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    is_registered = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="user", cascade="all, delete-orphan")


class Enrollment(Base):
    """User course enrollments."""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.course_id"), nullable=False)
    
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="enrolled")  # enrolled, completed, dropped
    
    # Completion data
    confirmation_of_participation = Column(Boolean, default=False)
    record_of_achievement = Column(Boolean, default=False)
    course_completed = Column(Boolean, default=False)
    
    # Progress metrics
    items_visited_percentage = Column(Float)
    avg_session_duration = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class QuizResult(Base):
    """Quiz results and performance data."""
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.course_id"), nullable=False)
    
    quiz_name = Column(String, nullable=False)
    quiz_type = Column(String)  # graded, ungraded, survey
    
    # Performance
    score = Column(Float)
    max_score = Column(Float)
    percentage = Column(Float)
    attempts = Column(Integer, default=1)
    
    # Timing
    submitted_at = Column(DateTime)
    time_spent = Column(Integer)  # in seconds
    
    # Relationships
    user = relationship("User", back_populates="quiz_results")
    course = relationship("Course", back_populates="quiz_results")


class SurveyResponse(Base):
    """Survey responses and feedback."""
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, ForeignKey("courses.course_id"))
    
    survey_type = Column(String)  # teacher, student, end-of-course
    response_data = Column(JSON)  # Flexible storage for survey responses
    
    submitted_at = Column(DateTime, default=datetime.utcnow)


class HelpdeskTicket(Base):
    """Helpdesk ticket tracking."""
    __tablename__ = "helpdesk_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True, nullable=False)
    
    status = Column(String)  # open, closed, pending
    state = Column(String)
    owner = Column(String)
    
    time_open = Column(String)  # e.g., "6Hrs", "30Mins"
    ticket_url = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapingJob(Base):
    """Track scraping job executions."""
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False)  # course_data, dashboard_stats, helpdesk
    status = Column(String, default="pending")  # pending, running, completed, failed
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    records_processed = Column(Integer, default=0)
    error_message = Column(Text)
    
    job_metadata = Column(JSON)  # Additional job-specific data
