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
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.voice_mapping = {"default": "alloy", "female": "nova", "male": "onyx"}

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        voice = self.voice_mapping.get(voice_id, "alloy")
        response = self.client.audio.speech.create(
            model="tts-1", voice=voice, input=text, speed=speed
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

    def text_to_audio(self, text: str, voice_id: str, speed: float) -> bytes:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice_name, lang_code = self.voice_mapping.get(
            voice_id, ("en-US-Neural2-D", "en-US")
        )
        
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
        print(f"--- MOCK TTS: Generating audio for text (voice: {voice_id}, speed: {speed}) ---")
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
    ) -> tuple[bytes, float]:
        try:
            if progress_callback:
                progress_callback(5)
            raw_text = self._extract_text(pdf_path)

            if not raw_text.strip():
                raise ValueError("No text could be extracted from the PDF.")

            if progress_callback:
                progress_callback(15)
            cleaned_text = self._advanced_text_cleanup(raw_text)

            final_text = self._get_final_text(
                cleaned_text, include_summary, conversion_mode, progress_callback
            )

            if progress_callback:
                progress_callback(35)
            
            # Smart chunking for TTS safety (Google has 5000 char limit)
            chunks = self._chunk_text_for_tts(final_text)

            tts_provider = self.tts_manager.get_provider(voice_provider)

            chapter_audio_segments = []
            for i, chunk in enumerate(chunks):
                progress = 40 + int((i / len(chunks)) * 55)
                if progress_callback:
                    progress_callback(progress)

                audio_data = tts_provider.text_to_audio(
                    chunk, voice_type, reading_speed
                )
                chapter_audio_segments.append(
                    AudioSegment.from_file(io.BytesIO(audio_data))
                )

            if progress_callback:
                progress_callback(95)
            full_audio_data = self._assemble_audio_chapters(chapter_audio_segments)

            # Calculate estimated cost
            estimated_cost = self._calculate_cost(
                voice_provider, voice_type, final_text
            )

            if progress_callback:
                progress_callback(100)
            return full_audio_data, estimated_cost

        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

    def _get_final_text(self, cleaned_text, include_summary, conversion_mode, progress_callback):
        if conversion_mode == "summary":
            if progress_callback:
                progress_callback(25)
            return self._generate_summary(cleaned_text)
        elif conversion_mode == "explanation":
            if progress_callback:
                progress_callback(25)
            return self._generate_concept_explanation(cleaned_text)
        elif conversion_mode == "summary_explanation":
             # Legacy fallback
            if progress_callback:
                progress_callback(25)
            return self._generate_concept_explanation(cleaned_text)
        
        # Mode is FULL or anything else
        if include_summary:
            if progress_callback:
                progress_callback(25)
            summary = self._generate_summary(cleaned_text)
            return f"Summary of the document: {summary}\n\n{cleaned_text}"
        return cleaned_text

    def _calculate_cost(self, provider: str, voice_type: str, text: str) -> float:
        char_count = len(text)
        cost = 0.0

        if provider == "google":
            if "premium" in voice_type.lower():
                cost = (char_count / 1_000_000) * settings.GOOGLE_TTS_COST_CHIRP
            else:
                cost = (char_count / 1_000_000) * settings.GOOGLE_TTS_COST_WAVENET
        elif provider == "openai":
            # OpenAI is flat $15 per 1M characters for tts-1
            cost = (char_count / 1_000_000) * 15.0
        
        # Add a placeholder for LLM cost (Summary/Explanation)
        # Assuming Flash 2.0 is extremely cheap, we'll just add a tiny flat fee or ignore it for now
        # until token counting is implemented.
        
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

    def _generate_summary(self, text: str) -> str:
        try:
            # Use OpenRouter if available, otherwise fallback to OpenAI
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                client = openai.OpenAI(
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1",
                )
                model = settings.LLM_MODEL
            else:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                model = "gpt-3.5-turbo"

            max_length = 12000
            truncated_text = text[:max_length] if len(text) > max_length else text

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following text in about 150 words.",
                    },
                    {"role": "user", "content": truncated_text},
                ],
                max_tokens=500, # Increased for safer summaries
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            from loguru import logger
            logger.warning(f"Summary generation error: {e}")
            return text[:500] + "..."

    def _generate_concept_explanation(self, text: str) -> str:
        """Generate a comprehensive explanation of core concepts from the text."""
        try:
            # Use OpenRouter if available, otherwise fallback to OpenAI
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                client = openai.OpenAI(
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1",
                )
                model = settings.LLM_MODEL
            else:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                model = "gpt-4"

            max_length = 10000  # Larger context for concept extraction
            truncated_text = text[:max_length] if len(text) > max_length else text

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the provided text and create a comprehensive explanation of its core concepts.
                        Focus on explaining key ideas, methodologies, findings, and conclusions in a narrative form suitable for audio conversion.
                        Make the explanation educational and accessible, as if teaching the concepts to someone new to the topic.""",
                    },
                    {"role": "user", "content": truncated_text},
                ],
                max_tokens=3000,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            from loguru import logger
            logger.warning(f"Concept explanation error: {e}")
            # Fallback: generate a basic summary-style explanation
            return f"This document explores key concepts and ideas. {text[:1000]}... The main themes and conclusions are presented in a structured format suitable for understanding the core content."

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
        self, chapter_audio_segments: List[AudioSegment]
    ) -> bytes:
        full_audio = sum(chapter_audio_segments, AudioSegment.empty())

        audio_buffer = io.BytesIO()
        full_audio.export(audio_buffer, format="mp3")
        return audio_buffer.getvalue()
