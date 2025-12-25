#!/usr/bin/env python3
"""
Comprehensive I18n (Internationalization) Backend Testing
Tests the newly implemented multi-language endpoints for Arabic and English support
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Backend URL from frontend environment
BACKEND_URL = "https://backend-hardening.preview.emergentagent.com"

class I18nTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_english_translations(self):
        """Test GET /api/i18n/translations/en - Get English translations"""
        try:
            url = f"{BACKEND_URL}/api/i18n/translations/en"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if (data.get("success") and 
                        "data" in data and 
                        "translations" in data["data"] and
                        "rtl" in data["data"] and
                        data["data"]["language"] == "en"):
                        
                        translations = data["data"]["translations"]
                        rtl = data["data"]["rtl"]
                        
                        # Verify RTL is false for English
                        if rtl != False:
                            self.log_test("English Translations", False, f"RTL should be false for English, got: {rtl}")
                            return
                        
                        # Verify we have comprehensive translations (50+ keys)
                        if len(translations) < 50:
                            self.log_test("English Translations", False, f"Expected 50+ translation keys, got: {len(translations)}")
                            return
                        
                        # Verify key translations exist
                        required_keys = ["welcome", "digital_supremacy", "ai_powered_solutions", "home", "contact"]
                        missing_keys = [key for key in required_keys if key not in translations]
                        if missing_keys:
                            self.log_test("English Translations", False, f"Missing required keys: {missing_keys}")
                            return
                        
                        # Verify translations are in English (not Arabic)
                        if "مرحباً" in translations.get("welcome", ""):
                            self.log_test("English Translations", False, "English translations contain Arabic text")
                            return
                        
                        self.log_test("English Translations", True, f"Retrieved {len(translations)} English translations, RTL: {rtl}")
                    else:
                        self.log_test("English Translations", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("English Translations", False, f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("English Translations", False, f"Exception: {str(e)}")
    
    async def test_arabic_translations(self):
        """Test GET /api/i18n/translations/ar - Get Arabic translations"""
        try:
            url = f"{BACKEND_URL}/api/i18n/translations/ar"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if (data.get("success") and 
                        "data" in data and 
                        "translations" in data["data"] and
                        "rtl" in data["data"] and
                        data["data"]["language"] == "ar"):
                        
                        translations = data["data"]["translations"]
                        rtl = data["data"]["rtl"]
                        
                        # Verify RTL is true for Arabic
                        if rtl != True:
                            self.log_test("Arabic Translations", False, f"RTL should be true for Arabic, got: {rtl}")
                            return
                        
                        # Verify we have comprehensive translations (50+ keys)
                        if len(translations) < 50:
                            self.log_test("Arabic Translations", False, f"Expected 50+ translation keys, got: {len(translations)}")
                            return
                        
                        # Verify key translations exist
                        required_keys = ["welcome", "digital_supremacy", "ai_powered_solutions", "home", "contact"]
                        missing_keys = [key for key in required_keys if key not in translations]
                        if missing_keys:
                            self.log_test("Arabic Translations", False, f"Missing required keys: {missing_keys}")
                            return
                        
                        # Verify translations contain actual Arabic text
                        arabic_welcome = translations.get("welcome", "")
                        if "مرحباً" not in arabic_welcome:
                            self.log_test("Arabic Translations", False, f"Arabic welcome should contain 'مرحباً', got: {arabic_welcome}")
                            return
                        
                        # Verify digital supremacy translation
                        arabic_digital = translations.get("digital_supremacy", "")
                        if "التفوق الرقمي" not in arabic_digital:
                            self.log_test("Arabic Translations", False, f"Arabic digital_supremacy should contain 'التفوق الرقمي', got: {arabic_digital}")
                            return
                        
                        self.log_test("Arabic Translations", True, f"Retrieved {len(translations)} Arabic translations with proper Arabic text, RTL: {rtl}")
                    else:
                        self.log_test("Arabic Translations", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Arabic Translations", False, f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Arabic Translations", False, f"Exception: {str(e)}")
    
    async def test_supported_languages(self):
        """Test GET /api/i18n/languages - Get supported languages"""
        try:
            url = f"{BACKEND_URL}/api/i18n/languages"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if (data.get("success") and 
                        "data" in data and 
                        "languages" in data["data"]):
                        
                        languages = data["data"]["languages"]
                        
                        # Verify we have exactly 2 languages (English & Arabic)
                        if len(languages) != 2:
                            self.log_test("Supported Languages", False, f"Expected 2 languages, got: {len(languages)}")
                            return
                        
                        # Find English and Arabic languages
                        english_lang = None
                        arabic_lang = None
                        
                        for lang in languages:
                            if lang.get("code") == "en":
                                english_lang = lang
                            elif lang.get("code") == "ar":
                                arabic_lang = lang
                        
                        # Verify English language metadata
                        if not english_lang:
                            self.log_test("Supported Languages", False, "English language not found")
                            return
                        
                        if (english_lang.get("name") != "English" or 
                            english_lang.get("native_name") != "English" or 
                            english_lang.get("rtl") != False):
                            self.log_test("Supported Languages", False, f"Invalid English metadata: {english_lang}")
                            return
                        
                        # Verify Arabic language metadata
                        if not arabic_lang:
                            self.log_test("Supported Languages", False, "Arabic language not found")
                            return
                        
                        if (arabic_lang.get("name") != "Arabic" or 
                            arabic_lang.get("native_name") != "العربية" or 
                            arabic_lang.get("rtl") != True):
                            self.log_test("Supported Languages", False, f"Invalid Arabic metadata: {arabic_lang}")
                            return
                        
                        self.log_test("Supported Languages", True, f"Retrieved {len(languages)} languages with correct metadata")
                    else:
                        self.log_test("Supported Languages", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Supported Languages", False, f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Supported Languages", False, f"Exception: {str(e)}")
    
    async def test_language_detection_english(self):
        """Test GET /api/i18n/detect with English Accept-Language header"""
        try:
            url = f"{BACKEND_URL}/api/i18n/detect"
            headers = {
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if (data.get("success") and 
                        "data" in data and 
                        "detected_language" in data["data"] and
                        "from_header" in data["data"]):
                        
                        detected = data["data"]["detected_language"]
                        from_header = data["data"]["from_header"]
                        
                        # Verify English is detected
                        if detected != "en":
                            self.log_test("Language Detection (English)", False, f"Expected 'en', got: {detected}")
                            return
                        
                        # Verify header is captured
                        if from_header != "en-US,en;q=0.9":
                            self.log_test("Language Detection (English)", False, f"Header not captured correctly: {from_header}")
                            return
                        
                        self.log_test("Language Detection (English)", True, f"Detected '{detected}' from header '{from_header}'")
                    else:
                        self.log_test("Language Detection (English)", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Language Detection (English)", False, f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Language Detection (English)", False, f"Exception: {str(e)}")
    
    async def test_language_detection_arabic(self):
        """Test GET /api/i18n/detect with Arabic Accept-Language header"""
        try:
            url = f"{BACKEND_URL}/api/i18n/detect"
            headers = {
                'Accept-Language': 'ar-AE,ar;q=0.9',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if (data.get("success") and 
                        "data" in data and 
                        "detected_language" in data["data"] and
                        "from_header" in data["data"]):
                        
                        detected = data["data"]["detected_language"]
                        from_header = data["data"]["from_header"]
                        
                        # Verify Arabic is detected
                        if detected != "ar":
                            self.log_test("Language Detection (Arabic)", False, f"Expected 'ar', got: {detected}")
                            return
                        
                        # Verify header is captured
                        if from_header != "ar-AE,ar;q=0.9":
                            self.log_test("Language Detection (Arabic)", False, f"Header not captured correctly: {from_header}")
                            return
                        
                        self.log_test("Language Detection (Arabic)", True, f"Detected '{detected}' from header '{from_header}'")
                    else:
                        self.log_test("Language Detection (Arabic)", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Language Detection (Arabic)", False, f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Language Detection (Arabic)", False, f"Exception: {str(e)}")
    
    async def test_unsupported_language(self):
        """Test unsupported language handling"""
        try:
            url = f"{BACKEND_URL}/api/i18n/translations/fr"  # French not supported
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should return error for unsupported language
                    if data.get("success") == False and "Unsupported language" in data.get("message", ""):
                        self.log_test("Unsupported Language Handling", True, "Correctly rejected unsupported language 'fr'")
                    else:
                        self.log_test("Unsupported Language Handling", False, f"Should reject unsupported language: {data}")
                else:
                    self.log_test("Unsupported Language Handling", False, f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Unsupported Language Handling", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all i18n tests"""
        print("🌍 STARTING I18N (INTERNATIONALIZATION) BACKEND TESTING")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Test all 4 main endpoints
            await self.test_english_translations()
            await self.test_arabic_translations()
            await self.test_supported_languages()
            await self.test_language_detection_english()
            await self.test_language_detection_arabic()
            
            # Test edge cases
            await self.test_unsupported_language()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🌍 I18N TESTING SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL I18N TESTS PASSED - MULTI-LANGUAGE SUPPORT FULLY FUNCTIONAL!")
            print("✅ English translations working with RTL: false")
            print("✅ Arabic translations working with RTL: true and proper Arabic text")
            print("✅ Language detection working for both English and Arabic headers")
            print("✅ Supported languages endpoint returning correct metadata")
        else:
            print(f"\n⚠️ {self.total_tests - self.passed_tests} TESTS FAILED - ISSUES FOUND IN I18N IMPLEMENTATION")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if not result["success"]]
            if failed_tests:
                print("\nFAILED TESTS:")
                for test in failed_tests:
                    print(f"❌ {test['test']}: {test['details']}")
        
        return success_rate == 100

async def main():
    """Main test runner"""
    tester = I18nTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())