#!/usr/bin/env python3
"""
Advanced AI Systems Re-Testing Suite
Focus on previously failed endpoints after model configuration fixes
"""

import asyncio
import aiohttp
import json
import sys
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend .env file
def get_backend_url():
    """Get backend URL from frontend .env file"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

class AdvancedAITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
        if success:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
    
    # ================================================================================================
    # PRIORITY RE-TESTS - PREVIOUSLY FAILED ENDPOINTS
    # ================================================================================================
    
    async def test_advanced_ai_reasoning(self):
        """Test POST /api/ai/advanced/reasoning - o1-mini temperature fix"""
        try:
            # Dubai business scenario for reasoning
            reasoning_data = {
                "prompt": "I'm launching a fintech startup in Dubai's DIFC. Analyze the regulatory landscape, competition from traditional banks vs neobanks, and recommend a go-to-market strategy for acquiring 10,000 customers in the first year. Consider UAE Central Bank regulations, cultural preferences, and digital adoption rates.",
                "task_type": "business_strategy",
                "context": {
                    "industry": "fintech",
                    "location": "Dubai, UAE",
                    "target": "10K customers",
                    "timeline": "1 year"
                }
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/reasoning",
                json=reasoning_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result_data = data.get("data", {})
                        if "analysis" in result_data or "reasoning" in result_data or "response" in result_data:
                            # Check for substantial content
                            content = str(result_data)
                            if len(content) > 100:
                                self.log_test("Advanced AI Reasoning (o1-mini)", True, "Reasoning analysis completed with temperature fix")
                                return True
                            else:
                                self.log_test("Advanced AI Reasoning (o1-mini)", False, "Response too short", data)
                                return False
                        else:
                            self.log_test("Advanced AI Reasoning (o1-mini)", False, "No analysis content in response", data)
                            return False
                    else:
                        self.log_test("Advanced AI Reasoning (o1-mini)", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Reasoning (o1-mini)", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Reasoning (o1-mini)", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_code_generation(self):
        """Test POST /api/ai/advanced/code-generation - Claude model name fix"""
        try:
            # Code generation request
            code_data = {
                "task_description": "Create a Python FastAPI endpoint for processing UAE VAT calculations. Include validation for UAE VAT number format, calculate 5% VAT on amounts, handle exemptions for healthcare and education sectors, and return detailed breakdown with Arabic and English descriptions.",
                "language": "python",
                "framework": "fastapi",
                "requirements": [
                    "UAE VAT number validation",
                    "5% VAT calculation",
                    "Sector-based exemptions",
                    "Multilingual support (Arabic/English)",
                    "Pydantic models for validation"
                ]
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/code-generation",
                json=code_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result_data = data.get("data", {})
                        if "code" in result_data or "generated_code" in result_data or "response" in result_data:
                            # Check for substantial code content
                            content = str(result_data)
                            if len(content) > 200 and ("def " in content or "class " in content or "from fastapi" in content):
                                self.log_test("Advanced AI Code Generation (Claude)", True, "Code generation completed with stable Claude model")
                                return True
                            else:
                                self.log_test("Advanced AI Code Generation (Claude)", False, "Generated code too short or invalid", data)
                                return False
                        else:
                            self.log_test("Advanced AI Code Generation (Claude)", False, "No code content in response", data)
                            return False
                    else:
                        self.log_test("Advanced AI Code Generation (Claude)", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Code Generation (Claude)", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Code Generation (Claude)", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_multimodal(self):
        """Test POST /api/ai/advanced/multimodal - Gemini model name fix"""
        try:
            # Create a simple test image (1x1 red pixel in base64)
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            # Multimodal analysis request
            multimodal_data = {
                "text": "Analyze this image in the context of Dubai's digital transformation initiatives. How could this visual element be used in a smart city application?",
                "images": [test_image_base64],
                "task": "comprehensive_analysis"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/multimodal",
                json=multimodal_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result_data = data.get("data", {})
                        if "analysis" in result_data or "response" in result_data or "multimodal_analysis" in result_data:
                            # Check for substantial analysis content
                            content = str(result_data)
                            if len(content) > 100:
                                self.log_test("Advanced AI Multimodal (Gemini)", True, "Multimodal analysis completed with correct Gemini model")
                                return True
                            else:
                                self.log_test("Advanced AI Multimodal (Gemini)", False, "Analysis too short", data)
                                return False
                        else:
                            self.log_test("Advanced AI Multimodal (Gemini)", False, "No analysis content in response", data)
                            return False
                    else:
                        self.log_test("Advanced AI Multimodal (Gemini)", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Multimodal (Gemini)", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Multimodal (Gemini)", False, f"Exception: {str(e)}")
            return False
    
    # ================================================================================================
    # REGRESSION TESTS - ENSURE NO REGRESSIONS IN WORKING ENDPOINTS
    # ================================================================================================
    
    async def test_advanced_ai_models(self):
        """Test GET /api/ai/advanced/models - Should show updated model names"""
        try:
            async with self.session.get(f"{API_BASE}/ai/advanced/models") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "models" in data.get("data", {}):
                        models_data = data["data"]
                        
                        # Check for updated model names
                        expected_models = [
                            "claude-3-5-sonnet-20241022",
                            "gemini-2.0-flash",
                            "o1-mini"
                        ]
                        
                        latest_updates = models_data.get("latest_updates", {})
                        found_models = []
                        
                        for model in expected_models:
                            if model in str(latest_updates) or model in str(models_data):
                                found_models.append(model)
                        
                        if len(found_models) >= 2:  # At least 2 of the updated models should be present
                            self.log_test("Advanced AI Models", True, f"Updated model names found: {found_models}")
                            return True
                        else:
                            self.log_test("Advanced AI Models", False, f"Updated models not found. Found: {found_models}", data)
                            return False
                    else:
                        self.log_test("Advanced AI Models", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Models", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Models", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_vision(self):
        """Test POST /api/ai/advanced/vision - Should still work with GPT-4o"""
        try:
            # Create a simple test image (1x1 red pixel in base64)
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            vision_data = {
                "image_data": test_image_base64,
                "prompt": "Describe this image and suggest how it could be used in a Dubai business context.",
                "detail_level": "high"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/vision",
                json=vision_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result_data = data.get("data", {})
                        if "analysis" in result_data or "description" in result_data or "response" in result_data:
                            content = str(result_data)
                            if len(content) > 50:
                                self.log_test("Advanced AI Vision (GPT-4o)", True, "Vision analysis working correctly")
                                return True
                            else:
                                self.log_test("Advanced AI Vision (GPT-4o)", False, "Vision response too short", data)
                                return False
                        else:
                            self.log_test("Advanced AI Vision (GPT-4o)", False, "No vision analysis in response", data)
                            return False
                    else:
                        self.log_test("Advanced AI Vision (GPT-4o)", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Vision (GPT-4o)", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Vision (GPT-4o)", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_dubai_market_analysis(self):
        """Test POST /api/ai/advanced/dubai-market-analysis - Should still work"""
        try:
            market_data = {
                "industry": "technology",
                "analysis_type": "comprehensive",
                "specific_questions": [
                    "What are the key growth opportunities for tech startups in Dubai?",
                    "How does the regulatory environment support innovation?",
                    "What are the main challenges for international companies entering the UAE market?"
                ]
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/dubai-market-analysis",
                json=market_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result_data = data.get("data", {})
                        if "analysis" in result_data or "market_analysis" in result_data or "response" in result_data:
                            content = str(result_data)
                            if len(content) > 200:
                                self.log_test("Advanced AI Dubai Market Analysis", True, "Dubai market analysis working correctly")
                                return True
                            else:
                                self.log_test("Advanced AI Dubai Market Analysis", False, "Market analysis too short", data)
                                return False
                        else:
                            self.log_test("Advanced AI Dubai Market Analysis", False, "No market analysis in response", data)
                            return False
                    else:
                        self.log_test("Advanced AI Dubai Market Analysis", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Dubai Market Analysis", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Dubai Market Analysis", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_enhanced_chat(self):
        """Test POST /api/ai/advanced/enhanced-chat - Should still work"""
        try:
            chat_data = {
                "message": "I'm planning to open a luxury restaurant in Dubai Marina. What are the key considerations for success in this competitive market?",
                "session_id": "test_session_123",
                "context": {
                    "business_type": "restaurant",
                    "location": "Dubai Marina",
                    "segment": "luxury"
                }
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/enhanced-chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result_data = data.get("data", {})
                        if "response" in result_data:
                            chat_response = result_data["response"]
                            if len(chat_response) > 100:
                                self.log_test("Advanced AI Enhanced Chat", True, "Enhanced chat working correctly")
                                return True
                            else:
                                self.log_test("Advanced AI Enhanced Chat", False, "Chat response too short", data)
                                return False
                        else:
                            self.log_test("Advanced AI Enhanced Chat", False, "No chat response in data", data)
                            return False
                    else:
                        self.log_test("Advanced AI Enhanced Chat", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Enhanced Chat", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Enhanced Chat", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_capabilities(self):
        """Test GET /api/ai/advanced/capabilities - Should still work"""
        try:
            async with self.session.get(f"{API_BASE}/ai/advanced/capabilities") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "core_capabilities" in data.get("data", {}):
                        capabilities = data["data"]["core_capabilities"]
                        
                        # Check for key capabilities
                        expected_capabilities = ["reasoning", "coding", "vision", "multimodal"]
                        found_capabilities = []
                        
                        for cap in expected_capabilities:
                            if cap in capabilities:
                                found_capabilities.append(cap)
                        
                        if len(found_capabilities) >= 3:
                            self.log_test("Advanced AI Capabilities", True, f"Core capabilities found: {found_capabilities}")
                            return True
                        else:
                            self.log_test("Advanced AI Capabilities", False, f"Missing capabilities. Found: {found_capabilities}", data)
                            return False
                    else:
                        self.log_test("Advanced AI Capabilities", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Capabilities", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Capabilities", False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_ai_status(self):
        """Test GET /api/ai/advanced/status - Should still work"""
        try:
            async with self.session.get(f"{API_BASE}/ai/advanced/status") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "status" in data.get("data", {}):
                        status_data = data["data"]
                        if status_data.get("status") == "operational":
                            self.log_test("Advanced AI Status", True, "AI system status operational")
                            return True
                        else:
                            self.log_test("Advanced AI Status", False, f"System not operational: {status_data.get('status')}", data)
                            return False
                    else:
                        self.log_test("Advanced AI Status", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Advanced AI Status", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Advanced AI Status", False, f"Exception: {str(e)}")
            return False
    
    async def test_core_ai_problem_analysis(self):
        """Test POST /api/ai/analyze-problem - Core AI endpoint should still work"""
        try:
            problem_data = {
                "problem_description": "I need to expand my Dubai-based e-commerce business to other GCC countries. What are the key challenges and opportunities?",
                "industry": "ecommerce",
                "budget_range": "AED 500K - 1M"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/analyze-problem",
                json=problem_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        analysis = data.get("data", {}).get("analysis", {})
                        if analysis and "ai_analysis" in analysis and len(analysis["ai_analysis"]) > 100:
                            self.log_test("Core AI Problem Analysis", True, "Core AI analysis working correctly")
                            return True
                        else:
                            self.log_test("Core AI Problem Analysis", False, "Analysis content insufficient", data)
                            return False
                    else:
                        self.log_test("Core AI Problem Analysis", False, f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Core AI Problem Analysis", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Core AI Problem Analysis", False, f"Exception: {str(e)}")
            return False
    
    # ================================================================================================
    # TEST EXECUTION
    # ================================================================================================
    
    async def run_all_tests(self):
        """Run all advanced AI tests"""
        print("🚀 ADVANCED AI SYSTEMS RE-TESTING STARTED")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Priority re-tests (previously failed)
        print("\n🔥 PRIORITY RE-TESTS - PREVIOUSLY FAILED ENDPOINTS:")
        await self.test_advanced_ai_reasoning()
        await self.test_advanced_ai_code_generation()
        await self.test_advanced_ai_multimodal()
        
        # Regression tests (ensure no regressions)
        print("\n✅ REGRESSION TESTS - ENSURE NO REGRESSIONS:")
        await self.test_advanced_ai_models()
        await self.test_advanced_ai_vision()
        await self.test_advanced_ai_dubai_market_analysis()
        await self.test_advanced_ai_enhanced_chat()
        await self.test_advanced_ai_capabilities()
        await self.test_advanced_ai_status()
        await self.test_core_ai_problem_analysis()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 ADVANCED AI SYSTEMS RE-TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        if self.passed_tests:
            print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
            for test in self.passed_tests:
                print(f"  - {test}")
        
        print("\n" + "=" * 80)
        
        # Determine overall result
        if success_rate >= 90:
            print("🎉 EXCELLENT: Advanced AI Systems are production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Most Advanced AI Systems working, minor issues to address")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Several Advanced AI Systems need attention")
        else:
            print("❌ CRITICAL: Major issues with Advanced AI Systems")
        
        return success_rate >= 75  # Consider success if 75% or more tests pass

async def main():
    """Main test execution"""
    try:
        async with AdvancedAITester() as tester:
            success = await tester.run_all_tests()
            return 0 if success else 1
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)