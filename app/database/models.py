from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Text
from pgvector.sqlalchemy import Vector
import datetime

Base = declarative_base()


class Role(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)
    password_hash = Column(String)
    email = Column(String)

    role_id = Column(Integer, ForeignKey("roles.id"))
    locked = Column(Boolean, default=False)

    role = relationship("Role")


class Term(Base):

    __tablename__ = "terms"

    id = Column(Integer, primary_key=True)
    canvas_id = Column(Integer)
    name = Column(String)

    start_date = Column(DateTime)
    end_date = Column(DateTime)


class Course(Base):

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    canvas_id = Column(Integer)
    name = Column(String)

    term_id = Column(Integer, ForeignKey("terms.id"))
    sis_id = Column(String)

    term = relationship("Term")


class ScanJob(Base):

    __tablename__ = "scan_jobs"

    id = Column(Integer, primary_key=True)

    term_id = Column(Integer)
    status = Column(String)

    paused = Column(Boolean, default=False)
    cancelled = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CourseScan(Base):

    __tablename__ = "course_scans"

    id = Column(Integer, primary_key=True)

    course_id = Column(Integer, ForeignKey("courses.id"))
    scan_date = Column(DateTime, default=datetime.datetime.utcnow)

    risk_score = Column(Float)

    course = relationship("Course")


class AccessibilityIssue(Base):

    __tablename__ = "accessibility_issues"

    id = Column(Integer, primary_key=True)

    course_scan_id = Column(Integer, ForeignKey("course_scans.id"))

    issue_type = Column(String)
    severity = Column(String)
    location = Column(String)

    description = Column(Text)


class Video(Base):

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)

    course_id = Column(Integer, ForeignKey("courses.id"))

    url = Column(String)
    provider = Column(String)

    duration_seconds = Column(Integer)


class CaptionStatus(Base):

    __tablename__ = "caption_status"

    id = Column(Integer, primary_key=True)

    video_id = Column(Integer, ForeignKey("videos.id"))

    captions_present = Column(Boolean)
    accuracy_score = Column(Float)


class ContentFingerprint(Base):

    __tablename__ = "content_fingerprints"

    id = Column(Integer, primary_key=True)

    course_id = Column(Integer)
    content_type = Column(String)

    hash = Column(String)


class ContentEmbedding(Base):

    __tablename__ = "content_embeddings"

    id = Column(Integer, primary_key=True)

    content_id = Column(Integer)

    embedding = Column(Vector(768))


class DuplicateGroup(Base):

    __tablename__ = "duplicate_groups"

    id = Column(Integer, primary_key=True)

    similarity_score = Column(Float)


class DuplicateItem(Base):

    __tablename__ = "duplicate_items"

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("duplicate_groups.id"))
    content_id = Column(Integer)


class AIReport(Base):

    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True)

    course_scan_id = Column(Integer)
    summary = Column(Text)