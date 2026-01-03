"""
Translation Service for Multilingual Support (Phase 1)
Supports Vietnamese <-> English translation
"""

from typing import Dict, Optional
from app.models.model import AIService
import os
import re


class TranslationService:
    """Service for translating text between Vietnamese and English"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.cache = {}  # Simple in-memory cache
    
    def detect_language(self, text: str) -> str:
        """
        Detect if text is Vietnamese or English
        Returns: 'vi' or 'en'
        """
        # Simple heuristic: check for Vietnamese characters
        vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        vietnamese_chars += vietnamese_chars.upper()
        
        # Count Vietnamese characters
        vn_count = sum(1 for char in text if char in vietnamese_chars)
        
        # If >10% Vietnamese characters, consider it Vietnamese
        if len(text) > 0 and (vn_count / len(text)) > 0.1:
            return 'vi'
        
        return 'en'
    
    def translate(self, text: str, target_lang: str = 'en') -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language ('en' or 'vi')
        
        Returns:
            Translated text
        """
        if not text or len(text.strip()) == 0:
            return text
        
        # Check cache
        cache_key = f"{text}_{target_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Detect source language
        source_lang = self.detect_language(text)
        
        # If already in target language, return as is
        if source_lang == target_lang:
            return text
        
        # Translate using AI
        if target_lang == 'en':
            prompt = f"Translate this Vietnamese text to English. Only return the translation, no explanation:\n\n{text}"
        else:  # target_lang == 'vi'
            prompt = f"Translate this English text to Vietnamese. Only return the translation, no explanation:\n\n{text}"
        
        try:
            translation = self.ai_service.generate_response(
                user_message=prompt,
                data_extend=""
            )
            
            # Clean up translation (remove quotes, extra spaces)
            translation = translation.strip().strip('"').strip("'")
            
            # Cache result
            self.cache[cache_key] = translation
            
            return translation
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original if translation fails
    
    def translate_dict(self, data: Dict, target_lang: str = 'en', 
                      fields: list = None) -> Dict:
        """
        Translate specific fields in a dictionary
        
        Args:
            data: Dictionary to translate
            target_lang: Target language
            fields: List of fields to translate (default: ['name', 'description', 'address'])
        
        Returns:
            Dictionary with translated fields
        """
        if fields is None:
            fields = ['name', 'description', 'address', 'summary']
        
        result = data.copy()
        
        for field in fields:
            if field in result and isinstance(result[field], str):
                result[f"{field}_{target_lang}"] = self.translate(
                    result[field], 
                    target_lang
                )
        
        return result
    
    def create_bilingual_response(self, data: Dict, 
                                 user_language: str = 'vi') -> Dict:
        """
        Create a bilingual response with both Vietnamese and English
        
        Args:
            data: Original data (assumed to be in Vietnamese)
            user_language: User's preferred language
        
        Returns:
            Dictionary with bilingual data and primary language set
        """
        # Translate to English
        translated_data = self.translate_dict(data, target_lang='en')
        
        # Structure bilingual response
        bilingual = {
            'primary_language': user_language,
            'vi': {},
            'en': {}
        }
        
        # Extract original (Vietnamese) fields
        for key, value in data.items():
            if isinstance(value, str):
                bilingual['vi'][key] = value
        
        # Extract translated (English) fields
        for key, value in translated_data.items():
            if key.endswith('_en'):
                original_key = key[:-3]  # Remove '_en' suffix
                bilingual['en'][original_key] = value
        
        return bilingual


# Singleton instance
_translation_service = None

def get_translation_service() -> TranslationService:
    """Get singleton translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
