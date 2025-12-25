"""
Internationalization API Routes
Provides translation data for frontend
"""
from fastapi import APIRouter, Header
from typing import Optional
from i18n import i18n, Language, get_language_from_header
from models import StandardResponse

router = APIRouter(prefix="/api/i18n", tags=["Internationalization"])

@router.get("/translations/{language}", response_model=StandardResponse)
async def get_translations(language: str):
    """
    Get all translations for a specific language
    
    Args:
        language: Language code (en or ar)
    
    Returns:
        All translations for the specified language
    """
    if language not in ["en", "ar"]:
        return StandardResponse(
            success=False,
            message=f"Unsupported language: {language}. Supported: en, ar",
            data=None
        )
    
    translations = i18n.get_translations(language)
    
    return StandardResponse(
        success=True,
        message=f"Translations retrieved for {language}",
        data={
            "language": language,
            "translations": translations,
            "rtl": i18n.is_rtl(language)
        }
    )

@router.get("/languages", response_model=StandardResponse)
async def get_supported_languages():
    """
    Get list of all supported languages
    
    Returns:
        List of supported languages with metadata
    """
    languages = i18n.get_supported_languages()
    
    return StandardResponse(
        success=True,
        message="Supported languages retrieved",
        data={"languages": languages}
    )

@router.get("/detect", response_model=StandardResponse)
async def detect_language(accept_language: Optional[str] = Header(None)):
    """
    Detect user's preferred language from Accept-Language header
    
    Args:
        accept_language: Accept-Language header from request
    
    Returns:
        Detected language code
    """
    detected = get_language_from_header(accept_language)
    
    return StandardResponse(
        success=True,
        message="Language detected",
        data={
            "detected_language": detected,
            "from_header": accept_language
        }
    )
