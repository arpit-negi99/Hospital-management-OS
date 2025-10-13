from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

# SQLAlchemy instance will be created in app factory

db = SQLAlchemy()

# Association tables
student_skills = Table(
    'student_skills', db.metadata,
    Column('student_id', Integer, ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)

internship_skills = Table(
    'internship_skills', db.metadata,
    Column('internship_id', Integer, ForeignKey('internships.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'student', 'company', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = relationship('Student', back_populates='user', uselist=False)
    company_profile = relationship('Company', back_populates='user', uselist=False)

    def get_id(self):
        return str(self.id)

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(120), nullable=True)
    gpa = db.Column(db.Float, nullable=True)
    resume_url = db.Column(db.String(512), nullable=True)

    user = relationship('User', back_populates='student_profile')
    skills = relationship('Skill', secondary=student_skills, back_populates='students')
    applications = relationship('Application', back_populates='student', cascade='all, delete-orphan')

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)

    user = relationship('User', back_populates='company_profile')
    internships = relationship('Internship', back_populates='company', cascade='all, delete-orphan')

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)

    students = relationship('Student', secondary=student_skills, back_populates='skills')
    internships = relationship('Internship', secondary=internship_skills, back_populates='skills')

class Internship(db.Model):
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='internships')
    skills = relationship('Skill', secondary=internship_skills, back_populates='internships')
    applications = relationship('Application', back_populates='internship', cascade='all, delete-orphan')

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(20), default='applied', index=True)  # applied, shortlisted, rejected, hired
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('student_id', 'internship_id', name='uq_application_student_internship'),
    )

    student = relationship('Student', back_populates='applications')
    internship = relationship('Internship', back_populates='applications')
