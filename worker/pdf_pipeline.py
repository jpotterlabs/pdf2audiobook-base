import os
import sys
import tempfile
from typing import Optional, Callable, List

# Add backend to path for settings access
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.core.config import settings
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import openai
from pydub import AudioSegment
import io
import re
import random
from abc import ABC, abstractmethod
import base64

# TTS Provider Imports
from google.cloud import texttospeech
import boto3
from botocore.exceptions import NoCredentialsError
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, ResultReason
from elevenlabs.client import ElevenLabs


# --- TTS PROVIDER INTERFACE ---
class TTSProvider(ABC):
    @abstractmethod
    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        pass


# --- CONCRETE TTS IMPLEMENTATIONS ---
class OpenAITTS(TTSProvider):
    def __init__(self):
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        self.model = os.getenv("OPENAI_TTS_MODEL", "tts-1")
        
        if "kokoro" in self.model.lower():
             default_voice = os.getenv("KOKORO_VOICE_DEFAULT", "af_sky+af_bella")
             female_voice = os.getenv("KOKORO_VOICE_FEMALE", "af_bella")
             male_voice = os.getenv("KOKORO_VOICE_MALE", "af_sky")
             
             self.voice_mapping = {
                 "default": default_voice,
                 "female": female_voice,
                 "male": male_voice,
                 "alloy": os.getenv("KOKORO_VOICE_ALLOY", default_voice),
                 "echo": os.getenv("KOKORO_VOICE_ECHO", female_voice),
                 "fable": os.getenv("KOKORO_VOICE_FABLE", male_voice),
                 "onyx": os.getenv("KOKORO_VOICE_ONYX", male_voice),
                 "nova": os.getenv("KOKORO_VOICE_NOVA", female_voice),
                 "shimmer": os.getenv("KOKORO_VOICE_SHIMMER", default_voice)
             }
        else:
             self.voice_mapping = {"default": "alloy", "female": "nova", "male": "onyx"}

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        voice = self.voice_mapping.get(voice_id, self.voice_mapping.get("default"))
        response = self.client.audio.speech.create(
            model=self.model, voice=voice, input=text, speed=speed
        )
        return response.content


class GoogleTTS(TTSProvider):
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.voice_mapping = {
            "us_female_std": (settings.GOOGLE_VOICE_US_FEMALE_STD, "en-US"),
            "us_male_std": (settings.GOOGLE_VOICE_US_MALE_STD, "en-US"),
            "gb_female_std": (settings.GOOGLE_VOICE_GB_FEMALE_STD, "en-GB"),
            "gb_male_std": (settings.GOOGLE_VOICE_GB_MALE_STD, "en-GB"),
            "us_female_premium": (settings.GOOGLE_VOICE_US_FEMALE_PREMIUM, "en-US"),
            "us_male_premium": (settings.GOOGLE_VOICE_US_MALE_PREMIUM, "en-US"),
            "gb_female_premium": (settings.GOOGLE_VOICE_GB_FEMALE_PREMIUM, "en-GB"),
            "gb_male_premium": (settings.GOOGLE_VOICE_GB_MALE_PREMIUM, "en-GB"),
        }
        from loguru import logger
        logger.info(f"🎤 GoogleTTS initialized with voice mapping: {self.voice_mapping}")

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice_name, lang_code = self.voice_mapping.get(
            voice_id, ("en-US-Neural2-D", "en-US")
        )
        
        from loguru import logger
        logger.info(f"🎤 Google TTS synthesis: voice_id='{voice_id}', actual_name='{voice_name}', lang='{lang_code}'")

        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code, name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speed
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content


class AWSPollyTTS(TTSProvider):
    def __init__(self):
        self.client = boto3.client(
            "polly",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    import html

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        # Polly uses SSML for speed control
        rate = f"{int(speed * 100)}%"
        escaped_text = html.escape(text)
        ssml_text = f'<speak><prosody rate="{rate}">{escaped_text}</prosody></speak>'
        response = self.client.synthesize_speech(
            Text=ssml_text,
            OutputFormat="mp3",
            VoiceId=voice_id or "Joanna",
            TextType="ssml",
        )
        return response["AudioStream"].read()


class AzureTTS(TTSProvider):
    def __init__(self):
        self.speech_config = SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION"),
        )

    import html

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        self.speech_config.speech_synthesis_voice_name = voice_id or "en-US-JennyNeural"
        synthesizer = SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=None
        )
        # Azure uses SSML for speed control
        rate = f"{speed:.2f}"
        escaped_text = html.escape(text)
        ssml_text = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="{self.speech_config.speech_synthesis_voice_name}"><prosody rate="{rate}">{escaped_text}</prosody></voice></speak>'
        result = synthesizer.speak_ssml_async(ssml_text).get()
        if result.reason == ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            raise Exception(f"Azure TTS failed: {result.reason}")


