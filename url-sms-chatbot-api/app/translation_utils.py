# from googletrans import Translator

# translator = Translator()

# async def detect_language(text: str) -> str:
#     """
#     Asynchronously detect the language of the provided text.
#     Returns the ISO 639-1 language code (e.g., 'en' for English, 'ar' for Arabic).
#     """
#     # Await the detection coroutine
#     detection = await translator.detect(text)
#     return detection.lang

# async def translate_text(text: str, target_lang: str) -> str:
#     """
#     Asynchronously translate the given text to the target language.
#     """
#     translation = await translator.translate(text, dest=target_lang)
#     return translation.text
from deep_translator import GoogleTranslator
from langdetect import detect
import asyncio

async def detect_language(text: str) -> str:
    """
    Asynchronously detect the language of the provided text.
    Returns the ISO 639-1 language code (e.g., 'en' for English', 'ar' for Arabic).
    """
    loop = asyncio.get_event_loop()
    # Run the detection in a thread to simulate async behavior
    return await loop.run_in_executor(None, lambda: detect(text))

async def translate_text(text: str, target_lang: str) -> str:
    """
    Asynchronously translate the given text to the target language.
    """
    loop = asyncio.get_event_loop()
    # Run the translation in a thread to simulate async behavior
    return await loop.run_in_executor(None, lambda: GoogleTranslator(source='auto', target=target_lang).translate(text))
