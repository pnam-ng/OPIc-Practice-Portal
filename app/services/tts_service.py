"""
TTS Service for OPIc Practice Portal
Uses edge-tts (Microsoft Edge Text-to-Speech) for free, high-quality neural voices.
"""
import os
import asyncio
import edge_tts
import nest_asyncio
from flask import current_app

# Apply nest_asyncio to allow nested event loops (required for running async edge-tts in Flask)
nest_asyncio.apply()

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
        self.default_voice = self.VOICE_MAPPING['ava']
    
    async def _generate_audio_async(self, text: str, output_path: str, voice: str) -> bool:
        """Async internal method to generate audio"""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            current_app.logger.error(f"Error in edge-tts generation: {e}")
            return False

    def generate_audio(self, text: str, output_path: str, voice_key: str = 'ava') -> bool:
        """
        Generate audio file from text using edge-tts.
        
        Args:
            text: Text to convert to speech
            output_path: Full path to save the audio file
            voice_key: Key from VOICE_MAPPING (default: 'ava')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get voice ID
            voice = self.VOICE_MAPPING.get(voice_key.lower(), self.default_voice)
            
            current_app.logger.info(f"Generating TTS audio using voice: {voice}")
            
            # Run async function in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running (e.g. in some servers), use a task
                # But for edge-tts which needs to complete, we might need a new loop or thread
                # nest_asyncio handles the re-entrant loop issue
                loop.run_until_complete(self._generate_audio_async(text, output_path, voice))
            else:
                loop.run_until_complete(self._generate_audio_async(text, output_path, voice))
                
            # Verify file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
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
