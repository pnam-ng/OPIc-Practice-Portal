"""
Question Generation Service for OPIc Practice Portal
Provides AI-powered question generation, variation, and intelligent rotation
"""
import os
import json
import random
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app.models import Question, QuestionSession
from app import db


class QuestionGeneratorService:
    """Service for AI-powered question generation and management"""
    
    # Question type templates for different categories
    QUESTION_TEMPLATES = {
        'general': [
            "Tell me about {topic} in your area/country.",
            "What do you know about {topic}?",
            "Can you describe {topic} to me?",
        ],
        'experience': [
            "Tell me about a memorable experience related to {topic}.",
            "Describe a time when you had an interesting experience with {topic}.",
            "What was your best/worst experience involving {topic}?",
        ],
        'comparison': [
            "Compare {topic} in the past and now. What has changed?",
            "What are the differences between {topic} in your country and other countries?",
            "Compare two different aspects of {topic}.",
        ],
        'roleplay': [
            "Imagine you are at a place related to {topic}. Ask 3-4 questions about it.",
            "You need to help a friend with {topic}. What would you say?",
            "There's a problem with {topic}. Call to report the issue and ask questions.",
        ],
        'opinion': [
            "What do you think about {topic}? Why?",
            "Do you think {topic} is important? Explain your reasons.",
            "What are the advantages and disadvantages of {topic}?",
        ]
    }
    
    # Variation prompts for generating question variations
    VARIATION_PROMPTS = {
        'rephrase': """Rephrase the following OPIc question while keeping the same meaning.
Original: {question}
Topic: {topic}
Level: {level}

Create a new version that asks the same thing but uses different words and structure.
Keep the difficulty level appropriate for {level}.
Respond with ONLY the new question text, nothing else.""",

        'followup': """Create a follow-up question based on this OPIc question.
Original: {question}
Topic: {topic}
Level: {level}

Create a deeper exploration question that could be asked after the original.
It should encourage more detailed or specific responses.
Respond with ONLY the follow-up question text, nothing else.""",

        'perspective': """Create a perspective-shift version of this OPIc question.
Original: {question}
Topic: {topic}
Level: {level}

Change the point of view (e.g., from personal to hypothetical, or add a scenario).
Examples: "If a tourist asked you...", "From your friend's perspective...", "In a professional setting..."
Respond with ONLY the new question text, nothing else.""",

        'timeshift': """Create a time-based variation of this OPIc question.
Original: {question}
Topic: {topic}
Level: {level}

Shift the time frame (past, present, or future) to create a new question.
Examples: past experiences, current habits, future plans, or changes over time.
Respond with ONLY the new question text, nothing else."""
    }
    
    def __init__(self):
        self._ai_service = None
    
    @property
    def ai_service(self):
        """Lazy load AI service"""
        if self._ai_service is None:
            from app.services.ai_service import AIService
            self._ai_service = AIService()
        return self._ai_service
    
    def generate_question(self, topic: str, level: str, question_type: str = 'general',
                         existing_questions: List[str] = None) -> Optional[Dict]:
        """
        Generate a new OPIc question using AI with template fallback
        
        Args:
            topic: The topic for the question (e.g., "Restaurants")
            level: Difficulty level (IM, IH, AL)
            question_type: Type of question to generate
            existing_questions: List of existing question texts to avoid duplication
            
        Returns:
            Dict with 'text', 'sample_answer', 'keywords' or None if failed
        """
        # Try AI-powered generation only (no template fallback)
        result = self._generate_with_ai(topic, level, question_type, existing_questions)
        return result  # Returns None if AI fails
    
    def _generate_with_ai(self, topic: str, level: str, question_type: str,
                          existing_questions: List[str] = None) -> Optional[Dict]:
        """Generate question using AI (Gemini API) with level-appropriate complexity"""
        try:
            existing_list = existing_questions or []
            existing_str = '\n'.join([f"- {q}" for q in existing_list[:10]])  # Limit to 10
            
            # Level-specific complexity guidelines
            level_guidelines = self._get_level_guidelines(level)
            
            prompt = f"""You are an OPIc (Oral Proficiency Interview - Computer) test question creator.

Generate a NEW, UNIQUE question for the OPIc test.

**Parameters:**
- Topic: {topic}
- Level: {level} (IM=Intermediate-Mid, IH=Intermediate-High, AL=Advanced-Low)
- Question Type: {question_type}

**IMPORTANT - Level-Specific Complexity Guidelines for {level}:**
{level_guidelines}

**Existing questions to AVOID duplicating:**
{existing_str if existing_str else "(No existing questions)"}

**Requirements:**
1. The question MUST match the complexity level of {level} as described above
2. It must be related to the topic "{topic}"
3. For {question_type} type: {"general description/introduction" if question_type == 'general' else "personal experience/story" if question_type == 'experience' else "compare two things" if question_type == 'comparison' else "role-play scenario" if question_type == 'roleplay' else "opinion/viewpoint"}
4. It must be DIFFERENT from the existing questions listed above

**Sample Answer Requirements:**
- The sample answer must also match the {level} level complexity
- Use vocabulary and sentence structures appropriate for {level}
{self._get_sample_answer_guidelines(level)}

**Respond in JSON format:**
{{
    "question_text": "The full question text",
    "sample_answer": "A model response matching {level} level",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

            content = self.ai_service._call_google_api(prompt)
            
            if not content:
                return None
            
            # Parse JSON response
            import re
            content = content.strip()
            content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
            content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)
            
            # Find JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'text': data.get('question_text', ''),
                    'sample_answer': data.get('sample_answer', ''),
                    'keywords': data.get('keywords', [])
                }
            
            return None
            
        except Exception as e:
            try:
                current_app.logger.warning(f"AI generation failed, will use template: {e}")
            except:
                print(f"AI generation failed, will use template: {e}")
            return None

    def _get_level_guidelines(self, level: str) -> str:
        """Get complexity guidelines for each level"""
        guidelines = {
            'IM': """
