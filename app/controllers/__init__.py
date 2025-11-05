"""
Controllers package for OPIc Practice Portal
Contains route handlers and controllers following OOP principles
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date
import time
import random

from app import db
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
            email = request.form.get('email', '').strip()  # Optional
            name = request.form.get('name', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate required fields (email is optional)
            if not username or not name or not password or not confirm_password:
                flash('Username, name, and password are required.', 'error')
                return redirect(url_for('auth.register'))
            
            # Validate username starts with lowercase letter
            if not username or not username[0].islower():
                flash('Username must start with a lowercase letter (a-z).', 'error')
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
            
            # Validate email format only if provided (email is optional)
            if email:
                if '@' not in email or '.' not in email:
                    flash('Please enter a valid email address or leave it empty.', 'error')
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
        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        # Otherwise, show the landing page
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
    def chatbot(self):
        """Handle chatbot page request"""
        return render_template('main/chatbot.html')
    
    def pwa_guide(self):
        """Handle PWA installation guide request"""
        return render_template('main/pwa_guide.html')
    
    @login_required
    def tips(self):
        """Render Tips page with useful PDF resources"""
        from app.models import Tip
        
        # Get active tips from database, ordered by display_order
        db_tips = Tip.query.filter_by(is_active=True).order_by(Tip.display_order, Tip.created_at.desc()).all()
        
        # Convert to list of dictionaries for template
        pdf_resources = []
        for tip in db_tips:
            pdf_resources.append({
                'id': f'tip-{tip.id}',
                'title': tip.title,
                'description': tip.description or 'Useful resource for OPIc test preparation.',
                'filename': tip.filename,
                'thumbnail_path': tip.thumbnail_path,
                'category': tip.category or 'Test Preparation'
            })
        
        # Fallback: If no tips in database, show default one
        if not pdf_resources:
            pdf_resources = [
                {
                    'id': 'opic-rater-guide',
                    'title': 'OPIc Rater Guidelines',
                    'description': 'Learn about OPIc test evaluation criteria, scoring guidelines, and what raters look for in responses.',
                    'filename': 'secrets-from-an-opic-rater.pdf',
                    'category': 'Test Preparation'
                }
            ]
        
        return render_template('main/tips.html', pdf_resources=pdf_resources)
    
    @login_required
    def profile(self):
        """Handle user profile request"""
        if request.method == 'POST':
            # Update user profile
            name = request.form.get('name')
            email = request.form.get('email')
            target_language = request.form.get('target_language')
            avatar = request.form.get('avatar')
            
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
            
            # Update avatar if provided and different from current
            if avatar and avatar != current_user.avatar:
                # Delete old custom avatar if user is switching away from it
                old_avatar = current_user.avatar
                if old_avatar and old_avatar.startswith('uploads/avatars/'):
                    self._delete_old_avatar(old_avatar)
                
                current_user.avatar = avatar
            
            if self.user_service.commit():
                flash('Profile updated successfully!', 'success')
            else:
                flash('Failed to update profile. Please try again.', 'error')
            
            return redirect(url_for('main.profile'))
        
        # GET request - show profile form
        user_stats = self.user_service.get_user_statistics(current_user.id)
        return render_template('main/profile.html', user_stats=user_stats)
    
    def _delete_old_avatar(self, avatar_path):
        """Helper function to delete old avatar file"""
        try:
            # Only delete uploaded avatars, not default ones
            if avatar_path and avatar_path.startswith('uploads/avatars/'):
                import os
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', os.path.basename(avatar_path))
                if os.path.exists(full_path):
                    os.remove(full_path)
                    current_app.logger.info(f"Deleted old avatar: {full_path}")
                    return True
        except Exception as e:
            current_app.logger.error(f"Error deleting old avatar: {e}")
        return False
    
    @login_required
    def upload_avatar(self):
        """Handle avatar file upload"""
        if request.method == 'POST':
            try:
                avatar_file = request.files.get('avatar_file')
                
                if not avatar_file:
                    return jsonify({'success': False, 'error': 'No file provided'})
                
                # Validate file
                import os
                from werkzeug.utils import secure_filename
                
                # Check file extension
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                filename = secure_filename(avatar_file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if file_ext not in allowed_extensions:
                    return jsonify({'success': False, 'error': 'Invalid file type. Allowed: JPG, PNG, GIF, WEBP'})
                
                # Delete old avatar if it exists and is a custom upload
                old_avatar = current_user.avatar
                if old_avatar and old_avatar.startswith('uploads/avatars/'):
                    self._delete_old_avatar(old_avatar)
                
                # Generate unique filename
                import time
                unique_filename = f"avatar_{current_user.id}_{int(time.time())}.{file_ext}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', unique_filename)
                
                # Create avatars directory if it doesn't exist
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                
                # Try to use PIL for image processing, fallback to direct save
                try:
                    from PIL import Image
                    
                    # Save and resize image
                    image = Image.open(avatar_file)
                    
                    # Convert RGBA to RGB if necessary
                    if image.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                        image = background
                    
                    # Resize to 500x500 for avatars
                    image.thumbnail((500, 500), Image.Resampling.LANCZOS)
                    
                    # Save the image
                    image.save(upload_path, quality=85, optimize=True)
                    
                except ImportError:
                    # PIL not installed, just save the file directly
                    current_app.logger.warning("PIL/Pillow not installed, saving avatar without processing")
                    avatar_file.seek(0)  # Reset file pointer
                    avatar_file.save(upload_path)
                
                avatar_url = f"uploads/avatars/{unique_filename}"
                
                return jsonify({
                    'success': True,
                    'avatar_url': avatar_url
                })
                
            except Exception as e:
                current_app.logger.error(f"Error uploading avatar: {e}")
                import traceback
                current_app.logger.error(traceback.format_exc())
                return jsonify({'success': False, 'error': f'Failed to upload avatar: {str(e)}'})
        
        return jsonify({'success': False, 'error': 'Invalid request method'})
    
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
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # Get all user responses with related question data
        responses = self.response_service.get_user_responses(current_user.id, limit=None)
        
        # Get user surveys
        surveys = Survey.query.filter_by(user_id=current_user.id)\
            .order_by(Survey.created_at.desc()).all()
        
        # Get user statistics
        user_stats = self.user_service.get_user_statistics(current_user.id)
        
        # Separate practice and test responses
        practice_responses = [r for r in responses if r.mode == 'practice']
        test_responses = [r for r in responses if r.mode == 'test']
        
        # Group test responses into sessions (responses within 2 hours are considered same session)
        test_sessions = []
        if test_responses:
            # Sort test responses by date
            test_responses.sort(key=lambda x: x.created_at)
            
            current_session = []
            last_time = None
            
            for response in test_responses:
                if not last_time or (response.created_at - last_time) < timedelta(hours=2):
                    current_session.append(response)
                else:
                    # Start new session
                    if current_session:
                        test_sessions.append(current_session)
                    current_session = [response]
                last_time = response.created_at
            
            # Add the last session
            if current_session:
                test_sessions.append(current_session)
        
        # Group everything by date for timeline display
        responses_by_date = defaultdict(list)
        
        # Add practice responses
        for response in practice_responses:
            date_key = response.created_at.strftime('%Y-%m-%d')
            responses_by_date[date_key].append(response)
        
        # Add test sessions as grouped entries
        for session in test_sessions:
            if session:
                # Use the first response's date as the session date
                date_key = session[0].created_at.strftime('%Y-%m-%d')
                
                # Find the matching survey (closest one by time)
                session_survey = None
                for survey in surveys:
                    if survey.created_at.date() == session[0].created_at.date():
                        session_survey = survey
                        break
                
                # Create a test session entry
                test_session_entry = {
                    'type': 'test_session',
                    'responses': session,
                    'start_time': session[0].created_at,
                    'survey': session_survey
                }
                responses_by_date[date_key].append(test_session_entry)
        
        # Sort items within each date by time
        for date_key in responses_by_date:
            responses_by_date[date_key].sort(key=lambda x: 
                x.created_at if hasattr(x, 'created_at') else x['start_time'], 
                reverse=True)
        
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
                flash('Survey completed! Please proceed to self-assessment.', 'success')
                return redirect(url_for('test_mode.self_assessment'))
            else:
                flash('Error saving survey. Please try again.', 'error')
        
        return render_template('test_mode/survey.html')
    
    @login_required
    def self_assessment(self):
        """Handle self-assessment level selection"""
        if request.method == 'POST':
            # Get selected level
            level = request.form.get('level')
            
            if not level:
                flash('Please select your English level.', 'error')
                return redirect(url_for('test_mode.self_assessment'))
            
            # Save level to session
            session['self_assessment_level'] = int(level)
            
            # Update the survey record with the level
            survey = self.survey_service.get_user_survey(current_user.id)
            if survey:
                # Update survey answers to include self-assessment level
                # Create a new dict to ensure SQLAlchemy detects the change
                updated_answers = dict(survey.answers) if survey.answers else {}
                updated_answers['self_assessment_level'] = int(level)
                # Map level to difficulty string for question selection
                level_map = {
                    1: 'IM',  # Novice Low -> IM
                    2: 'IM',  # Novice Mid -> IM
                    3: 'IM',  # Novice High/Intermediate Low -> IM
                    4: 'IH',  # Intermediate Mid -> IH
                    5: 'IH',  # Intermediate High/Advanced Low -> IH
                    6: 'AL'   # Advanced Mid/High -> AL
                }
                updated_answers['english_level'] = level_map.get(int(level), 'IM')
                survey.answers = updated_answers
                db.session.commit()
                
                # Debug log
                print(f"[Test Mode] Self-assessment level saved: {int(level)}, Survey answers: {survey.answers}")
                
                flash('Self-assessment complete! Starting your test...', 'success')
                return redirect(url_for('test_mode.questions', q=1))
            else:
                flash('Please complete the survey first.', 'error')
                return redirect(url_for('test_mode.survey'))
        
        return render_template('test_mode/self_assessment.html')
    
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
        """Get personalized questions based on survey answers and self-assessment level"""
        # Handle both dict and JSON types
        if survey_answers is None:
            survey_answers = {}
        
        # Ensure it's a dict (SQLAlchemy JSON columns might return different types)
        if not isinstance(survey_answers, dict):
            try:
                import json
                if isinstance(survey_answers, str):
                    survey_answers = json.loads(survey_answers)
                else:
                    survey_answers = dict(survey_answers)
            except:
                survey_answers = {}
        
        english_level = survey_answers.get('english_level', 'IM')
        self_assessment_level = survey_answers.get('self_assessment_level', 3)
        interests = survey_answers.get('interests', [])
        
        # Convert to int if it's a string or float
        if isinstance(self_assessment_level, str):
            try:
                self_assessment_level = int(float(self_assessment_level))
            except (ValueError, TypeError):
                self_assessment_level = 3
        elif isinstance(self_assessment_level, float):
            self_assessment_level = int(self_assessment_level)
        elif not isinstance(self_assessment_level, int):
            self_assessment_level = 3
        
        # Ensure level is between 1 and 6
        if self_assessment_level < 1 or self_assessment_level > 6:
            self_assessment_level = 3
        
        # Determine number of questions based on self-assessment level
        # Level-based question count: Lower levels (1-4): 10-12 questions, Higher levels (5-6): Maximum 15 questions
        question_count_map = {
            1: 10,  # Novice Low - 10 questions
            2: 10,  # Novice Mid - 10 questions
            3: 12,  # Novice High / Intermediate Low - 12 questions
            4: 12,  # Intermediate Mid - 12 questions
            5: 15,  # Intermediate High / Advanced Low - Maximum 15 questions
            6: 15   # Advanced Mid / Advanced High - Maximum 15 questions
        }
        target_count = question_count_map.get(self_assessment_level, 12)
        
        # Debug log to verify level is being read correctly
        print(f"[Test Mode] get_personalized_questions - self_assessment_level: {self_assessment_level} (type: {type(self_assessment_level)}), target_count: {target_count}, survey_answers keys: {list(survey_answers.keys()) if survey_answers else 'None'}")
        
        # Get questions based on difficulty and interests
        questions = []
        
        # Add questions based on interests from survey
        # Maximum 3 questions per topic to ensure variety
        if interests:
            questions_per_topic = 3  # Maximum 3 questions per topic
            for interest in interests[:5]:  # Use up to 5 different interests
                topic_questions = self.question_service.get_questions_by_topic(interest.title(), 'english')
                if topic_questions:
                    # Add up to 3 questions from this topic
                    questions.extend(topic_questions[:questions_per_topic])
        
        # Track how many questions we have per topic
        topic_count = {}
        for q in questions:
            topic_count[q.topic] = topic_count.get(q.topic, 0) + 1
        
        # Add level-specific questions if we don't have enough
        if len(questions) < target_count:
            level_questions = self.question_service.get_questions_by_difficulty(english_level, 'english')
            for q in level_questions:
                if len(questions) >= target_count:
                    break
                # Only add if we don't have 3 questions from this topic already
                if topic_count.get(q.topic, 0) < 3 and q not in questions:
                    questions.append(q)
                    topic_count[q.topic] = topic_count.get(q.topic, 0) + 1
        
        # Fill remaining with random questions at appropriate level
        if len(questions) < target_count:
            # Request more than needed to account for filtering
            random_questions = self.question_service.get_random_questions_by_level(
                (target_count - len(questions)) * 2,  # Request 2x to have buffer
                'english',
                level=english_level
            )
            for q in random_questions:
                if len(questions) >= target_count:
                    break
                # Only add if we don't have 3 questions from this topic already
                if topic_count.get(q.topic, 0) < 3 and q not in questions:
                    questions.append(q)
                    topic_count[q.topic] = topic_count.get(q.topic, 0) + 1
        
        # Shuffle questions for variety
        random.shuffle(questions)
        
        # Ensure we return exactly the target count (or less if not enough questions available)
        # For levels 5 and 6, this will be maximum 15 questions
        final_questions = questions[:target_count]
        
        # Log for debugging
        print(f"[Test Mode] Self-assessment level: {self_assessment_level}, Target count: {target_count}, Final questions: {len(final_questions)}")
        
        return final_questions
    
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
                
                # Save response to database with mode='test'
                response = self.response_service.create_response(
                    user_id=current_user.id,
                    question_id=question_id,
                    audio_url=f"uploads/responses/{filename}",
                    mode='test'
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
        
        # Redirect to congratulations page
        return redirect(url_for('test_mode.congratulations'))
    
    @login_required
    def congratulations(self):
        """Show test completion congratulations page"""
        # Get user statistics
        user_stats = self.user_service.get_user_statistics(current_user.id)
        
        # Get the most recent test session (responses from last 2 hours)
        from datetime import datetime, timedelta
        from app.models import Response
        
        cutoff_time = datetime.utcnow() - timedelta(hours=2)
        recent_test_responses = Response.query.filter(
            Response.user_id == current_user.id,
            Response.mode == 'test',
            Response.created_at >= cutoff_time
        ).count()
        
        test_data = {
            'question_count': recent_test_responses,
            'streak_count': current_user.streak_count,
            'total_tests': user_stats.get('test_responses_count', 0)
        }
        
        return render_template('test_mode/congratulations.html', test_data=test_data)
    
    @login_required
    def ai_score(self, response_id):
        """Get AI scoring for a test response"""
        if request.method != 'POST':
            return jsonify({'success': False, 'error': 'Invalid request method'})
        
        try:
            from app.models import Response
            from app.services.ai_service import ai_service
            import json
            
            # Get the response
            response = Response.query.filter_by(
                id=response_id,
                user_id=current_user.id
            ).first()
            
            if not response:
                return jsonify({'success': False, 'error': 'Response not found'})
            
            # Always re-query AI for fresh feedback (removed cache check - user can request new feedback anytime)
            # Get transcript from request or from response
            transcript = request.json.get('transcript', '') if request.is_json else request.form.get('transcript', '')
            
            if not transcript:
                # If no transcript provided, check if response has one
                if not response.transcript:
                    return jsonify({
                        'success': False, 
                        'error': 'No transcript provided. Please type or speak your response first.'
                    })
                transcript = response.transcript
            
            # Get audio features for tone/prosody evaluation
            audio_features = None
            if request.is_json:
                audio_features = request.json.get('audio_features')
            else:
                audio_features_str = request.form.get('audio_features')
                if audio_features_str:
                    try:
                        import json
                        audio_features = json.loads(audio_features_str)
                    except:
                        audio_features = None
            
            # Get question text - prefer full text, fallback to topic
            question_text = response.question.text
            if not question_text or question_text.strip() == '':
                question_text = response.question.topic
            
            # Ensure we have question context for evaluation
            if not question_text:
                return jsonify({
                    'success': False,
                    'error': 'Question context not found. Cannot evaluate response without question.'
                })
            
            # Get AI scoring with audio features
            ai_result = ai_service.score_response(transcript, question_text, audio_features)
            
            if not ai_result:
                return jsonify({
                    'success': False,
                    'error': 'AI scoring failed. Please try again later.'
                })
            
            # Save AI results to database
            response.transcript = transcript
            response.ai_score = ai_result.get('score', 50)
            response.ai_feedback = ai_result.get('feedback', '')
            response.ai_data = json.dumps({
                'strengths': ai_result.get('strengths', []),
                'suggestions': ai_result.get('suggestions', [])
            })
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'score': response.ai_score,
                'feedback': response.ai_feedback,
                'data': json.loads(response.ai_data)
            })
            
        except Exception as e:
            current_app.logger.error(f"Error in AI scoring: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Internal error: {str(e)}'
            })
    

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
        """Handle practice question display - allows direct access via links"""
        question = self.question_service.get_question_by_id(question_id)
        if not question:
            flash('Question not found.', 'error')
            return redirect(url_for('practice_mode.index'))
        
        # Allow direct access - store this as the current practice question
        session['allowed_practice_question'] = question_id
        
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
                
                # Get transcript if provided
                transcript = request.form.get('transcript', '').strip()
                
                response = self.response_service.create_response(
                    user_id=current_user.id,
                    question_id=question_id,
                    audio_url=f"uploads/responses/{filename}"
                )
                
                # Save transcript if provided
                if response and transcript:
                    response.transcript = transcript
                    db.session.commit()
                
                if response:
                    # Update user streak
                    self.user_service.update_user_streak(current_user)
                    # Clear the session to prevent reuse of the same question
                    session.pop('allowed_practice_question', None)
                    # Return success with redirect URL
                    return jsonify({
                        'success': True, 
                        'response_id': response.id,
                        'redirect_url': url_for('practice_mode.congratulations', response_id=response.id)
                    })
                else:
                    return jsonify({'success': False, 'error': 'Failed to save response'})
                    
            except Exception as e:
                current_app.logger.error(f"Error recording practice response: {e}")
                return jsonify({'success': False, 'error': 'Internal server error'})
        
        return jsonify({'success': False, 'error': 'Invalid request method'})
    
    @login_required
    def congratulations(self):
        """Show practice completion congratulations page"""
        response_id = request.args.get('response_id', type=int)
        
        # Get user statistics
        user_stats = self.user_service.get_user_statistics(current_user.id)
        
        # Get the response details if provided
        from app.models import Response
        response = None
        if response_id:
            response = Response.query.filter_by(
                id=response_id,
                user_id=current_user.id
            ).first()
        
        practice_data = {
            'response': response,
            'streak_count': current_user.streak_count,
            'total_practices': user_stats.get('practice_responses_count', 0),
            'question': response.question if response else None
        }
        
        return render_template('practice_mode/congratulations.html', practice_data=practice_data)
    
    @login_required
    def ai_score(self, response_id):
        """Get AI scoring for a response"""
        if request.method != 'POST':
            return jsonify({'success': False, 'error': 'Invalid request method'})
        
        try:
            from app.models import Response
            from app.services.ai_service import ai_service
            import json
            
            # Get the response
            response = Response.query.filter_by(
                id=response_id,
                user_id=current_user.id
            ).first()
            
            if not response:
                return jsonify({'success': False, 'error': 'Response not found'})
            
            # Always re-query AI for fresh feedback (removed cache check - user can request new feedback anytime)
            # Get transcript from request or from response
            transcript = request.json.get('transcript', '') if request.is_json else request.form.get('transcript', '')
            
            if not transcript:
                # If no transcript provided, check if response has one
                if not response.transcript:
                    return jsonify({
                        'success': False, 
                        'error': 'No transcript provided. Please type or speak your response first.'
                    })
                transcript = response.transcript
            
            # Get audio features for tone/prosody evaluation
            audio_features = None
            if request.is_json:
                audio_features = request.json.get('audio_features')
            else:
                audio_features_str = request.form.get('audio_features')
                if audio_features_str:
                    try:
                        import json
                        audio_features = json.loads(audio_features_str)
                    except:
                        audio_features = None
            
            # Get question text - prefer full text, fallback to topic
            question_text = response.question.text
            if not question_text or question_text.strip() == '':
                question_text = response.question.topic
            
            # Ensure we have question context for evaluation
            if not question_text:
                return jsonify({
                    'success': False,
                    'error': 'Question context not found. Cannot evaluate response without question.'
                })
            
            # Get AI scoring with audio features
            ai_result = ai_service.score_response(transcript, question_text, audio_features)
            
            if not ai_result:
                return jsonify({
                    'success': False,
                    'error': 'AI scoring failed. Please try again later.'
                })
            
            # Save AI results to database
            response.transcript = transcript
            response.ai_score = ai_result.get('score', 50)
            response.ai_feedback = ai_result.get('feedback', '')
            response.ai_data = json.dumps({
                'strengths': ai_result.get('strengths', []),
                'suggestions': ai_result.get('suggestions', [])
            })
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'score': response.ai_score,
                'feedback': response.ai_feedback,
                'data': json.loads(response.ai_data)
            })
            
        except Exception as e:
            current_app.logger.error(f"Error in AI scoring: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Internal error: {str(e)}'
            })