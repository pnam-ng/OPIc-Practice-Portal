"""
TTS Service for OPIc Practice Portal
Uses edge-tts (Microsoft Edge Text-to-Speech) for free, high-quality neural voices.
"""
import os
import asyncio
import threading
import edge_tts
from flask import current_app

class TTSService:
    """Service for generating Text-to-Speech audio using edge-tts"""
    
    # Voice mapping - using "Ava" as requested for OPIc interviewer style
    VOICE_MAPPING = {
        'ava': 'en-US-AvaNeural',      # The requested voice (OPIc interviewer style)
        'jenny': 'en-US-JennyNeural',  # Good alternative
        'guy': 'en-US-GuyNeural',      # Male option
        'aria': 'en-US-AriaNeural'     # Another female option
    }
    
    def __init__(self):
        self.default_voice = self.VOICE_MAPPING['aria']
    
    async def _generate_audio_async(self, text: str, output_path: str, voice: str) -> bool:
        """Async internal method to generate audio"""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            # We can't log to current_app here easily if it's not in context, 
            # but we are in a thread where we might lose context. 
            # However, we are just returning False and logging in the caller.
            print(f"Error in edge-tts generation: {e}")
            return False

    def generate_audio(self, text: str, output_path: str, voice_key: str = 'aria') -> bool:
        """
        Generate audio file from text using edge-tts.
        
        Args:
            text: Text to convert to speech
            output_path: Full path to save the audio file
            voice_key: Key from VOICE_MAPPING (default: 'aria')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get voice ID
            voice = self.VOICE_MAPPING.get(voice_key.lower(), self.default_voice)
            
            current_app.logger.info(f"Generating TTS audio using voice: {voice}")
            
            # Run async function in a separate thread with its own loop
            # This avoids conflicts with Flask's loop or nest_asyncio issues
            result = [False]
            
            def run_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(self._generate_audio_async(text, output_path, voice))
                    result[0] = success
                except Exception as e:
                    print(f"Thread error: {e}")
                finally:
                    loop.close()

            t = threading.Thread(target=run_in_thread)
            t.start()
            t.join()
                
            # Verify file was created
            if result[0] and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                current_app.logger.info(f"TTS audio saved to: {output_path}")
                return True
            else:
                current_app.logger.error("TTS audio file was not created or is empty")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Failed to generate TTS audio: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False