**Intermediate-Mid (IM) - SIMPLEST Level:**
- Use SIMPLE, direct questions that are easy to understand
- Ask about familiar, everyday topics (daily routines, personal preferences)
- Question structure: Simple sentences, one idea at a time
- Expected response: Short descriptions, basic vocabulary
- Avoid: Complex scenarios, hypothetical situations, abstract concepts
- Focus on: "What", "Where", "When" questions
- Example complexity: "Tell me about your favorite restaurant."
- Response time: 30-60 seconds""",

            'IH': """
**Intermediate-High (IH) - MODERATE Level:**
- Use moderately complex questions with some detail
- Include personal experiences and comparisons
- Question structure: Compound sentences, connected ideas
- Expected response: Descriptions with reasons, some elaboration
- Can include: Simple comparisons, past experiences, preferences with explanations
- Focus on: "How", "Why", and "Describe" questions
- Example complexity: "Describe a memorable experience at a restaurant and explain why it was special."
- Response time: 60-90 seconds""",

            'AL': """
**Advanced-Low (AL) - MOST COMPLEX Level:**
- Use sophisticated, multi-layered questions
- Include hypothetical scenarios, abstract concepts, and analytical elements
- Question structure: Complex sentences with multiple parts
- Expected response: Detailed analysis, opinions with supporting arguments
- Must include: Hypothetical situations ("If you were...", "Imagine that..."), comparisons across time or cultures, problem-solving scenarios
- Focus on: Analysis, evaluation, and synthesis questions
- Add challenges: Ask about changes over time, cultural differences, or solutions to problems
- Example complexity: "If you were to open a restaurant, what concept would you choose and how would you make it different from existing restaurants in your area? Consider current trends and customer preferences."
- Response time: 90-120 seconds"""
        }
        return guidelines.get(level.upper(), guidelines['IH'])

    def _get_sample_answer_guidelines(self, level: str) -> str:
        """Get sample answer requirements for each level"""
        guidelines = {
            'IM': """- Use simple vocabulary and short sentences
