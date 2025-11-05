"""
Generate sample answers for questions that don't have them
Uses Gemini model (same as chatbot) to generate sample answers based on question text
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Question
from app.services.chatbot_service import ChatbotService
import time

def generate_sample_answer(question_text: str, question_topic: str = None, difficulty_level: str = None) -> str:
    """
    Generate a sample answer for a question using Gemini
    
    Args:
        question_text: The question text
        question_topic: The topic of the question (optional)
        difficulty_level: The difficulty level (IM, IH, AL) (optional)
    
    Returns:
        Generated sample answer text
    """
    chatbot_service = ChatbotService()
    
    # Build prompt for sample answer generation
    prompt = f"""You are an expert OPIc (Oral Proficiency Interview - Computer) test rater and educator.

**TASK**: Generate a high-quality sample answer for an OPIc test question.

**QUESTION**:
{question_text}

"""
    
    if question_topic:
        prompt += f"**Topic**: {question_topic}\n\n"
    
    if difficulty_level:
        prompt += f"**Difficulty Level**: {difficulty_level}\n\n"
    
    prompt += """**INSTRUCTIONS**:
1. Generate a natural, fluent sample answer that demonstrates good English speaking proficiency
2. The answer should be appropriate for an OPIc test response
3. Keep it conversational and natural (as if spoken, not written)
4. The answer should be approximately 1-2 minutes when spoken (roughly 150-250 words)
5. Use appropriate grammar and vocabulary for the difficulty level
6. Include personal examples or details to make it authentic
7. The answer should directly address the question
8. Make it sound like a real person speaking, not a script

**IMPORTANT**: 
- Generate ONLY the sample answer text, no explanations or meta-commentary
- Do not include "Sample answer:" or any prefix
- Write it as if someone is speaking their response
- Keep it natural and conversational

**SAMPLE ANSWER**:"""
    
    # Call Gemini API
    response = chatbot_service._call_gemini_api(prompt)
    
    if response:
        # Clean up the response (remove any prefixes that might have been added)
        response = response.strip()
        # Remove common prefixes if they exist
        prefixes = ["Sample answer:", "Answer:", "Here's a sample answer:", "Here is a sample answer:"]
        for prefix in prefixes:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
        
        return response
    else:
        return None

def main():
    """Main function to generate sample answers for questions without them"""
    app = create_app()
    
    with app.app_context():
        # Find questions without sample answers
        questions = Question.query.filter(
            (Question.sample_answer_text == None) | 
            (Question.sample_answer_text == '') |
            (Question.sample_answer_text == 'None')
        ).all()
        
        total = len(questions)
        print(f"Found {total} questions without sample answers")
        
        if total == 0:
            print("All questions already have sample answers!")
            return
        
        # Check if API key is available
        chatbot_service = ChatbotService()
        if not chatbot_service.api_token:
            print("ERROR: GOOGLE_AI_API_KEY not set. Please set it in your environment or config.")
            print("Get a free key at: https://aistudio.google.com/app/apikey")
            return
        
        print(f"Using Gemini model: {chatbot_service.model}")
        print(f"API URL: {chatbot_service.api_url}")
        print("\nStarting generation...")
        print("=" * 60)
        
        successful = 0
        failed = 0
        skipped = 0
        
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{total}] Processing Question ID {question.id}...")
            print(f"Topic: {question.topic}")
            
            if not question.text:
                print(f"  ⚠️  Skipping: Question has no text")
                skipped += 1
                continue
            
            # Show question text preview
            question_preview = question.text[:100] + "..." if len(question.text) > 100 else question.text
            print(f"Question: {question_preview}")
            
            try:
                # Generate sample answer
                print("  Generating sample answer...")
                sample_answer = generate_sample_answer(
                    question_text=question.text,
                    question_topic=question.topic,
                    difficulty_level=question.difficulty_level
                )
                
                if sample_answer and sample_answer.strip():
                    # Update question with sample answer
                    question.sample_answer_text = sample_answer.strip()
                    db.session.commit()
                    
                    print(f"  ✅ Generated sample answer ({len(sample_answer)} characters)")
                    successful += 1
                else:
                    print(f"  ❌ Failed to generate sample answer (empty response)")
                    failed += 1
                
                # Rate limiting: wait 1 second between requests (Gemini free tier: 60 req/min)
                if i < total:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                failed += 1
                db.session.rollback()
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("Generation complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Skipped: {skipped}")
        print(f"📊 Total processed: {total}")

if __name__ == '__main__':
    main()

