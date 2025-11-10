"""
Chatbot Service for OPIc Practice Portal
Handles AI-powered chatbot using Google AI Studio (Gemini)
"""
import requests
from typing import Optional, List, Dict
from flask import current_app
import os
import json
import time


class ChatbotService:
    """Service for AI-powered chatbot"""
    
    def __init__(self):
        # Using Google AI Studio (Gemini) - COMPLETELY FREE!
        self.api_provider = "google"
        
        # Model configuration with fallback support
        # Based on available models and rate limits:
        # - gemini-2.5-flash: RPD 250 (currently exceeded)
        # - gemini-2.5-flash-lite: RPD 1000 (best fallback)
        # - gemini-2.0-flash: RPD 200
        # - gemini-2.0-flash-lite: RPD 200
        # - gemini-2.5-pro: RPD 50
        self.default_model = "gemini-2.5-flash"
        self.fallback_models = [
            "gemini-2.5-flash-lite",  # First fallback (RPD: 1000 - highest limit)
            "gemini-2.0-flash",       # Second fallback (RPD: 200)
            "gemini-2.0-flash-lite",   # Third fallback (RPD: 200)
            "gemini-2.5-pro",          # Fourth fallback (RPD: 50)
        ]
        self.model = self.default_model
        self.current_model_index = 0  # 0 = default, 1+ = fallback index
        self.last_model_check = 0  # Timestamp of last model availability check
        self.model_check_interval = 3600  # Check default model availability every hour
        
        self._update_api_url()
        
        # Don't set api_token in __init__ - get it dynamically
        self._api_token_cache = None
        
        self.max_retries = 3
        self.timeout = 90
        
        # System prompt for OPIc chatbot
        self._system_prompt = self._build_system_prompt()
    
    def _get_api_token(self):
        """Get API token, checking environment and Flask config dynamically"""
        # Always check environment first (most up-to-date)
        token = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if token:
            self._api_token_cache = token
            return token
        
        # Try Flask config if in app context
        try:
            from flask import has_app_context, current_app
            if has_app_context():
                token = current_app.config.get("GOOGLE_AI_API_KEY") or current_app.config.get("GEMINI_API_KEY")
                if token:
                    self._api_token_cache = token
                    return token
        except:
            pass
        
        # Return cached token if available (fallback)
        return self._api_token_cache
    
    @property
    def api_token(self):
        """Property to get API token dynamically"""
        return self._get_api_token()
    
    @api_token.setter
    def api_token(self, value):
        """Setter for API token (for backward compatibility)"""
        self._api_token_cache = value
    
    def _update_api_url(self):
        """Update API URL based on current model"""
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    def _switch_to_fallback_model(self):
        """Switch to next fallback model if available"""
        if self.current_model_index < len(self.fallback_models):
            self.current_model_index += 1
            self.model = self.fallback_models[self.current_model_index - 1]
            self._update_api_url()
            try:
                from flask import has_app_context
                if has_app_context():
                    current_app.logger.warning(f"Switched to fallback model: {self.model}")
            except:
                pass
            return True
        return False
    
    def _try_switch_back_to_default(self):
        """Try to switch back to default model if it's available again"""
        import time
        current_time = time.time()
        
        # Only check periodically to avoid too many API calls
        if current_time - self.last_model_check < self.model_check_interval:
            return False
        
        self.last_model_check = current_time
        
        # Test if default model is available
        if self._test_model_availability(self.default_model):
            self.model = self.default_model
            self.current_model_index = 0
            self._update_api_url()
            try:
                from flask import has_app_context
                if has_app_context():
                    current_app.logger.info(f"Switched back to default model: {self.model}")
            except:
                pass
            return True
        return False
    
    def _test_model_availability(self, model_name: str) -> bool:
        """Test if a model is available by making a simple API call"""
        if not self.api_token:
            return False
        
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_token}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": "test"}]}],
            "generationConfig": {"maxOutputTokens": 5}
        }
        
        try:
            response = requests.post(test_url, headers=headers, json=payload, timeout=10)
            # If we get 200 or 429 (rate limit but model works), model is available
            # If we get 403 with quota exceeded, model is not available
            if response.status_code == 200:
                return True
            elif response.status_code == 429:
                return True  # Rate limited but model works
            elif response.status_code == 403:
                error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_info.get('error', {}).get('message', '')
                # Check if it's quota exceeded (not just invalid key)
                if 'quota' in error_msg.lower() or 'exceeded' in error_msg.lower():
                    return False
                return True  # Other 403 might be temporary
            return False
        except:
            return False
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for OPIc chatbot"""
        return """You are a helpful AI assistant for the OPIc (Oral Proficiency Interview - Computer) Practice Portal.

