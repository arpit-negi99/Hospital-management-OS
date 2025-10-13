#!/usr/bin/env python3
import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from dotenv import load_dotenv

from .config import DevConfig
from .models import db, User, Student, Company, Skill, Internship, Application, student_skills

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(DevConfig())

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    @app.route('/')
    def home():
        return render_template('landing.html')

    # Authentication
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            identifier = request.form.get('identifier', '').strip().lower()
            password = request.form.get('password', '')
            user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=True, duration=timedelta(days=app.config.get('REMEMBER_COOKIE_DURATION_DAYS', 14)))
                flash('Logged in successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                # First-time sign-up on login page
                username = request.form.get('username') or identifier.split('@')[0]
                email = request.form.get('email') or (identifier if '@' in identifier else f"{identifier}@example.edu")
                role = request.form.get('role', 'student')
                if not user and password and username:
                    # Create account
                    if User.query.filter((User.email == email) | (User.username == username)).first():
                        flash('User already exists. Try logging in.', 'warning')
                        return redirect(url_for('login'))
                    new_user = User(email=email, username=username, password_hash=generate_password_hash(password), role=role)
                    db.session.add(new_user)
                    db.session.flush()
                    if role == 'student':
                        profile = Student(user_id=new_user.id, name=username.title(), department='Unknown', year='1', contact=None)
                        db.session.add(profile)
                    elif role == 'company':
                        company = Company(user_id=new_user.id, name=username.title(), description=None)
                        db.session.add(company)
                    db.session.commit()
                    login_user(new_user, remember=True, duration=timedelta(days=app.config.get('REMEMBER_COOKIE_DURATION_DAYS', 14)))
                    flash('Account created and logged in', 'success')
                    return redirect(url_for('dashboard'))
                flash('Invalid credentials', 'danger')
        return render_template('auth/login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        if current_user.role == 'company':
            return redirect(url_for('company_dashboard'))
        return redirect(url_for('admin_dashboard'))

    # Student routes
    @app.route('/student')
    @login_required
    def student_dashboard():
        if current_user.role != 'student':
            return redirect(url_for('dashboard'))
        profile = current_user.student_profile
        internships = Internship.query.order_by(Internship.created_at.desc()).all()
        my_apps = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
        applied_ids = {a.internship_id for a in my_apps}
        # Recommendation: simple skill match percentage
        recommendations = []
        student_skill_ids = {s.id for s in profile.skills}
        for intern in internships:
            req_ids = {s.id for s in intern.skills}
            if req_ids:
                match = len(student_skill_ids & req_ids) / len(req_ids)
            else:
                match = 0.0
            recommendations.append({
                'internship': intern,
                'match_pct': int(match * 100)
            })
        return render_template('student/dashboard.html', profile=profile, recommendations=recommendations, applied_ids=applied_ids, my_apps=my_apps)

    @app.route('/student/profile', methods=['GET', 'POST'])
    @login_required
    def student_profile():
        if current_user.role != 'student':
            return redirect(url_for('dashboard'))
        profile = current_user.student_profile
        if request.method == 'POST':
            profile.name = request.form.get('name', profile.name)
            profile.department = request.form.get('department', profile.department)
            profile.year = request.form.get('year', profile.year)
            profile.contact = request.form.get('contact', profile.contact)
            profile.gpa = float(request.form.get('gpa')) if request.form.get('gpa') else profile.gpa
            profile.resume_url = request.form.get('resume_url') or profile.resume_url
            db.session.commit()
            flash('Profile updated', 'success')
            return redirect(url_for('student_profile'))
        all_skills = Skill.query.order_by(Skill.name.asc()).all()
        return render_template('student/profile.html', profile=profile, all_skills=all_skills)

    @app.route('/student/skills', methods=['POST'])
    @login_required
    def student_update_skills():
        if current_user.role != 'student':
            return redirect(url_for('dashboard'))
        profile = current_user.student_profile
        skills_raw = request.form.get('skills', '')
        selected_ids = {int(sid) for sid in skills_raw.split(',') if sid.strip().isdigit()}
        profile.skills = Skill.query.filter(Skill.id.in_(selected_ids)).all()
        db.session.commit()
        flash('Skills updated', 'success')
        return redirect(url_for('student_profile'))

    @app.route('/student/apply/<int:internship_id>', methods=['POST'])
    @login_required
    def student_apply(internship_id):
        if current_user.role != 'student':
            return redirect(url_for('dashboard'))
        profile = current_user.student_profile
        existing = Application.query.filter_by(student_id=profile.id, internship_id=internship_id).first()
        if existing:
            flash('Already applied', 'warning')
        else:
            app_obj = Application(student_id=profile.id, internship_id=internship_id)
            db.session.add(app_obj)
            db.session.commit()
            flash('Applied successfully', 'success')
        return redirect(url_for('student_dashboard'))

    # Company routes
    @app.route('/company')
    @login_required
    def company_dashboard():
        if current_user.role != 'company':
            return redirect(url_for('dashboard'))
        company = current_user.company_profile
        interns = Internship.query.filter_by(company_id=company.id).order_by(Internship.created_at.desc()).all()
        return render_template('company/dashboard.html', company=company, internships=interns)

    @app.route('/company/internship/new', methods=['GET', 'POST'])
    @login_required
    def company_new_internship():
        if current_user.role != 'company':
            return redirect(url_for('dashboard'))
        company = current_user.company_profile
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            duration = int(request.form.get('duration_months', '1'))
            req_skill_ids = {int(sid) for sid in request.form.get('skill_ids', '').split(',') if sid.strip().isdigit()}
            internship = Internship(company_id=company.id, title=title, description=description, duration_months=duration)
            internship.skills = Skill.query.filter(Skill.id.in_(req_skill_ids)).all()
            db.session.add(internship)
            db.session.commit()
            flash('Internship posted', 'success')
            return redirect(url_for('company_dashboard'))
        all_skills = Skill.query.order_by(Skill.name.asc()).all()
        return render_template('company/new_internship.html', company=company, all_skills=all_skills)

    @app.route('/company/candidates')
    @login_required
    def company_candidates():
        if current_user.role != 'company':
            return redirect(url_for('dashboard'))
        req_skill_ids = {int(sid) for sid in request.args.get('skill_ids', '').split(',') if sid.strip().isdigit()}
        students = Student.query.all()
        results = []
        for s in students:
            student_skill_ids = {sk.id for sk in s.skills}
            if req_skill_ids:
                match = len(student_skill_ids & req_skill_ids) / len(req_skill_ids)
            else:
                match = 0.0
            results.append({'student': s, 'match_pct': int(match * 100)})
        results.sort(key=lambda x: x['match_pct'], reverse=True)
        return render_template('company/candidates.html', results=results)

    # Admin routes
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            return redirect(url_for('dashboard'))
        stats = {
            'num_students': Student.query.count(),
            'num_companies': Company.query.count(),
            'num_internships': Internship.query.count(),
            'num_applications': Application.query.count(),
        }
        # Skill stats
        top_skills = db.session.query(Skill.name, db.func.count(student_skills.c.student_id)).\
            join(student_skills, Skill.id == student_skills.c.skill_id).\
            group_by(Skill.name).order_by(db.func.count(student_skills.c.student_id).desc()).limit(10).all()
        return render_template('admin/dashboard.html', stats=stats, top_skills=top_skills)

    @app.route('/admin/reports')
    @login_required
    def admin_reports():
        if current_user.role != 'admin':
            return redirect(url_for('dashboard'))

        # Applications by status
        status_counts = dict(
            db.session.query(Application.status, db.func.count(Application.id))
            .group_by(Application.status)
            .all()
        )

        # Hires per student (completed internships)
        hires_subq = (
            db.session.query(Application.student_id, db.func.count(Application.id).label('hire_count'))
            .filter(Application.status == 'hired')
            .group_by(Application.student_id)
            .subquery()
        )
        top_students = (
            db.session.query(Student, db.func.coalesce(hires_subq.c.hire_count, 0))
            .outerjoin(hires_subq, Student.id == hires_subq.c.student_id)
            .order_by(db.desc(db.func.coalesce(hires_subq.c.hire_count, 0)))
            .limit(15)
            .all()
        )

        # Most popular required skills across internships
        popular_intern_skills = db.session.query(Skill.name, db.func.count(Skill.id)).\
            join(Skill.internships).group_by(Skill.name).\
            order_by(db.func.count(Skill.id).desc()).limit(10).all()

        return render_template(
            'admin/reports.html',
            status_counts=status_counts,
            top_students=top_students,
            popular_intern_skills=popular_intern_skills,
        )

    # Minimal JSON endpoints for async UI enhancements
    @app.route('/api/skills')
    def api_skills():
        items = Skill.query.order_by(Skill.name.asc()).all()
        return jsonify([{'id': s.id, 'name': s.name} for s in items])

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create DB tables if not existing and seed skills minimally
        db.create_all()
        if Skill.query.count() == 0:
            for name in [
                'Python', 'Java', 'C++', 'SQL', 'JavaScript', 'HTML', 'CSS', 'React', 'Flask', 'Django',
                'Data Analysis', 'Machine Learning', 'Communication', 'Teamwork']:
                db.session.add(Skill(name=name))
            db.session.commit()
    app.run(host='0.0.0.0', port=5001, debug=True)
