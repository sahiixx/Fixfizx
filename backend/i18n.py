"""
Internationalization (i18n) Support
Arabic and English language support for Dubai/UAE market
"""
from typing import Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Language(str, Enum):
    ENGLISH = "en"
    ARABIC = "ar"

class I18n:
    """Internationalization manager"""
    
    def __init__(self):
        self.translations = {
            "en": self._get_english_translations(),
            "ar": self._get_arabic_translations()
        }
        self.default_language = Language.ENGLISH
    
    def _get_english_translations(self) -> Dict[str, str]:
        """English translations"""
        return {
            # Common
            "welcome": "Welcome to NOWHERE.AI",
            "hello": "Hello",
            "goodbye": "Goodbye",
            "thank_you": "Thank you",
            "please": "Please",
            
            # App specific
            "digital_supremacy": "Digital Supremacy",
            "ai_powered_solutions": "AI-Powered Solutions",
            "transform_your_business": "Transform your business with AI-powered digital marketing solutions",
            "successful_projects": "Successful Projects",
            "satisfied_clients": "Satisfied Clients",
            "success_rate": "Success Rate",
            "support": "24/7 Support",
            
            # Services
            "ai_automation": "AI Automation",
            "digital_ecosystem": "Digital Ecosystem",
            "marketing_intelligence": "Marketing Intelligence",
            "web_development": "Web Development",
            "mobile_apps": "Mobile Apps",
            "social_media": "Social Media Marketing",
            
            # Forms
            "name": "Name",
            "email": "Email",
            "phone": "Phone",
            "message": "Message",
            "service": "Service",
            "submit": "Submit",
            "send": "Send",
            
            # Buttons
            "start_project": "Start Your Project",
            "view_portfolio": "View Portfolio",
            "contact_us": "Contact Us",
            "learn_more": "Learn More",
            "get_started": "Get Started",
            
            # Status messages
            "success": "Success",
            "error": "Error",
            "loading": "Loading...",
            "saving": "Saving...",
            "processing": "Processing...",
            
            # AI Solver
            "problem_description": "Describe your business challenge",
            "industry": "Industry",
            "budget_range": "Budget Range",
            "analyze": "Analyze",
            "ai_analysis": "AI Analysis",
            "market_insights": "Market Insights",
            "strategic_recommendations": "Strategic Recommendations",
            
            # Navigation
            "home": "Home",
            "platform": "Platform",
            "services": "Services",
            "ai_solver": "AI Solver",
            "agents": "Agents",
            "plugins": "Plugins",
            "templates": "Templates",
            "insights": "Insights",
            "about": "About",
            "contact": "Contact",
            
            # Footer
            "all_rights_reserved": "All rights reserved",
            "privacy_policy": "Privacy Policy",
            "terms_of_service": "Terms of Service",
            
            # Validation
            "required_field": "This field is required",
            "invalid_email": "Invalid email address",
            "invalid_phone": "Invalid phone number",
            "min_length": "Minimum length is {min} characters",
            "max_length": "Maximum length is {max} characters",
        }
    
    def _get_arabic_translations(self) -> Dict[str, str]:
        """Arabic translations for Dubai/UAE market"""
        return {
            # Common
            "welcome": "مرحباً بك في NOWHERE.AI",
            "hello": "مرحباً",
            "goodbye": "وداعاً",
            "thank_you": "شكراً لك",
            "please": "من فضلك",
            
            # App specific
            "digital_supremacy": "التفوق الرقمي",
            "ai_powered_solutions": "حلول مدعومة بالذكاء الاصطناعي",
            "transform_your_business": "حول عملك بحلول التسويق الرقمي المدعومة بالذكاء الاصطناعي",
            "successful_projects": "مشاريع ناجحة",
            "satisfied_clients": "عملاء راضون",
            "success_rate": "معدل النجاح",
            "support": "دعم على مدار الساعة",
            
            # Services
            "ai_automation": "أتمتة الذكاء الاصطناعي",
            "digital_ecosystem": "النظام البيئي الرقمي",
            "marketing_intelligence": "ذكاء التسويق",
            "web_development": "تطوير المواقع",
            "mobile_apps": "تطبيقات الهاتف المحمول",
            "social_media": "التسويق عبر وسائل التواصل الاجتماعي",
            
            # Forms
            "name": "الاسم",
            "email": "البريد الإلكتروني",
            "phone": "الهاتف",
            "message": "الرسالة",
            "service": "الخدمة",
            "submit": "إرسال",
            "send": "إرسال",
            
            # Buttons
            "start_project": "ابدأ مشروعك",
            "view_portfolio": "عرض الأعمال",
            "contact_us": "اتصل بنا",
            "learn_more": "اعرف المزيد",
            "get_started": "ابدأ الآن",
            
            # Status messages
            "success": "نجح",
            "error": "خطأ",
            "loading": "جاري التحميل...",
            "saving": "جاري الحفظ...",
            "processing": "جاري المعالجة...",
            
            # AI Solver
            "problem_description": "صف التحدي التجاري الخاص بك",
            "industry": "الصناعة",
            "budget_range": "نطاق الميزانية",
            "analyze": "تحليل",
            "ai_analysis": "تحليل الذكاء الاصطناعي",
            "market_insights": "رؤى السوق",
            "strategic_recommendations": "توصيات استراتيجية",
            
            # Navigation
            "home": "الرئيسية",
            "platform": "المنصة",
            "services": "الخدمات",
            "ai_solver": "محلل الذكاء الاصطناعي",
            "agents": "الوكلاء",
            "plugins": "الإضافات",
            "templates": "القوالب",
            "insights": "الرؤى",
            "about": "عن الشركة",
            "contact": "اتصل بنا",
            
            # Footer
            "all_rights_reserved": "جميع الحقوق محفوظة",
            "privacy_policy": "سياسة الخصوصية",
            "terms_of_service": "شروط الخدمة",
            
            # Validation
            "required_field": "هذا الحقل مطلوب",
            "invalid_email": "عنوان بريد إلكتروني غير صالح",
            "invalid_phone": "رقم هاتف غير صالح",
            "min_length": "الحد الأدنى للطول هو {min} أحرف",
            "max_length": "الحد الأقصى للطول هو {max} أحرف",
        }
    
    def translate(self, key: str, language: str = "en", **kwargs) -> str:
        """
        Get translation for a key
        
        Args:
            key: Translation key
            language: Language code (en, ar)
            **kwargs: Variables for string formatting
        
        Returns:
            Translated string
        """
        lang = language if language in self.translations else self.default_language
        
        translation = self.translations[lang].get(key, key)
        
        # Format with variables if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing translation variable: {e}")
        
        return translation
    
    def get_translations(self, language: str = "en") -> Dict[str, str]:
        """Get all translations for a language"""
        lang = language if language in self.translations else self.default_language
        return self.translations[lang]
    
    def is_rtl(self, language: str) -> bool:
        """Check if language is right-to-left"""
        return language == Language.ARABIC
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return [
            {"code": "en", "name": "English", "native_name": "English", "rtl": False},
            {"code": "ar", "name": "Arabic", "native_name": "العربية", "rtl": True}
        ]

# Global i18n instance
i18n = I18n()

def t(key: str, language: str = "en", **kwargs) -> str:
    """Shorthand for translate"""
    return i18n.translate(key, language, **kwargs)

def get_language_from_header(accept_language: Optional[str] = None) -> str:
    """
    Extract language from Accept-Language header
    
    Args:
        accept_language: Accept-Language header value
    
    Returns:
        Language code (en or ar)
    """
    if not accept_language:
        return "en"
    
    # Parse Accept-Language header
    languages = []
    for lang in accept_language.split(","):
        parts = lang.strip().split(";")
        lang_code = parts[0].strip()[:2].lower()
        
        # Extract quality value if present
        quality = 1.0
        if len(parts) > 1:
            try:
                quality = float(parts[1].split("=")[1])
            except:
                pass
        
        languages.append((lang_code, quality))
    
    # Sort by quality
    languages.sort(key=lambda x: x[1], reverse=True)
    
    # Return first supported language
    for lang_code, _ in languages:
        if lang_code in ["en", "ar"]:
            return lang_code
    
    return "en"