**YOUR ROLE**: You help users understand:
1. OPIc test format, structure, and evaluation criteria
2. How to use the OPIc Practice Portal app features
3. Best practices for OPIc test preparation
4. Speaking tips and strategies for OPIc success

**ABOUT OPIc TEST**:
- OPIc is a standardized computer-based speaking proficiency assessment
- Tests are available in multiple proficiency levels (IM, IH, AL)
- Questions cover various topics (news, technology, travel, food, etc.)
- Responses are evaluated on grammar, vocabulary, fluency, content relevance, and tone/prosody
- Scores range from 0-100 points

**ABOUT THIS APP**:
- Practice Mode: Practice individual questions with immediate AI feedback
- Test Mode: Complete a full 12-question simulated OPIc test
- AI Feedback: Get personalized feedback on your responses with scores and suggestions
- Audio Recording: Record your responses and listen back
- Progress Tracking: Track your practice history and daily streaks

**RESPONSE GUIDELINES**:
- Be friendly, encouraging, and helpful
- Provide clear, concise answers
- Use examples when helpful
- If you don't know something specific about the app, admit it but offer general OPIc advice
- Keep responses conversational and easy to understand
- Use Vietnamese (Tiếng Việt) if the user asks in Vietnamese, otherwise respond in English
- For script generation, you could follow P.R.E.P structure: Point, Reason, Example, Point.

**IMPORTANT**: 
- You can help with general OPIc questions, test preparation tips, and app usage
- You cannot access specific user data or modify the system
- Always encourage users to practice regularly for best results
- If user request script generation, please ensure duration limit maximum is 2 minutes for each question, so you must use less words to generate the script.

