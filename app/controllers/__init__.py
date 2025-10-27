"""
Controllers package for OPIc Practice Portal
Contains route handlers and controllers following OOP principles
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date
import time
import random

from app.services import AuthService, UserService, QuestionService, ResponseService, SurveyService
from app.models import Survey


class BaseController:
    """Base controller class with common functionality"""
    
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()
        self.question_service = QuestionService()
        self.response_service = ResponseService()


class AuthController(BaseController):
    """Controller for authentication routes"""
    
    def login(self):
        """Handle login GET and POST requests"""
        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            remember = request.form.get('remember', False)
            
            result = self.auth_service.login_user(username, password)
            
            if result['success']:
                # Make session permanent to keep user logged in
                session.permanent = True
                login_user(result['user'], remember=True)
                flash(result['message'], 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash(result['message'], 'error')
                return redirect(url_for('auth.login'))
        
        return render_template('auth/login.html')
    
    def register(self):
        """Handle registration GET and POST requests"""
        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            name = request.form.get('name', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate input
            if not username or not email or not name or not password or not confirm_password:
                flash('All fields are required.', 'error')
                return redirect(url_for('auth.register'))
            
            # Validate password match
            if password != confirm_password:
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('auth.register'))
            
            # Validate password length
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return redirect(url_for('auth.register'))
            
            # Validate username format (alphanumeric, underscore, and dot only)
            if not username.replace('_', '').replace('.', '').isalnum():
                flash('Username can only contain letters, numbers, underscores, and dots.', 'error')
                return redirect(url_for('auth.register'))
            
            # Validate email format (basic check)
            if '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'error')
                return redirect(url_for('auth.register'))
            
            result = self.auth_service.register_user(username, email, name, password)
            
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(result['message'], 'error')
                return redirect(url_for('auth.register'))
        
        return render_template('auth/register.html')
    
    def logout(self):
        """Handle logout request"""
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('auth.login'))


class MainController(BaseController):
    """Controller for main application routes"""
    
    def index(self):
        """Handle home page request"""
        return render_template('main/index.html')
    
    @login_required
    def dashboard(self):
        """Handle dashboard request"""
        # Get user statistics
        user_stats = self.user_service.get_user_statistics(current_user.id)
        
        # Get total questions count
        total_questions = self.question_service.get_all_questions_count()
        
        # Update user streak if needed
        if current_user.last_active_date != date.today():
            self.user_service.update_user_streak(current_user)
            user_stats = self.user_service.get_user_statistics(current_user.id)
        
        return render_template('main/dashboard.html',
                             user_stats=user_stats,
                             total_questions=total_questions)
    
    @login_required
    def test_mode(self):
        """Handle test mode request"""
        return redirect(url_for('test_mode.survey'))
    
    @login_required
    def practice_mode(self):
        """Handle practice mode request"""
        return redirect(url_for('practice_mode.index'))
    
    @login_required
    def profile(self):
        """Handle user profile request"""
        if request.method == 'POST':
            # Update user profile
            name = request.form.get('name')
            email = request.form.get('email')
            target_language = request.form.get('target_language')
            
            # Validate input
            if not name or not email:
                flash('Name and email are required.', 'error')
                return redirect(url_for('main.profile'))
            
            # Check if email is already taken by another user
            existing_user = self.user_service.get_user_by_email(email)
            if existing_user and existing_user.id != current_user.id:
                flash('Email is already registered to another account.', 'error')
                return redirect(url_for('main.profile'))
            
            # Update user
            current_user.name = name
            current_user.email = email
            current_user.target_language = target_language
            
            if self.user_service.commit():
                flash('Profile updated successfully!', 'success')
            else:
                flash('Failed to update profile. Please try again.', 'error')
            
            return redirect(url_for('main.profile'))
        
        # GET request - show profile form
        user_stats = self.user_service.get_user_statistics(current_user.id)
        return render_template('main/profile.html', user_stats=user_stats)
    
    @login_required
    def change_password(self):
        """Handle password change request"""
        if request.method == 'POST':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_new_password = request.form.get('confirm_new_password', '')
            
            # Validate input
            if not current_password or not new_password or not confirm_new_password:
                flash('All password fields are required.', 'error')
                return redirect(url_for('main.profile'))
            
            # Verify current password
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('main.profile'))
            
            # Validate new password match
            if new_password != confirm_new_password:
                flash('New passwords do not match. Please try again.', 'error')
                return redirect(url_for('main.profile'))
            
            # Validate new password length
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'error')
                return redirect(url_for('main.profile'))
            
            # Check if new password is different from current
            if current_password == new_password:
                flash('New password must be different from current password.', 'error')
                return redirect(url_for('main.profile'))
            
            # Update password
            current_user.set_password(new_password)
            if self.user_service.commit():
                flash('Password changed successfully!', 'success')
            else:
                flash('Failed to change password. Please try again.', 'error')
            
            return redirect(url_for('main.profile'))
        
        # If GET request, redirect to profile
        return redirect(url_for('main.profile'))
    
    @login_required
    def history(self):
        """Handle user history/activity page"""
        # Get all user responses with related question data
        responses = self.response_service.get_user_responses(current_user.id, limit=None)
        
        # Get user surveys
        surveys = Survey.query.filter_by(user_id=current_user.id)\
            .order_by(Survey.created_at.desc()).all()
        
        # Get user statistics
        user_stats = self.user_service.get_user_statistics(current_user.id)
        
        # Group responses by date for better organization
        from collections import defaultdict
        responses_by_date = defaultdict(list)
        for response in responses:
            date_key = response.created_at.strftime('%Y-%m-%d')
            responses_by_date[date_key].append(response)
        
        return render_template('main/history.html',
                             responses=responses,
                             responses_by_date=dict(responses_by_date),
                             surveys=surveys,
                             user_stats=user_stats)


class TestModeController(BaseController):
    """Controller for test mode routes"""
    
    def __init__(self):
        super().__init__()
        from app.services import SurveyService
        self.survey_service = SurveyService()
    
    @login_required
    def survey(self):
        """Handle test mode survey"""
        if request.method == 'POST':
            # Process survey answers
            answers = request.form.to_dict()
            
            # Handle interests list
            if 'interests_list' in answers:
                interests = answers['interests_list'].split(',') if answers['interests_list'] else []
                answers['interests'] = interests
                del answers['interests_list']
            
            # Save survey
            survey = self.survey_service.create_survey(current_user.id, answers)
            
            if survey:
                flash('Survey completed! Starting your personalized test...', 'success')
                return redirect(url_for('test_mode.questions', q=1))
            else:
                flash('Error saving survey. Please try again.', 'error')
        
        return render_template('test_mode/survey.html')
    
    @login_required
    def questions(self):
        """Handle test mode questions"""
        question_number = request.args.get('q', 1, type=int)
        
        # Get user's survey to personalize questions
        survey = self.survey_service.get_user_survey(current_user.id)
        
        if not survey:
            flash('Please complete the survey first.', 'error')
            return redirect(url_for('test_mode.survey'))
        
        # Get personalized questions based on survey
        questions = self.get_personalized_questions(survey.answers)
        
        if question_number > len(questions):
            return redirect(url_for('test_mode.finish'))
        
        question = questions[question_number - 1]
        
        return render_template('test_mode/questions.html',
                             question=question,
                             current_question_index=question_number,
                             total_questions=len(questions))
    
    def get_personalized_questions(self, survey_answers):
        """Get personalized questions based on survey answers"""
        # This is a simplified version - in production, you'd have more sophisticated logic
        english_level = survey_answers.get('english_level', 'intermediate')
        interests = survey_answers.get('interests', [])
        
        # Get questions based on difficulty and interests
        questions = []
        
        # Add questions based on interests
        for interest in interests[:3]:  # Limit to 3 interests
            topic_questions = self.question_service.get_questions_by_topic(interest.title(), 'english')
            if topic_questions:
                questions.extend(topic_questions[:2])  # 2 questions per interest
        
        # Add general questions if we don't have enough
        if len(questions) < 5:
            general_questions = self.question_service.get_questions_by_difficulty(english_level, 'english')
            questions.extend(general_questions[:5-len(questions)])
        
        # Ensure we have at least 5 questions
        if len(questions) < 5:
            random_questions = self.question_service.get_random_questions(5-len(questions), 'english')
            questions.extend(random_questions)
        
        return questions[:5]  # Limit to 5 questions for now
    
    @login_required
    def record_response(self, question_id):
        """Handle response recording"""
        if request.method == 'POST':
            try:
                # Get the uploaded audio file
                audio_file = request.files.get('audio')
                
                if not audio_file:
                    return jsonify({'success': False, 'error': 'No audio file provided'})
                
                # Save the audio file
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(f"response_{current_user.id}_{question_id}_{int(time.time())}.webm")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'responses', filename)
                
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                audio_file.save(upload_path)
                
                # Save response to database
                response = self.response_service.create_response(
                    user_id=current_user.id,
                    question_id=question_id,
                    audio_url=f"uploads/responses/{filename}"
                )
                
                if response:
                    return jsonify({'success': True, 'response_id': response.id})
                else:
                    return jsonify({'success': False, 'error': 'Failed to save response'})
                    
            except Exception as e:
                current_app.logger.error(f"Error recording response: {e}")
                return jsonify({'success': False, 'error': 'Internal server error'})
        
        return jsonify({'success': False, 'error': 'Invalid request method'})
    
    @login_required
    def finish_test(self):
        """Handle test completion"""
        # Update user streak
        self.user_service.update_user_streak(current_user)
        
        flash('Congratulations! You have completed the test.', 'success')
        return redirect(url_for('main.dashboard'))


class PracticeModeController(BaseController):
    """Controller for practice mode routes"""
    
    @login_required
    def index(self):
        """Handle practice mode index"""
        # Don't load topics initially - they will be loaded via AJAX based on level
        user_stats = self.user_service.get_user_statistics(current_user.id)
        return render_template('practice_mode/index.html', user_stats=user_stats)
    
    @login_required
    def get_topics_by_level(self, level):
        """Return topics available for a specific level as JSON"""
        if level not in ['IM', 'IH', 'AL']:
            return jsonify({'topics': [], 'error': 'Invalid level'})
        
        topics = self.question_service.get_all_topics(
            language=current_user.target_language,
            level=level
        )
        return jsonify({'topics': topics})
    
    @login_required
    def start_practice(self):
        """Handle practice session start"""
        if request.method == 'POST':
            topic = request.form.get('topic')
            level = request.form.get('level')
            language = current_user.target_language
            
            if not level:
                flash('Please select a difficulty level.', 'error')
                return redirect(url_for('practice_mode.index'))
            
            if topic == 'random':
                # Get random question with level filter
                questions = self.question_service.get_random_questions_by_level(
                    count=1, 
                    language=language, 
                    level=level
                )
                if questions:
                    question_id = questions[0].id
                    # Store allowed question in session for security
                    session['allowed_practice_question'] = question_id
                    return redirect(url_for('practice_mode.question', question_id=question_id))
            else:
                # Get questions by topic and level
                questions = self.question_service.get_questions_by_topic_and_level(
                    topic, 
                    language, 
                    level
                )
                if questions:
                    question = random.choice(questions)
                    question_id = question.id
                    # Store allowed question in session for security
                    session['allowed_practice_question'] = question_id
                    return redirect(url_for('practice_mode.question', question_id=question_id))
            
            flash('No questions found for your selection.', 'error')
            return redirect(url_for('practice_mode.index'))
    
    @login_required
    def question(self, question_id):
        """Handle practice question display with security check"""
        # Security check: Verify user is authorized to access this question
        allowed_question_id = session.get('allowed_practice_question')
        
        if allowed_question_id != question_id:
            flash('Unauthorized access. Please start a practice session properly.', 'warning')
            return redirect(url_for('practice_mode.index'))
        
        question = self.question_service.get_question_by_id(question_id)
        if not question:
            flash('Question not found.', 'error')
            return redirect(url_for('practice_mode.index'))
        
        return render_template('practice_mode/question.html', question=question)
    
    @login_required
    def record_practice_response(self, question_id):
        """Handle practice response recording with security check"""
        if request.method == 'POST':
            # Security check: Verify user is authorized to submit response for this question
            allowed_question_id = session.get('allowed_practice_question')
            
            if allowed_question_id != question_id:
                return jsonify({'success': False, 'error': 'Unauthorized access to this question'})
            
            try:
                audio_file = request.files.get('audio')
                
                if not audio_file:
                    return jsonify({'success': False, 'error': 'No audio file provided'})
                
                import os
                from werkzeug.utils import secure_filename
                import time
                
                filename = secure_filename(f"practice_response_{current_user.id}_{question_id}_{int(time.time())}.webm")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'responses', filename)
                
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                audio_file.save(upload_path)
                
                response = self.response_service.create_response(
                    user_id=current_user.id,
                    question_id=question_id,
                    audio_url=f"uploads/responses/{filename}"
                )
                
                if response:
                    # Update user streak
                    self.user_service.update_user_streak(current_user)
                    # Clear the session to prevent reuse of the same question
                    session.pop('allowed_practice_question', None)
                    return jsonify({'success': True, 'response_id': response.id})
                else:
                    return jsonify({'success': False, 'error': 'Failed to save response'})
                    
            except Exception as e:
                current_app.logger.error(f"Error recording practice response: {e}")
                return jsonify({'success': False, 'error': 'Internal server error'})
        
        return jsonify({'success': False, 'error': 'Invalid request method'})