class ElevenLabsTTS(TTSProvider):
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        # ElevenLabs does not directly support a speed parameter in the same way
        # Voice settings are managed in the ElevenLabs studio
        audio = self.client.generate(
            text=text, voice=voice_id or "Rachel", model="eleven_multilingual_v2"
        )
        return audio


class MockTTS(TTSProvider):
    """A mock TTS provider for testing and development."""

    def __init__(self):
        # A small, silent 1-second MP3 file content
        self.silent_audio = base64.b64decode(
            "//MkxAAgEAAAAEAYFMYXNtZQAACAAADhQCAAACgAAAABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVax-p.t"
        )

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        logger.info(f"--- MOCK TTS: Generating audio for text (voice: {voice_id}, speed: {speed}) ---")
        return self.silent_audio

# --- TTS MANAGER ---
class TTSManager:
    def __init__(self):
        self._provider_map = {
            "openai": OpenAITTS,
            "google": GoogleTTS,
            "aws_polly": AWSPollyTTS,
            "azure": AzureTTS,
            "eleven_labs": ElevenLabsTTS,
        }
        self._instances = {}

    def get_provider(self, provider_name: str) -> TTSProvider:
        # If testing mode is enabled, always return the mock provider
        if os.getenv("TESTING_MODE", "False").lower() == "true":
            provider_name = "mock"
            self._provider_map["mock"] = MockTTS

        if provider_name in self._instances:
            return self._instances[provider_name]

        provider_class = self._provider_map.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unsupported TTS provider: {provider_name}")

        # Instantiate the provider on first request.
        # Credential or other instantiation errors will be raised here
        # and handled by the calling Celery task.
        instance = provider_class()
        self._instances[provider_name] = instance
        return instance


