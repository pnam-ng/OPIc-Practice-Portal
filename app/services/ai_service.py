"""
AI Service for OPIc Practice Portal
Handles AI-powered scoring and feedback using Google AI Studio (Gemini)
COMPLETELY FREE - No credit card required!
Uses gemini-2.5-flash model (free tier, 60 requests/minute)
"""
import requests
from typing import Dict, Optional
from flask import current_app
import os
import json
import time


class AIService:
    """Service for AI-powered response scoring"""
    
    def __init__(self):
        # Using Google AI Studio (Gemini) - COMPLETELY FREE, no credit card required!
        # Get API key: https://aistudio.google.com/app/apikey
        # Free tier: 60 requests/minute, generous limits
        # Model: gemini-2.5-flash (free, fast, good for instruction following)
        self.api_provider = "google"
        self.model = "gemini-2.5-flash"  # Free Gemini model
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        self.api_token = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not self.api_token:
            try:
                from flask import has_app_context
                if has_app_context():
                    self.api_token = current_app.config.get("GOOGLE_AI_API_KEY") or current_app.config.get("GEMINI_API_KEY")
            except:
                pass
        
        self.max_retries = 3
        self.timeout = 90  # 90 seconds timeout (increased for API calls)
        self._rater_guidelines = None  # Cache for PDF content (loaded once)
        self._rater_summary = None  # Cache for PDF summary (concise version)
        self._system_prompt_base = None  # Cached system prompt with PDF summary
        self._pdf_loaded = False  # Flag to track if PDF has been loaded
        
        # Check API token (only log if we have app context)
        if not self.api_token:
            try:
                from flask import has_app_context
                if has_app_context():
                    current_app.logger.warning("⚠️ GOOGLE_AI_API_KEY not found. Get FREE key at https://aistudio.google.com/app/apikey (no credit card required!)")
            except:
                pass
        
    def _load_rater_guidelines(self) -> Optional[str]:
        """Load OPIc rater guidelines from PDF file (only once, then cached forever)"""
        if self._pdf_loaded:
            return self._rater_guidelines if self._rater_guidelines else ""
        
        try:
            # Try to find PDF file
            pdf_paths = [
                os.path.join('files', 'secrets-from-an-opic-rater.pdf'),
                os.path.join(current_app.root_path, '..', 'files', 'secrets-from-an-opic-rater.pdf'),
                current_app.config.get('OPIC_RATER_PDF_PATH', 'files/secrets-from-an-opic-rater.pdf')
            ]
            
            pdf_path = None
            for path in pdf_paths:
                if os.path.exists(path):
                    pdf_path = path
                    break
            
            if not pdf_path:
                current_app.logger.warning("OPIc rater PDF not found. AI will evaluate without PDF guidelines.")
                self._rater_guidelines = ""
                return ""
            
            # Try PyPDF2 first (lighter)
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    # Clean text
                    text = text.strip()
                    self._rater_guidelines = text  # Store full text
                    
                    # Create concise summary (extract key points, limit to ~1500 chars)
                    summary = self._summarize_guidelines(text)
                    self._rater_summary = summary
                    self._pdf_loaded = True
                    current_app.logger.info(f"✅ Loaded and summarized OPIc rater PDF ({len(text)} chars → {len(summary)} chars). Will reuse for all evaluations.")
                    return summary  # Return summary instead of full text
            except ImportError:
                pass
            
            # Try pdfplumber as fallback
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages[:5]:  # Limit to first 5 pages
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    
                    text = text.strip()
                    self._rater_guidelines = text  # Store full text
                    
                    # Create concise summary
                    summary = self._summarize_guidelines(text)
                    self._rater_summary = summary
                    self._pdf_loaded = True
                    current_app.logger.info(f"✅ Loaded and summarized OPIc rater PDF with pdfplumber ({len(text)} chars → {len(summary)} chars). Will reuse for all evaluations.")
                    return summary  # Return summary instead of full text
            except ImportError:
                pass
            
            # If no PDF library available, log warning
            current_app.logger.warning("No PDF library available (PyPDF2 or pdfplumber). Install with: pip install PyPDF2")
            self._rater_guidelines = ""
            self._pdf_loaded = True  # Mark as loaded (even if empty) to avoid retrying
            return ""
            
        except Exception as e:
            current_app.logger.error(f"Error loading OPIc rater PDF: {e}")
            self._rater_guidelines = ""
            self._pdf_loaded = True  # Mark as loaded to avoid retrying on error
            return ""
    
    def _summarize_guidelines(self, full_text: str) -> str:
        """
        Extract key points from OPIc rater PDF to create a concise summary
        Focuses on scoring criteria, evaluation methods, and key guidelines
        """
        if not full_text or len(full_text.strip()) < 100:
            return ""
        
        # Extract key sections using simple keyword-based extraction
        lines = full_text.split('\n')
        key_sections = []
        important_keywords = [
            'level', 'proficiency', 'score', 'rating', 'evaluation', 'criteria',
            'grammar', 'vocabulary', 'fluency', 'content', 'pronunciation',
            'accuracy', 'range', 'natural', 'relevant', 'complete',
            'intermediate', 'advanced', 'novice', 'superior',
            'task', 'function', 'context', 'topic', 'situation',
            'strength', 'weakness', 'improve', 'error', 'mistake'
        ]
        
        # Collect lines with important content
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if len(line_lower) > 20 and any(keyword in line_lower for keyword in important_keywords):
                # Get context (previous and next line if available)
                context = []
                if i > 0 and len(lines[i-1].strip()) > 10:
                    context.append(lines[i-1].strip())
                context.append(line.strip())
                if i < len(lines) - 1 and len(lines[i+1].strip()) > 10:
                    context.append(lines[i+1].strip())
                key_sections.extend(context)
        
        # If we found key sections, combine them
        if key_sections:
            summary = '\n'.join(key_sections[:50])  # Limit to ~50 lines
            # Limit total length to ~1500 characters
            if len(summary) > 1500:
                summary = summary[:1500] + "..."
            return summary.strip()
        
        # Fallback: Extract first 1500 chars with some structure
        if len(full_text) > 1500:
            # Try to break at sentence boundaries
            truncated = full_text[:1500]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')
            cut_point = max(last_period, last_newline)
            if cut_point > 1000:  # Only use if we found a reasonable break point
                return full_text[:cut_point + 1] + "..."
            return truncated + "..."
        
        return full_text
    
    def score_response(self, transcript: str, question_text: str, audio_features: Dict = None) -> Optional[Dict]:
        """
        Score an OPIc response using AI
        
        Args:
            transcript: The user's spoken response (transcribed text)
            question_text: The question text
            audio_features: Optional dict with audio analysis features (pitch, tempo, pauses, etc.)
            
        Returns:
            Dict with 'score', 'feedback', 'strengths', 'suggestions'
            None if scoring fails
        """
        try:
            # Load OPIc rater guidelines summary from PDF (only once, then cached)
            # Returns a concise summary (~1500 chars) of key evaluation criteria
            rater_guidelines = self._load_rater_guidelines()
            
            # Build system prompt (cached if PDF already loaded)
            if self._system_prompt_base is None:
                # Create base system prompt with clear OPIc test context
                system_prompt = """You are an OPIc (Oral Proficiency Interview - Computer) examiner evaluating English speaking responses for the OPIc test.

**CONTEXT**: You are evaluating responses from students taking the OPIc test, which is a standardized computer-based speaking proficiency assessment. Your evaluations will help students understand their speaking level and areas for improvement.

**YOUR TASK**: Evaluate English speaking responses on a scale of 0-100 based on OPIc evaluation criteria.

**IMPORTANT**: You must FIRST read and understand the question context, then evaluate how well the response answers that specific question in the context of the OPIc test."""
                
                # Add summarized PDF guidelines if available (only once)
                if rater_guidelines and rater_guidelines.strip():
                    system_prompt += f"""

**OPIC RATER GUIDELINES SUMMARY (Key evaluation criteria from official OPIc rater training):**
{rater_guidelines}

**IMPORTANT**: Use these OPIc rater guidelines as your primary reference for evaluation. These criteria are based on official OPIc rater standards. Apply them consistently to all OPIc test responses."""
                
                # Complete the system prompt with evaluation factors
                system_prompt += """

Consider these factors:
1. Grammar and accuracy (20 points)
2. Vocabulary range and usage (20 points)
3. Fluency and naturalness (20 points)
4. Content relevance and completeness (20 points) - **Evaluate if the response appropriately addresses the question**
5. **Tone and Prosody** (20 points):
   - Natural intonation patterns
   - Appropriate stress and emphasis
   - Rhythm and pacing
   - Expressiveness and clarity

**IMPORTANT - LANGUAGE REQUIREMENT:**
- You must provide ALL feedback in Vietnamese (Tiếng Việt)
- The feedback, strengths, and suggestions must be written in Vietnamese
- Only the JSON structure keys ("score", "feedback", "strengths", "suggestions") remain in English
- All text content must be in Vietnamese

**CRITICAL - PERSONALIZATION REQUIREMENT:**
- Each response is UNIQUE - you must analyze the SPECIFIC response provided
- Do NOT use generic or template-based feedback
- Provide personalized feedback based on the ACTUAL content, grammar, vocabulary, and fluency of THIS specific response
- Mention specific examples from the user's response (phrases, sentences, vocabulary choices, etc.)
- Each user's feedback must be different and tailored to their individual response
- If two users give similar responses, their feedback should still reflect their unique expression style, specific words used, and individual strengths/weaknesses

Provide:
- A numerical score out of 100 (based on THIS specific response's quality)
- Brief personalized feedback in Vietnamese (2-3 sentences) that mentions SPECIFIC aspects of this response, including comments on tone/pronunciation and how well THIS response addresses the question
- 2-3 specific strengths in Vietnamese that are UNIQUE to this response (mention specific examples from their answer)
- 2-3 specific areas for improvement in Vietnamese that are SPECIFIC to this response (cite actual errors, weaknesses, or areas where this particular response could be better)

Format your response as JSON with these keys: score, feedback (Vietnamese, personalized), strengths (array of Vietnamese strings, specific to this response), suggestions (array of Vietnamese strings, specific to this response)."""
                
                # Cache the system prompt (with PDF included)
                self._system_prompt_base = system_prompt
                current_app.logger.info("✅ System prompt with PDF guidelines cached. Will reuse for all evaluations.")
            else:
                # Use cached system prompt (PDF already included - no need to reload PDF)
                system_prompt = self._system_prompt_base
                current_app.logger.debug("Using cached system prompt with PDF guidelines (PDF already internalized)")

            # Build user prompt - Question context first, then response
            user_prompt = f"""**QUESTION CONTEXT:**
{question_text}

**USER'S RESPONSE:**
{transcript}

**EVALUATION TASK:**
First, read and understand the question above. Then evaluate whether the user's response appropriately addresses the question. Consider:
- Does the response answer the question asked?
- Is the content relevant to the question topic?
- Is the response complete and appropriate in length?
- How well does the response demonstrate understanding of the question?

Now provide your evaluation:"""

            # Add audio features analysis to prompt
            if audio_features:
                features_desc = []
                if audio_features.get('avg_pitch'):
                    features_desc.append(f"- Average pitch: {audio_features['avg_pitch']:.1f} Hz")
                if audio_features.get('pitch_variance'):
                    pitch_var = audio_features['pitch_variance']
                    if pitch_var < 50:
                        features_desc.append("- Pitch variation: Very monotone (little intonation)")
                    elif pitch_var < 150:
                        features_desc.append("- Pitch variation: Somewhat monotone")
                    else:
                        features_desc.append("- Pitch variation: Good variation (natural intonation)")
                
                if audio_features.get('speaking_rate'):
                    rate = audio_features['speaking_rate']
                    if rate < 120:
                        features_desc.append(f"- Speaking rate: Slow ({rate:.1f} words/min) - may affect naturalness")
                    elif rate > 200:
                        features_desc.append(f"- Speaking rate: Very fast ({rate:.1f} words/min) - may affect clarity")
                    else:
                        features_desc.append(f"- Speaking rate: Good pace ({rate:.1f} words/min)")
                
                if audio_features.get('pause_ratio'):
                    pause_ratio = audio_features['pause_ratio']
                    if pause_ratio > 0.3:
                        features_desc.append("- Pauses: Too many pauses (may indicate hesitation)")
                    elif pause_ratio < 0.1:
                        features_desc.append("- Pauses: Very few pauses (may sound rushed)")
                    else:
                        features_desc.append("- Pauses: Appropriate pause frequency")
                
                if audio_features.get('volume_consistency'):
                    vol_consistency = audio_features['volume_consistency']
                    if vol_consistency < 0.7:
                        features_desc.append("- Volume: Inconsistent volume (may affect clarity)")
                    else:
                        features_desc.append("- Volume: Consistent volume level")
                
                if features_desc:
                    user_prompt += "\n\n**AUDIO ANALYSIS (Tone & Prosody):**\n" + "\n".join(features_desc)

            user_prompt += """\n\n**EVALUATION INSTRUCTIONS:**
1. Review the QUESTION CONTEXT above
2. Analyze how well THIS SPECIFIC USER'S RESPONSE addresses the question - focus on the actual words, phrases, and sentences they used
3. Evaluate THIS response's content quality, relevance, and completeness - identify what they said specifically
4. Assess THIS response's speaking tone and prosody based on the audio analysis
5. Provide personalized feedback that mentions SPECIFIC examples from THIS user's response (their actual words, phrases, sentence structures, vocabulary choices)
6. DO NOT use generic feedback - every response is different, so every feedback must be unique and specific

**REMEMBER**: This is ONE user's unique response. Your feedback must reflect what THIS specific user said, not generic advice. Mention their actual words, identify their specific strengths in this response, and cite their specific weaknesses or areas to improve in this response."""

            # Add concise JSON format instruction (feedback must be personalized and in Vietnamese)
            user_prompt += "\n\nRespond in JSON format (ALL text in Vietnamese/Tiếng Việt, personalized for THIS specific response): {\"score\": number, \"feedback\": \"personalized text in Vietnamese mentioning specific aspects of this response\", \"strengths\": [\"Vietnamese text with specific examples from their response\"], \"suggestions\": [\"Vietnamese text with specific areas from their response to improve\"]}"

            # Call Google AI Studio (Gemini) API
            # For Gemini, we can use system instruction if supported, otherwise combine
            # Note: Gemini API doesn't support separate system/user roles in v1beta
            # So we combine them with clear separation
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            content = self._call_google_api(combined_prompt)
            
            # If content is None and it was MAX_TOKENS, try with a shorter prompt
            if content is None:
                current_app.logger.warning("First attempt failed, trying with shorter prompt...")
                # Retry with a simplified prompt (without full PDF content if it was included)
                simplified_prompt = f"""You are an OPIc language proficiency evaluator. Evaluate THIS SPECIFIC response on a 0-100 scale for:
- Grammar (25) - analyze the ACTUAL grammar used in this response
- Vocabulary (25) - evaluate the SPECIFIC words and phrases this user chose
- Fluency (25) - assess how THIS response flows naturally
- Content relevance (25) - check how well THIS specific response answers the question

QUESTION: {question_text}
RESPONSE: {transcript}

**CRITICAL REQUIREMENTS:**
1. Provide ALL feedback in Vietnamese (Tiếng Việt)
2. Make feedback PERSONALIZED - mention specific examples from THIS user's response
3. Do NOT use generic feedback - analyze what THIS user actually said
4. Each feedback must be unique to this specific response

Respond in JSON format (personalized feedback in Vietnamese): {{"score": number, "feedback": "Vietnamese text with specific examples from their response", "strengths": ["Vietnamese text mentioning their specific words/phrases"], "suggestions": ["Vietnamese text citing specific areas from their response"]}}"""
                content = self._call_google_api(simplified_prompt)
            
            if not content:
                return None
            
            # Parse the response (handle both JSON and text formats)
            result = self._parse_ai_response(content)
            
            current_app.logger.info(f"AI scoring successful for transcript: {transcript[:50]}...")
            return result
            
        except requests.exceptions.RequestException as e:
            # Network/API errors
            current_app.logger.error(f"Network error in AI scoring: {e}")
            return None
        except Exception as e:
            # Catch all other errors to prevent crashes
            current_app.logger.error(f"Error in AI scoring: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return None
    
    def _parse_ai_response(self, content: str) -> Dict:
        """
        Parse AI response into structured format
        Handles both JSON and natural language responses
        """
        import json
        import re
        
        # Clean content - remove markdown code blocks if present
        content = content.strip()
        # Remove ```json or ``` markers
        content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        # Try to find JSON object - look for opening brace and find matching closing brace
        # This handles multi-line JSON with nested objects/arrays properly
        brace_count = 0
        json_start = -1
        json_end = -1
        
        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    json_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and json_start != -1:
                    json_end = i + 1
                    break
        
        if json_start != -1 and json_end != -1:
            json_str = content[json_start:json_end]
            try:
                data = json.loads(json_str)
                
                # Validate and extract data
                feedback = data.get('feedback', '')
                # Ensure feedback is a string and not truncated
                if not isinstance(feedback, str):
                    feedback = str(feedback)
                
                # Log feedback length for debugging
                try:
                    from flask import has_app_context
                    if has_app_context():
                        current_app.logger.info(f"Parsed AI feedback: length={len(feedback)} chars, score={data.get('score')}, preview={feedback[:100]}...")
                except:
                    pass
                
                return {
                    'score': self._extract_score(data.get('score', content)),
                    'feedback': feedback,  # Use the full feedback string
                    'strengths': data.get('strengths', []) if isinstance(data.get('strengths'), list) else [],
                    'suggestions': data.get('suggestions', []) if isinstance(data.get('suggestions'), list) else []
                }
            except json.JSONDecodeError as e:
                current_app.logger.warning(f"JSON parsing failed: {e}. Attempting fallback parsing.")
                # Try to find JSON with regex as fallback
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        return {
                            'score': self._extract_score(data.get('score', content)),
                            'feedback': data.get('feedback', ''),
                            'strengths': data.get('strengths', []) if isinstance(data.get('strengths'), list) else [],
                            'suggestions': data.get('suggestions', []) if isinstance(data.get('suggestions'), list) else []
                        }
                    except json.JSONDecodeError:
                        pass
        
        # Fallback: Extract score and feedback from text
        score = self._extract_score(content)
        
        # Try to extract feedback sections
        feedback_match = re.search(r'feedback[:\s]+([^.]+)', content, re.IGNORECASE)
        feedback = feedback_match.group(1).strip() if feedback_match else content[:200]
        
        # Extract strengths and suggestions
        strengths = self._extract_list_items(content, ['strength', 'good', 'well'])
        suggestions = self._extract_list_items(content, ['suggest', 'improve', 'better', 'work on'])
        
        return {
            'score': score,
            'feedback': feedback,
            'strengths': strengths[:3],  # Limit to 3 items
            'suggestions': suggestions[:3]  # Limit to 3 items
        }
    
    def _extract_score(self, text: str) -> int:
        """Extract numerical score from text"""
        import re
        
        # Look for numbers 0-100
        score_match = re.search(r'\b(\d{1,2}|100)\b', str(text))
        if score_match:
            score = int(score_match.group(1))
            return max(0, min(100, score))  # Clamp between 0-100
        
        return 50  # Default score if not found
    
    def _extract_list_items(self, text: str, keywords: list) -> list:
        """Extract list items containing keywords"""
        import re
        
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Extract bullet points or numbered items
                bullet_match = re.search(r'[-•*]\s*(.+?)(?:\.|$)', line)
                if bullet_match:
                    items.append(bullet_match.group(1).strip())
                elif len(line.strip()) > 10:  # If no bullet, use the line itself
                    # Remove keywords to get clean item
                    clean_line = re.sub(r'|'.join(keywords), '', line, flags=re.IGNORECASE).strip()
                    if clean_line and len(clean_line) > 10:
                        items.append(clean_line)
        
        return items
    
    def _call_google_api(self, prompt: str) -> Optional[str]:
        """
        Call Google AI Studio (Gemini) API - COMPLETELY FREE!
        """
        # Refresh API token from config if not set
        if not self.api_token:
            self.api_token = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not self.api_token:
                try:
                    from flask import has_app_context
                    if has_app_context():
                        self.api_token = current_app.config.get("GOOGLE_AI_API_KEY") or current_app.config.get("GEMINI_API_KEY")
                except:
                    pass
        
        if not self.api_token:
            try:
                from flask import has_app_context
                if has_app_context():
                    current_app.logger.error("GOOGLE_AI_API_KEY not set. Get free key at https://aistudio.google.com/app/apikey")
            except:
                pass
            return None
        
        # Google Gemini API format
        api_url = f"{self.api_url}?key={self.api_token}"
        
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
                "maxOutputTokens": 4096,  # Increased to 4096 to allow full feedback responses
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                current_app.logger.debug(f"Calling Google AI (Gemini) API (attempt {attempt + 1}/{self.max_retries})...")
                
                # Make API call with timeout
                try:
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout,
                        stream=False  # Don't stream to avoid connection issues
                    )
                except requests.exceptions.ConnectionError as e:
                    current_app.logger.error(f"Connection error calling Google AI API: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                except requests.exceptions.Timeout as e:
                    current_app.logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Google Gemini returns format: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
                    content = None
                    if isinstance(result, dict) and 'candidates' in result:
                        candidates = result.get('candidates', [])
                        if len(candidates) > 0:
                            candidate = candidates[0]
                            finish_reason = candidate.get('finishReason', '')
                            
                            # Check if response was cut off
                            if finish_reason == 'MAX_TOKENS':
                                current_app.logger.warning(f"Response was cut off due to MAX_TOKENS. Content length: {len(content) if content else 0} chars. The response may be incomplete. Consider increasing maxOutputTokens or reducing prompt size.")
                            
                            content_obj = candidate.get('content', {})
                            if isinstance(content_obj, dict):
                                parts = content_obj.get('parts', [])
                                if len(parts) > 0:
                                    # Get text from first part
                                    first_part = parts[0]
                                    if isinstance(first_part, dict):
                                        content = first_part.get('text', '')
                                    elif isinstance(first_part, str):
                                        content = first_part
                                    
                                    # Log content length for debugging
                                    try:
                                        from flask import has_app_context
                                        if has_app_context():
                                            current_app.logger.info(f"Extracted content from API: length={len(content) if content else 0} chars, finish_reason={finish_reason}, preview={content[:100] if content else 'None'}...")
                                    except:
                                        pass
                                
                                # If no text found, log the structure for debugging
                                if not content:
                                    current_app.logger.error(f"No text found in parts. Finish reason: {finish_reason}. Content structure: {content_obj}")
                                    # Try to get any text from the response as fallback
                                    if finish_reason == 'MAX_TOKENS':
                                        current_app.logger.error("Response exceeded token limit. The prompt may be too long or maxOutputTokens too low.")
                            else:
                                current_app.logger.warning(f"Content is not a dict: {type(content_obj)}")
                        else:
                            current_app.logger.warning(f"No candidates in response: {result}")
                    else:
                        current_app.logger.warning(f"Unexpected response format: {result}")
                    
                    # Final check - ensure we have valid text content
                    if not content or not isinstance(content, str):
                        current_app.logger.error(f"Failed to extract text content. Result: {result}")
                        return None
                    
                    # Clean up content (remove markdown code blocks if present)
                    content = content.strip()
                    if content.startswith('```'):
                        # Remove markdown code block markers
                        lines = content.split('\n')
                        # Remove first line if it's ```json or ```
                        if lines[0].strip().startswith('```'):
                            lines = lines[1:]
                        # Remove last line if it's ```
                        if lines and lines[-1].strip() == '```':
                            lines = lines[:-1]
                        content = '\n'.join(lines).strip()
                    
                    current_app.logger.debug(f"✅ Google AI (Gemini) API call successful. Content length: {len(content)}")
                    return content
                    
                elif response.status_code == 429:
                    current_app.logger.warning("Rate limit exceeded. Waiting before retry...")
                    time.sleep(5)
                    continue
                elif response.status_code == 403:
                    error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    error_msg = error_info.get('error', {}).get('message', 'API key invalid or quota exceeded')
                    current_app.logger.error(f"Google AI API error (403): {error_msg}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                else:
                    current_app.logger.error(f"Google AI API error: {response.status_code} - {response.text[:200]}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                current_app.logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
                
            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Request error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                # Catch any other unexpected errors
                current_app.logger.error(f"Unexpected error in API call: {e}")
                import traceback
                current_app.logger.error(traceback.format_exc())
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        current_app.logger.error("Failed to get response from Google AI API after all retries")
        return None
    
    def health_check(self) -> bool:
        """Check if Google AI (Gemini) API is available and working"""
        try:
            if not self.api_token:
                current_app.logger.error("GOOGLE_AI_API_KEY not set")
                return False
            
            # Google Gemini health check
            api_url = f"{self.api_url}?key={self.api_token}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": "Hello"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            return response.status_code in [200, 429]  # 429 = rate limited but API works
            
        except Exception as e:
            current_app.logger.error(f"Google AI API health check failed: {e}")
            return False


# Global instance
ai_service = AIService()