- Include 3-5 sentences as the response
- Use present tense primarily
- Basic connectors only (and, but, so, because)
- Straightforward, personal statements""",

            'IH': """- Use varied vocabulary with some descriptive words
- Include 5-8 sentences with details and reasons
- Mix of present, past, and future tenses
- Use connectors (however, therefore, for example, in addition)
- Include personal opinions with simple explanations""",

            'AL': """- Use sophisticated vocabulary and complex sentence structures
- Include 8-12 sentences with analysis and multiple perspectives
- All tenses including conditionals and hypotheticals
- Advanced connectors (nevertheless, consequently, on the other hand, taking into account)
- Include hypothetical reasoning, comparisons, and well-supported arguments
- Demonstrate critical thinking and nuanced opinions"""
        }
        return guidelines.get(level.upper(), guidelines['IH'])
    
    def _generate_from_template(self, topic: str, level: str, question_type: str,
                                existing_questions: List[str] = None) -> Optional[Dict]:
        """Generate question from templates (fallback when AI is unavailable) with level-appropriate complexity"""
        existing_list = existing_questions or []
        
        # Clean topic name first (remove numbering like "01. " and lowercase)
        clean_topic = topic
        if '. ' in topic:
            clean_topic = topic.split('. ', 1)[1]
        clean_topic = clean_topic.lower()
        
        # Level-specific templates
        templates = self._get_level_templates(clean_topic, level.upper())
        
        # Get templates for the requested type
        available_templates = templates.get(question_type, templates['general'])
        
        # Filter out templates that are too similar to existing questions
        unused_templates = []
        for template in available_templates:
            is_similar = False
            for existing in existing_list:
                # Simple similarity check
                if template.lower()[:30] == existing.lower()[:30]:
                    is_similar = True
                    break
            if not is_similar:
                unused_templates.append(template)
        
        # If all templates used, just pick a random one
        if not unused_templates:
            unused_templates = available_templates
        
        # Pick a random template
        question_text = random.choice(unused_templates)
        
        # Generate level-appropriate sample answer prompt
        sample_answer = self._get_level_sample_answer(clean_topic, level.upper())
        
        return {
            'text': question_text,
            'sample_answer': sample_answer,
            'keywords': [clean_topic, question_type, level.lower()]
        }

    def _get_level_templates(self, topic: str, level: str) -> Dict[str, List[str]]:
        """Get level-appropriate question templates"""
        
        if level == 'IM':
            # IM - Simple, direct questions
            return {
                'general': [
                    f"Tell me about {topic}.",
                    f"What is {topic} like?",
                    f"Do you like {topic}? Why?",
                    f"What do you know about {topic}?",
                    f"Describe {topic} for me.",
                    f"Where can you find {topic}?",
                    f"When do you usually think about {topic}?",
                    f"Is {topic} popular in your country?"
                ],
                'experience': [
                    f"Tell me about a time with {topic}.",
                    f"What is your experience with {topic}?",
                    f"Do you have a story about {topic}?",
                    f"When did you last experience {topic}?",
                    f"What happened with {topic} recently?",
                    f"Share one memory about {topic}."
                ],
                'comparison': [
                    f"Do you prefer {topic} now or before?",
                    f"Is {topic} different now?",
                    f"Has {topic} changed?",
                    f"What is better about {topic} now?"
                ],
                'roleplay': [
                    f"Tell a friend about {topic}.",
                    f"Explain {topic} to someone new.",
                    f"Describe {topic} to a visitor.",
                    f"What would you say about {topic}?"
                ],
                'opinion': [
                    f"Do you like {topic}? Why?",
                    f"Is {topic} important to you?",
                    f"What do you think about {topic}?",
                    f"Is {topic} good or bad?"
                ]
            }
        
        elif level == 'AL':
            # AL - Complex, hypothetical, analytical questions
            return {
                'general': [
                    f"If you were to explain {topic} to someone from a completely different culture, what aspects would you emphasize and why?",
                    f"Analyze how {topic} has evolved over the past decade and predict how it might change in the future.",
                    f"Consider the various perspectives people might have about {topic}. What are the main viewpoints and what influences them?",
                    f"Discuss the cultural significance of {topic} in your society and compare it with what you know about other cultures.",
                    f"If you were writing a comprehensive guide about {topic}, what would be the key points you would include and why?"
                ],
                'experience': [
                    f"Describe a challenging situation involving {topic} and explain how you overcame the difficulties. What did you learn?",
                    f"Think of a time when your understanding of {topic} completely changed. What caused this shift in perspective?",
                    f"If you could go back and change how you approached {topic} in a past experience, what would you do differently and why?",
                    f"Analyze a memorable experience with {topic} from multiple angles - what would others involved have thought?",
                    f"Describe a situation where {topic} created an unexpected outcome. How did it affect your future decisions?"
                ],
                'comparison': [
                    f"Compare and contrast how different generations view {topic}. What causes these differences and what might bridge the gap?",
                    f"If you were to analyze {topic} from both Eastern and Western perspectives, what key differences would emerge?",
                    f"How might {topic} look different in 20 years? Consider technological, social, and cultural factors in your analysis.",
                    f"Compare the advantages and disadvantages of traditional versus modern approaches to {topic}. Which is more sustainable?",
                    f"Analyze how urbanization has affected {topic} compared to rural areas. What are the implications for the future?"
                ],
                'roleplay': [
                    f"Imagine you are a consultant hired to improve {topic} in your city. Present your analysis and recommendations.",
                    f"You're being interviewed as an expert on {topic} for a documentary. Provide insights that would educate an international audience.",
                    f"Suppose you're writing a policy proposal about {topic}. What problems would you address and what solutions would you propose?",
                    f"If you were teaching a university course about {topic}, what would be your main lecture points for advanced students?",
                    f"You're advising a foreign investor interested in {topic} in your country. What comprehensive overview would you provide?"
                ],
                'opinion': [
                    f"Some argue that {topic} is becoming too commercialized. Do you agree? Support your position with specific examples.",
                    f"What role should the government play in regulating {topic}? Discuss the balance between freedom and oversight.",
                    f"How do you think technology will fundamentally change {topic} in the coming decades? Is this change positive or concerning?",
                    f"If you could redesign how society approaches {topic}, what changes would you implement and what challenges might arise?",
                    f"Critically evaluate the current state of {topic} in your country. What are its strengths, weaknesses, and potential improvements?"
                ]
            }
        
        else:
            # IH - Moderate complexity (default)
            return {
                'general': [
                    f"Tell me about {topic} in your area. What is it like and why?",
                    f"Can you describe {topic} in detail? What are the main characteristics?",
                    f"I'd like to know about {topic}. What can you tell me about your experience?",
                    f"What is {topic} like in your country? Please describe it with examples.",
                    f"Describe your experience with {topic}. What do you know about it and why?",
                    f"Let's talk about {topic}. What comes to mind and why is it significant?",
                    f"Tell me everything you know about {topic} and explain why it matters.",
                    f"Can you give me an overview of {topic} with some personal insights?"
                ],
                'experience': [
                    f"Tell me about a memorable experience you had with {topic}. Why was it special?",
                    f"Describe a specific time when {topic} was important to you. What happened?",
                    f"What was your best experience related to {topic}? Why was it memorable?",
                    f"Share a story about {topic} that you remember well. What made it stand out?",
                    f"When was the last time you dealt with {topic}? What happened and how did you feel?",
                    f"Tell me about a time when {topic} surprised you. What did you learn?",
                    f"Describe an unforgettable moment involving {topic}. Why do you still remember it?",
                    f"What interesting experience have you had with {topic}? How did it affect you?"
                ],
                'comparison': [
                    f"Compare {topic} now and 10 years ago. What has changed and why?",
                    f"What are the differences between {topic} in your country and other places you know?",
                    f"Compare two different aspects of {topic}. Which do you prefer and why?",
                    f"How has {topic} changed since you were young? What caused these changes?",
                    f"Compare the advantages and disadvantages of {topic}. What's your conclusion?",
                    f"How does {topic} differ between different age groups? Why do these differences exist?",
                    f"Compare traditional and modern approaches to {topic}. Which is better?",
                    f"What's the difference between {topic} in urban and rural areas? Why?"
                ],
                'roleplay': [
                    f"Imagine you're explaining {topic} to a foreigner. What would you include and emphasize?",
                    f"You're helping a friend who knows nothing about {topic}. Describe it thoroughly.",
                    f"Pretend you're a tour guide talking about {topic}. What interesting facts would you share?",
                    f"You're writing a blog post about {topic}. What would you include to engage readers?",
                    f"Imagine someone asks you about {topic}. How would you explain it comprehensively?",
                    f"You're making a recommendation about {topic}. What advice would you give and why?",
                    f"Pretend you're being interviewed about {topic}. What's your thoughtful response?",
                    f"A new colleague asks about {topic}. How do you explain it to help them understand?"
                ],
                'opinion': [
                    f"What do you think about {topic}? Do you like it or not? Explain your reasons.",
                    f"In your opinion, is {topic} important? Explain your reasons with examples.",
                    f"What are your thoughts on {topic}? Share your perspective and reasoning.",
                    f"Do you think {topic} is beneficial or harmful? Why do you think so?",
                    f"How do you feel about {topic}? Has your opinion changed over time?",
                    f"What's your personal view on {topic}? What shaped this opinion?",
                    f"If you had to rate {topic}, what would you say and why?",
                    f"Do you agree that {topic} is important in modern life? Why or why not?"
                ]
            }

    def _get_level_sample_answer(self, topic: str, level: str) -> str:
        """Generate a placeholder sample answer appropriate for the level"""
        if level == 'IM':
            return f"I like {topic}. It is nice. I think {topic} is good because it is fun. In my country, {topic} is popular. Many people enjoy it."
        elif level == 'AL':
            return f"When considering {topic}, there are multiple perspectives to analyze. From a cultural standpoint, {topic} has evolved significantly over the years, reflecting broader societal changes. If we examine this from both traditional and modern viewpoints, we can see interesting contrasts. Furthermore, the implications of {topic} extend beyond the immediate context, affecting various aspects of daily life. Hypothetically speaking, if current trends continue, we might expect to see even more changes in how society perceives and interacts with {topic}."
        else:  # IH
            return f"I would like to tell you about {topic}. In my experience, {topic} is quite interesting because it has several aspects worth mentioning. For example, I remember a time when {topic} was particularly important to me. Additionally, I think {topic} has changed over the years, becoming more significant in modern life. Overall, I believe {topic} is an important part of our daily lives."

    
    def generate_variation(self, question: Question, variation_type: str) -> Optional[str]:
        """
        Generate a variation of an existing question
        
        Args:
            question: The original Question object
            variation_type: Type of variation ('rephrase', 'followup', 'perspective', 'timeshift')
            
        Returns:
            New question text or None if failed
        """
        if variation_type not in self.VARIATION_PROMPTS:
            current_app.logger.error(f"Invalid variation type: {variation_type}")
            return None
        
        try:
            prompt = self.VARIATION_PROMPTS[variation_type].format(
                question=question.text,
                topic=question.topic,
                level=question.difficulty_level or 'IH'
            )
            
            content = self.ai_service._call_google_api(prompt)
            
            if content:
                # Clean up the response
                content = content.strip()
                # Remove any quotes or extra formatting
                content = content.strip('"\'')
                if len(content) > 10:  # Basic validation
                    return content
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error generating variation: {e}")
            return None
    
    def generate_variations_batch(self, question: Question, types: List[str] = None) -> List[Dict]:
        """
        Generate multiple variations of a question
        
        Args:
            question: The original Question object
            types: List of variation types to generate
            
        Returns:
            List of dicts with 'text' and 'variation_type'
        """
        if types is None:
            types = ['rephrase', 'followup', 'perspective', 'timeshift']
        
        variations = []
        for var_type in types:
            text = self.generate_variation(question, var_type)
            if text:
                variations.append({
                    'text': text,
                    'variation_type': var_type,
                    'parent_id': question.id
                })
        
        return variations
    
    def get_next_question(self, user_id: int, topic: str, level: str) -> Tuple[Optional[Question], bool]:
        """
        Get the next question for a user using intelligent rotation
        
        Args:
            user_id: The user's ID
            topic: The topic to practice
            level: The difficulty level
            
        Returns:
            Tuple of (Question, is_new_round)
            - Question: The next question to show
            - is_new_round: True if a new round just started
        """
        try:
            # Get current round
            current_round = QuestionSession.get_current_round(user_id, topic, level)
            
            # Get seen question IDs in current round
            seen_ids = QuestionSession.get_seen_question_ids(user_id, topic, level, current_round)
            
            # Get all questions for this topic/level
            # Match both exact topic and number-prefixed variants (e.g., "32. Role Play")
            all_questions = Question.query.filter(
                db.or_(
                    Question.topic == topic,
                    Question.topic.like(f'%. {topic}')
                ),
                Question.difficulty_level == level
            ).all()
            
            if not all_questions:
                current_app.logger.warning(f"No questions found for topic={topic}, level={level}")
                return None, False
            
            # Filter unseen questions
            unseen_questions = [q for q in all_questions if q.id not in seen_ids]
            
            is_new_round = False
            
            if unseen_questions:
                # Pick random from unseen
                question = random.choice(unseen_questions)
            else:
                # All questions seen - start new round
                current_round += 1
                is_new_round = True
                question = random.choice(all_questions)
                current_app.logger.info(f"User {user_id} completed round {current_round - 1} for {topic}/{level}. Starting round {current_round}")
            
            # Log this session
            session = QuestionSession(
                user_id=user_id,
                question_id=question.id,
                topic=topic,
                difficulty_level=level,
                round_number=current_round,
                was_answered=False
            )
            db.session.add(session)
            db.session.commit()
            
            return question, is_new_round
            
        except Exception as e:
            current_app.logger.error(f"Error getting next question: {e}")
            db.session.rollback()
            # Fallback to random question
            question = Question.query.filter(
                db.or_(
                    Question.topic == topic,
                    Question.topic.like(f'%. {topic}')
                ),
                Question.difficulty_level == level
            ).order_by(db.func.random()).first()
            return question, False
    
    def mark_question_answered(self, user_id: int, question_id: int) -> bool:
        """Mark a question as answered in the current session"""
        try:
            session = QuestionSession.query.filter_by(
                user_id=user_id,
                question_id=question_id,
                was_answered=False
            ).order_by(QuestionSession.shown_at.desc()).first()
            
            if session:
                session.was_answered = True
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error marking question answered: {e}")
            db.session.rollback()
            return False
    
    def get_user_progress(self, user_id: int, topic: str = None, level: str = None) -> Dict:
        """
        Get user's progress across topics/levels
        
        Args:
            user_id: The user's ID
            topic: Optional specific topic
            level: Optional specific level
            
        Returns:
            Dict with progress information
        """
        if topic and level:
            return QuestionSession.get_progress(user_id, topic, level)
        
        # Get overall progress
        from sqlalchemy import func
        
        # Get stats per topic/level
        stats_query = db.session.query(
            QuestionSession.topic,
            QuestionSession.difficulty_level,
            func.max(QuestionSession.round_number).label('max_round'),
            func.count(QuestionSession.id).label('total_shown')
        ).filter_by(user_id=user_id).group_by(
            QuestionSession.topic,
            QuestionSession.difficulty_level
        ).all()
        
        progress = {}
        for stat in stats_query:
            key = f"{stat.topic}_{stat.difficulty_level}"
            total_questions = Question.query.filter_by(
                topic=stat.topic,
                difficulty_level=stat.difficulty_level
            ).count()
            progress[key] = {
                'topic': stat.topic,
                'level': stat.difficulty_level,
                'rounds_completed': stat.max_round - 1 if stat.max_round else 0,
                'current_round': stat.max_round or 1,
                'total_shown': stat.total_shown,
                'total_questions': total_questions
            }
        
        return progress
    
    def save_generated_question(self, topic: str, level: str, text: str, 
                                sample_answer: str = None, keywords: List[str] = None,
                                parent_id: int = None, variation_type: str = None,
                                generation_source: str = 'gemini',
                                auto_generate_audio: bool = True) -> Optional[Question]:
        """
        Save a generated question to the database
        
        Args:
            topic: Topic for the question
            level: Difficulty level
            text: Question text
            sample_answer: Optional sample answer
            keywords: Optional list of keywords
            parent_id: Optional parent question ID (for variations)
            variation_type: Type of variation if applicable
            generation_source: Source of generation ('gemini', 'template', 'manual')
            auto_generate_audio: Whether to auto-generate TTS audio (default: True)
            
        Returns:
            The created Question object or None
        """
        try:
            question = Question(
                topic=topic,
                difficulty_level=level,
                text=text,
                sample_answer_text=sample_answer,
                keywords=keywords,
                parent_id=parent_id,
                variation_type=variation_type,
                is_generated=True,
                generation_source=generation_source,
                language='english',
                question_type='question'
            )
            db.session.add(question)
            db.session.commit()
            
            current_app.logger.info(f"Saved generated question: {text[:50]}...")
            
            # Auto-generate TTS audio for question and sample answer
            if auto_generate_audio:
                self._generate_audio_for_question(question)
            
            return question
            
        except Exception as e:
            current_app.logger.error(f"Error saving generated question: {e}")
            db.session.rollback()
            return None

    def _generate_audio_for_question(self, question: Question):
        """
        Generate TTS audio for a question in a background thread.
        This is called automatically after saving a generated question.
        """
        import threading
        
        def generate_in_background(question_id, text, sample_answer_text):
            try:
                from app.services.tts_service import TTSService
                import os
                import time
                
                tts = TTSService()
                upload_dir = tts._get_upload_base_dir()
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate question audio
                if text and len(text.strip()) >= 5:
                    timestamp = int(time.time() * 1000)
                    filename = f"q_{question_id}_{timestamp}.mp3"
                    output_path = os.path.join(upload_dir, filename)
                    audio_url = f"/uploads/questions/{filename}"
                    
                    if tts.generate_audio_standalone(text, output_path, voice_key='ava'):
                        # Update database using a new app context
                        from app import create_app, db
                        app = create_app()
                        with app.app_context():
                            from app.models import Question
                            q = Question.query.get(question_id)
                            if q:
                                q.audio_url = audio_url
                                db.session.commit()
                                print(f"✓ Auto-generated question audio for #{question_id}")
                
                # Generate sample answer audio
                if sample_answer_text and len(sample_answer_text.strip()) >= 5:
                    timestamp = int(time.time() * 1000)
                    filename = f"sa_{question_id}_{timestamp}.mp3"
                    output_path = os.path.join(upload_dir, filename)
                    audio_url = f"/uploads/questions/{filename}"
                    
                    if tts.generate_audio_standalone(sample_answer_text, output_path, voice_key='ava'):
                        from app import create_app, db
                        app = create_app()
                        with app.app_context():
                            from app.models import Question
                            q = Question.query.get(question_id)
                            if q:
                                q.sample_answer_audio_url = audio_url
                                db.session.commit()
                                print(f"✓ Auto-generated sample answer audio for #{question_id}")
                                
            except Exception as e:
                print(f"✗ Error auto-generating audio for question #{question_id}: {e}")
        
        # Run in background thread to not block the main request
        thread = threading.Thread(
            target=generate_in_background,
            args=(question.id, question.text, question.sample_answer_text),
            daemon=True
        )
        thread.start()


# Global instance
question_generator = QuestionGeneratorService()