Now, answer the user's question about OPIc test or this practice portal:"""
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Optional[str]:
        """
        Get chatbot response
        
        Args:
            message: User's message
            conversation_history: Optional list of previous messages for context
                Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        
        Returns:
            Chatbot response text or None if failed
        """
        try:
            # Build conversation context
            prompt = self._system_prompt + "\n\n"
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-5:]:  # Keep last 5 exchanges for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        prompt += f"**User**: {content}\n\n"
                    elif role == "assistant":
                        prompt += f"**Assistant**: {content}\n\n"
            
            # Add current user message
            prompt += f"**User**: {message}\n\n**Assistant**:"
            
            # Call Gemini API
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.info(f"Calling Gemini API with prompt length: {len(prompt)}")
            except:
                pass
            
            response_text = self._call_gemini_api(prompt)
            
            if response_text:
                try:
                    from flask import has_app_context, current_app
                    if has_app_context():
                        current_app.logger.info(f"Chatbot response generated for: {message[:50]}...")
                except:
                    pass
                return response_text
            else:
                try:
                    from flask import has_app_context, current_app
                    if has_app_context():
                        current_app.logger.warning(f"Chatbot API returned None for: {message[:50]}...")
                except:
                    pass
                return None
                
        except Exception as e:
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.error(f"Error in chatbot: {e}")
                    import traceback
                    current_app.logger.error(traceback.format_exc())
                else:
                    print(f"Error in chatbot: {e}")
                    import traceback
                    traceback.print_exc()
            except:
                import traceback
                traceback.print_exc()
            return None
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API"""
        # Get API token dynamically (always fresh from environment)
        api_token = self._get_api_token()
        
        if not api_token:
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.error("GOOGLE_AI_API_KEY not set. Chatbot requires API key.")
                    # Log what we checked
                    env_key = os.getenv("GOOGLE_AI_API_KEY")
                    env_gemini = os.getenv("GEMINI_API_KEY")
                    config_key = current_app.config.get("GOOGLE_AI_API_KEY")
                    config_gemini = current_app.config.get("GEMINI_API_KEY")
                    current_app.logger.error(f"API Key check: env GOOGLE_AI_API_KEY={bool(env_key)}, env GEMINI_API_KEY={bool(env_gemini)}, config GOOGLE_AI_API_KEY={bool(config_key)}, config GEMINI_API_KEY={bool(config_gemini)}")
            except Exception as e:
                import traceback
                print(f"Error checking API token: {e}")
                traceback.print_exc()
            return None
        
        api_url = f"{self.api_url}?key={api_token}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": 2048,
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.info(f"Calling Gemini API for chatbot (attempt {attempt + 1}/{self.max_retries})...")
                    current_app.logger.info(f"API URL: {self.api_url}")
                    current_app.logger.info(f"API Token present: {bool(api_token)}")
                    current_app.logger.info(f"Model: {self.model}")
                else:
                    print(f"Calling Gemini API for chatbot (attempt {attempt + 1}/{self.max_retries})...")
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=False
                )
                
                # Log response status for debugging
                try:
                    from flask import has_app_context, current_app
                    if has_app_context():
                        current_app.logger.info(f"Gemini API response status: {response.status_code}")
                    else:
                        print(f"Gemini API response status: {response.status_code}")
                except:
                    pass
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract text from Gemini response
                    content = None
                    if isinstance(result, dict) and 'candidates' in result:
                        candidates = result.get('candidates', [])
                        if len(candidates) > 0:
                            candidate = candidates[0]
                            content_obj = candidate.get('content', {})
                            if isinstance(content_obj, dict):
                                parts = content_obj.get('parts', [])
                                if len(parts) > 0:
                                    first_part = parts[0]
                                    if isinstance(first_part, dict):
                                        content = first_part.get('text', '')
                                    elif isinstance(first_part, str):
                                        content = first_part
                    
                    if content:
                        current_app.logger.debug(f"Chatbot response received: {len(content)} chars")
                        # Try to switch back to default model if we're on fallback
                        if self.current_model_index > 0:
                            self._try_switch_back_to_default()
                        return content.strip()
                    else:
                        # Log full response for debugging
                        try:
                            response_debug = json.dumps(result, indent=2)[:500] if isinstance(result, dict) else str(result)[:500]
                            current_app.logger.warning(f"No content in Gemini response. Response structure: {response_debug}")
                        except:
                            current_app.logger.warning(f"No content in Gemini response. Response type: {type(result)}")
                        return None
                        
                elif response.status_code == 429:
                    # Rate limit - try fallback model if available
                    if self.current_model_index == 0:  # Currently using default model
                        if self._switch_to_fallback_model():
                            # Retry with fallback model
                            api_token = self._get_api_token()
                            api_url = f"{self.api_url}?key={api_token}"
                            current_app.logger.info(f"Rate limited on {self.default_model}, switching to {self.model}")
                            continue
                    
                    # If already on fallback or no fallback available, wait and retry
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) * 2
                        current_app.logger.warning(f"Rate limited on {self.model}. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        current_app.logger.error(f"Rate limit exceeded for {self.model}")
                        return None
                elif response.status_code == 403:
                    # Check if it's quota exceeded (not just invalid key)
                    error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    error_msg = error_info.get('error', {}).get('message', '')
                    
                    if 'quota' in error_msg.lower() or 'exceeded' in error_msg.lower() or 'RPD' in error_msg:
                        # Quota exceeded - try fallback model
                        if self.current_model_index == 0:  # Currently using default model
                            if self._switch_to_fallback_model():
                                # Retry with fallback model
                                api_token = self._get_api_token()
                                api_url = f"{self.api_url}?key={api_token}"
                                current_app.logger.warning(f"Quota exceeded on {self.default_model}, switching to {self.model}")
                                continue
                        else:
                            current_app.logger.error(f"Quota exceeded on fallback model {self.model}: {error_msg}")
                            return None
                    else:
                        # Other 403 error (invalid key, etc.)
                        current_app.logger.error(f"Gemini API error (403): {error_msg}")
                        return None
                elif response.status_code == 400:
                    # Bad request - check if it's an API key issue
                    error_text = response.text
                    current_app.logger.error(f"Gemini API bad request: {error_text}")
                    if 'API_KEY' in error_text or 'key' in error_text.lower():
                        current_app.logger.error("Invalid or missing API key")
                    return None
                else:
                    # Log detailed error information
                    error_text = response.text[:500] if response.text else "No error text"
                    try:
                        error_json = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        error_detail = json.dumps(error_json, indent=2)[:500] if error_json else error_text
                    except:
                        error_detail = error_text
                    
                    try:
                        from flask import has_app_context, current_app
                        if has_app_context():
                            current_app.logger.error(f"Gemini API error: {response.status_code}")
                            current_app.logger.error(f"Error response: {error_detail}")
                            current_app.logger.error(f"Response headers: {dict(response.headers)}")
                        else:
                            print(f"Gemini API error: {response.status_code}")
                            print(f"Error response: {error_detail}")
                    except:
                        print(f"Gemini API error: {response.status_code} - {error_text}")
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                current_app.logger.error("Chatbot API timeout")
                return None
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                current_app.logger.error("Chatbot API connection error")
                return None
            except Exception as e:
                current_app.logger.error(f"Unexpected error in chatbot API call: {e}")
                return None
        
        return None
    
    def health_check(self) -> bool:
        """Check if chatbot service is available"""
        api_token = self._get_api_token()
        if not api_token:
            return False
        # Simple test message
        test_response = self.chat("Hello")
        return test_response is not None


# Global instance
chatbot_service = ChatbotService()