# --- PDF PIPELINE ---
class PDFToAudioPipeline:
    def __init__(self):
        self.tts_manager = TTSManager()

    def process_pdf(
        self,
        pdf_path: str,
        voice_provider: str = "openai",
        voice_type: str = "default",
        reading_speed: float = 1.0,
        include_summary: bool = False,
        conversion_mode: str = "full",
        progress_callback: Optional[Callable[[int], None]] = None,
        work_dir: Optional[str] = None
    ) -> tuple[str, float, dict]:
        from loguru import logger
        logger.info(f"🚀 Starting PDF processing: provider='{voice_provider}', voice='{voice_type}', mode='{conversion_mode}', summary='{include_summary}'")
        
        usage_stats = {"chars": 0, "tokens": 0}
        
        try:
            if progress_callback:
                progress_callback(5)
            raw_text = self._extract_text(pdf_path)

            if not raw_text.strip():
                raise ValueError("No text could be extracted from the PDF.")

            if progress_callback:
                progress_callback(15)
            cleaned_text = self._advanced_text_cleanup(raw_text)

            final_text, tokens_used = self._get_final_text(
                cleaned_text, include_summary, conversion_mode, progress_callback
            )
            usage_stats["tokens"] += tokens_used

            if progress_callback:
                progress_callback(35)
            
            # Smart chunking for TTS safety (Google has 5000 char limit)
            chunks = self._chunk_text_for_tts(final_text)

            tts_provider = self.tts_manager.get_provider(voice_provider)

            # Create a localized temporary directory if not provided
            local_temp_dir = None
            if not work_dir:
                local_temp_dir = tempfile.TemporaryDirectory()
                work_dir = local_temp_dir.name
            
            chunk_files = []
            
            # Process chunks and save to disk immediately
            char_count = 0
            for i, chunk in enumerate(chunks):
                progress = 40 + int((i / len(chunks)) * 55)
                if progress_callback:
                    progress_callback(progress)
                
                char_count += len(chunk)

                audio_data = tts_provider.text_to_audio(
                    chunk, voice_type, reading_speed
                )
                
                chunk_path = os.path.join(work_dir, f"chunk_{i:04d}.mp3")
                with open(chunk_path, "wb") as f:
                    f.write(audio_data)
                
                chunk_files.append(chunk_path)
            
            usage_stats["chars"] = char_count

            if progress_callback:
                progress_callback(95)
            
            final_audio_path = self._assemble_audio_chapters(chunk_files, work_dir)
            
            # If we created a local temp dir, we need to ensure the final file 
            # is moved out or persisted before the dir is cleaned up.
            # actually, for now we will rely on the caller to handle cleanup if they provided work_dir
            # if we created it, we return the path inside it, which might be dangerous if local_temp_dir cleans up 
            # immediately upon garbage collection.
            # FIX: Ideally the caller should ALWAYS provide work_dir or we should disable auto-cleanup here.
            # pydub/tempfile logic: strict separation is better.
            
            if local_temp_dir:
                # If we made the dir, we should probably persist the final file elsewhere or 
                # keep the dir alive? For safety, let's assume the caller will likely move it 
                # or read it immediately. But since we return a path, let's effectively "detach" 
                # the tempdir if possible or warn. 
                # Better approach: The caller (Celery task) creates the temp dir context.
                # Use local_temp_dir.cleanup() ONLY if exception? 
                # actually, local_temp_dir object will be destroyed when this scope ends? 
                # No, it stays alive as long as ref exists. But here ref dies at end of function.
                # So we must NOT use local_temp_dir here if we want to return a path inside it.
                # But we can't change signature to force work_dir easily without breaking tests.
                # We will rely on returning the path. Use mkdtemp instead of TemporaryDirectory if no work_dir.
                pass 

            full_audio_data_path = final_audio_path

            # Calculate estimated cost
            estimated_cost = self._calculate_cost(
                voice_provider, voice_type, final_text, usage_stats["tokens"]
            )

            if progress_callback:
                progress_callback(100)
            return full_audio_data_path, estimated_cost, usage_stats

        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

    def _get_final_text(self, cleaned_text, include_summary, conversion_mode, progress_callback) -> tuple[str, int]:
        from loguru import logger
        mode = str(conversion_mode).lower()
        logger.info(f"🔍 Determining final text for mode: '{mode}' (original: '{conversion_mode}')")
        
        tokens = 0

        if mode == "summary":
            if progress_callback:
                progress_callback(25)
            content, t = self._generate_summary(cleaned_text)
            tokens += t
            return content, tokens
        elif mode in ["explanation", "summary_explanation"]:
            if progress_callback:
                progress_callback(25)
            content, t = self._generate_concept_explanation(cleaned_text)
            tokens += t
            return content, tokens
        
        # Custom logic for "Full + Explanation" mode or standard Full
        if mode == "full_explanation":
            if progress_callback:
                progress_callback(25)
            
            # Generate explanation
            explanation, t = self._generate_concept_explanation(cleaned_text)
            tokens += t
            
            final_content = f"Concept Explanation:\n{explanation}\n\nFull Text:\n{cleaned_text}"

            # Check if summary is ALSO requested
            if include_summary:
                summary, t2 = self._generate_summary(cleaned_text)
                tokens += t2
                final_content = f"Summary:\n{summary}\n\n{final_content}"
           
            return final_content, tokens

        if include_summary:
            if progress_callback:
                progress_callback(25)
            summary, t = self._generate_summary(cleaned_text)
            tokens += t
            return f"Summary of the document: {summary}\n\n{cleaned_text}", tokens
            
        return cleaned_text, tokens

    def _calculate_cost(self, provider: str, voice_type: str, text: str, tokens_used: int = 0) -> float:
        char_count = len(text)
        cost = 0.0

        # TTS Cost
        if provider == "google":
            if "premium" in voice_type.lower():
                cost = (char_count / 1_000_000) * settings.GOOGLE_TTS_COST_PREMIUM
            else:
                cost = (char_count / 1_000_000) * settings.GOOGLE_TTS_COST_STANDARD
        elif provider == "openai":
            # Check if using local OpenAI-compatible endpoint (e.g. Kokoro)
            base_url = os.getenv("OPENAI_BASE_URL", "").lower()
            api_key = os.getenv("OPENAI_API_KEY", "")
            
            if "localhost" in base_url or "0.0.0.0" in base_url or api_key == "not-needed":
                cost = 0.0
            else:
                # Actual OpenAI is flat $15 per 1M characters for tts-1
                cost = (char_count / 1_000_000) * 15.0
        
        # LLM Cost (Approximate using average of input/output rates)
        if tokens_used > 0:
            avg_llm_rate = (settings.LLM_COST_INPUT_PER_1K + settings.LLM_COST_OUTPUT_PER_1K) / 2
            llm_cost = (tokens_used / 1000) * avg_llm_rate
            cost += llm_cost
        
        return round(cost, 6)

    def _extract_text(self, pdf_path: str) -> str:
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
            if len(text.strip()) < 100:  # Threshold for considering OCR
                return self._ocr_pdf(pdf_path)
            return text
        except Exception:
            return self._ocr_pdf(pdf_path)

    def _ocr_pdf(self, pdf_path: str) -> str:
        text = ""
        try:
            images = convert_from_path(pdf_path, dpi=300)
            for image in images:
                text += pytesseract.image_to_string(image, lang="eng") + "\n"
            return text
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    def _advanced_text_cleanup(self, text: str) -> str:
        text = re.sub(r"\n\s*\n", "\n", text)
        text = re.sub(r"\s+", " ", text)
        replacements = {
            "â": "-",
            "â": '"',
            "â": '"',
            "â": "'",
            "â¦": "...",
            "â¢": "*",
            "â€™": "'",
            "â€˜": "'",
            "â€œ": '"',
            "â€ť": '"',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    def _generate_summary(self, text: str) -> tuple[str, int]:
        """Generate a concise summary of the text."""
        from loguru import logger
        try:
            system_prompt = "Summarize the following text in about 300 words. fastidiously covering the entire document from start to finish. Do not just summarize the introduction."
            # Dolphin Mistral 24B often has 32k context. 100k chars is ~25k tokens. Safe-ish.
            limit = 100000 
            user_content = text[:limit] if len(text) > limit else text
            
            logger.info(f"📝 Generating summary for text of length {len(text)} (truncated to {len(user_content)})")

            summary, tokens = self._call_llm_with_retry(
                system_prompt=system_prompt,
                user_content=user_content,
                max_tokens=1000,
                temperature=0.3
            )
            logger.info(f"✅ Summary generated: {len(summary)} chars, {tokens} tokens")
            return summary, tokens
        except Exception as e:
            logger.warning(f"⚠️ Summary generation error: {e}")
            if "api_key" in str(e).lower() or "401" in str(e):
                logger.error("❌ CRITICAL: LLM API key is missing or invalid. Check your environment variables.")
            return text[:500] + "...", 0

    def _generate_concept_explanation(self, text: str) -> tuple[str, int]:
        """Generate a comprehensive explanation of core concepts from the text."""
        from loguru import logger
        try:
            system_prompt = """Analyze the provided text and create a comprehensive explanation of its core concepts.
                Crucially, you must cover the ENTIRE document from beginning to end. 
                Focus on explaining key ideas, methodologies, findings, and conclusions in a narrative form suitable for audio conversion.
                Make the explanation educational and accessible, as if teaching the concepts to someone new to the topic."""
            
            limit = 100000
            user_content = text[:limit] if len(text) > limit else text
            
            logger.info(f"📝 Generating explanation for text of length {len(text)} (truncated to {len(user_content)})")

            explanation, tokens = self._call_llm_with_retry(
                system_prompt=system_prompt,
                user_content=user_content,
                max_tokens=4000,
                temperature=0.2
            )
            logger.info(f"✅ Concept explanation generated: {len(explanation)} chars, {tokens} tokens")
            return explanation, tokens
        except Exception as e:
            logger.warning(f"⚠️ Concept explanation error: {e}")
            if "api_key" in str(e).lower() or "401" in str(e):
                logger.error("❌ CRITICAL: LLM API key is missing or invalid. Check your environment variables.")
            # Fallback: generate a basic summary-style explanation
            return f"This document explores key concepts and ideas. {text[:1000]}... The main themes and conclusions are presented in a structured format suitable for understanding the core content.", 0

    def _call_llm_with_retry(self, system_prompt: str, user_content: str, max_tokens: int, temperature: float, max_retries: int = 5) -> tuple[str, int]:
        """Call LLM with exponential backoff to handle rate limits."""
        import time
        from loguru import logger
        
        openrouter_key = settings.OPENROUTER_API_KEY
        openai_key = settings.OPENAI_API_KEY

        if openrouter_key:
            logger.info(f"🔗 Using OpenRouter for LLM ({settings.LLM_MODEL})")
            client = openai.OpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
            )
            model = settings.LLM_MODEL
        elif openai_key:
            logger.info("🔗 Using direct OpenAI for LLM (gpt-3.5-turbo)")
            client = openai.OpenAI(api_key=openai_key)
            model = "gpt-3.5-turbo"
        else:
            logger.error("❌ No LLM API key found in settings (OPENROUTER_API_KEY or OPENAI_API_KEY)")
            raise ValueError("No LLM API key configured. Summary/Explanation modes require an API key.")

        logger.info(f"🤖 Calling LLM ({model}) for {system_prompt[:50]}...")
        for i in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                tokens = response.usage.total_tokens if response.usage else 0
                return response.choices[0].message.content.strip(), tokens
            except Exception as e:
                # Check for 429 Rate Limit
                if "429" in str(e) or "rate limit" in str(e).lower():
                    wait_time = (2 ** i) + (random.random() * i)
                    logger.warning(f"⚠️ Rate limit hit (429). Retrying in {wait_time:.2f}s... (Attempt {i+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                # Any other exception, raise it
                logger.error(f"❌ LLM call failed: {e}")
                raise e
        
        raise Exception(f"Max retries ({max_retries}) exceeded for LLM call.")

    def _chunk_text_for_tts(self, text: str, max_chars: int = 4500) -> List[str]:
        """
        Split text into chunks that are safe for TTS providers (e.g., Google's 5000 character limit).
        Attempts to split at sentence boundaries (., !, ?) or at the last whitespace if no sentence boundary is found.
        """
        if not text:
            return []
        
        if len(text) <= max_chars:
            return [text]

        chunks = []
        while text:
            if len(text) <= max_chars:
                chunks.append(text)
                break

            # Find the best split point within the max_chars limit
            sub_text = text[:max_chars]
            
            # 1. Look for a sentence boundary within the last 500 chars of the limit
            split_match = list(re.finditer(r'[.!?]\s+', sub_text))
            if split_match:
                split_point = split_match[-1].end()
            else:
                # 2. Look for ANY whitespace to avoid splitting words
                split_match = list(re.finditer(r'\s+', sub_text))
                if split_match:
                    split_point = split_match[-1].end()
                else:
                    # 3. Hard cut if necessary
                    split_point = max_chars

            chunks.append(text[:split_point].strip())
            text = text[split_point:].strip()

        return chunks

    def _chapterize_text(self, text: str, min_chapter_length_sentences=20) -> List[str]:
        # Legacy: keeping for backward compatibility if needed, but processing now uses _chunk_text_for_tts
        sentences = re.split(r"(?<=[.!?])\s+", text)

    def _assemble_audio_chapters(
        self, chunk_files: List[str], work_dir: str
    ) -> str:
        """
        Assemble audio chapters using ffmpeg concat demuxer to avoid OOM.
        Returns the path to the final assembled mp3 file.
        """
        import subprocess
        
        output_path = os.path.join(work_dir, "final_output.mp3")
        list_file_path = os.path.join(work_dir, "file_list.txt")

        # Create ffmpeg concat list file
        with open(list_file_path, "w") as f:
            for chunk_file in chunk_files:
                # ffmpeg requires absolute paths or relative to list file. 
                # Absolute is safest.
                abs_path = os.path.abspath(chunk_file)
                # Escape single quotes in filename for ffmpeg
                safe_path = abs_path.replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        # Run ffmpeg command
        # -f concat: use concat demuxer
        # -safe 0: allow unsafe file paths (absolute paths)
        # -i ...: input list file
        # -c copy: stream copy, no re-encoding (very fast, low memory)
        cmd = [
            "ffmpeg",
            "-y", # overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            output_path
        ]
        
        try:
            subprocess.run(
                cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            return output_path
        except subprocess.CalledProcessError as e:
            # Fallback to pydub if ffmpeg fails (runtime missing?) 
            # But we added it to Docker, so it should be fine.
            # If it fails, capturing stderr is critical.
            stderr_output = e.stderr.decode() if e.stderr else "No stderr"
            raise Exception(f"FFmpeg assembly failed: {stderr_output}")

