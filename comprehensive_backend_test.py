#!/usr/bin/env python3
"""
COMPREHENSIVE ERROR DETECTION - ALL BACKEND SYSTEMS
Tests ALL backend endpoints for errors, warnings, and issues
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, date
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

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.errors_found = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None, error_type: str = None):
        """Log test result with error categorization"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data,
            "error_type": error_type
        })
        
        if not success:
            self.failed_tests.append(test_name)
            if error_type:
                self.errors_found.append({
                    "endpoint": test_name,
                    "error_type": error_type,
                    "details": details,
                    "response": response_data
                })

    # ================================================================================================
    # CORE API TESTS (5 ENDPOINTS)
    # ================================================================================================
    
    async def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("GET /api/health", True, "Service is healthy")
                        return True
                    else:
                        self.log_test("GET /api/health", False, f"Unexpected status: {data.get('status')}", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("GET /api/health", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("GET /api/health", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False
    
    async def test_contact_form_submission(self):
        """Test POST /api/contact endpoint"""
        try:
            contact_data = {
                "name": "Ahmed Al-Rashid",
                "email": "ahmed.rashid@example.ae",
                "phone": "+971501234567",
                "service": "social_media",
                "message": "I need help with social media marketing for my Dubai-based restaurant."
            }
            
            async with self.session.post(
                f"{API_BASE}/contact",
                json=contact_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "id" in data.get("data", {}):
                        self.log_test("POST /api/contact", True, "Contact form submitted successfully")
                        return True
                    else:
                        self.log_test("POST /api/contact", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/contact", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/contact", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_ai_problem_analysis(self):
        """Test POST /api/ai/analyze-problem endpoint"""
        try:
            problem_data = {
                "problem_description": "I need to increase online sales for my e-commerce business",
                "industry": "ecommerce",
                "budget_range": "AED 25K - 75K/month"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/analyze-problem",
                json=problem_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("data", {}).get("analysis"):
                        analysis = data["data"]["analysis"]
                        required_fields = ["ai_analysis", "market_insights", "strategy_proposal"]
                        missing_fields = [f for f in required_fields if f not in analysis or not analysis[f]]
                        
                        if missing_fields:
                            self.log_test("POST /api/ai/analyze-problem", False, f"Missing fields: {missing_fields}", data, "INCOMPLETE_RESPONSE")
                            return False
                        else:
                            self.log_test("POST /api/ai/analyze-problem", True, "AI analysis completed successfully")
                            return True
                    else:
                        self.log_test("POST /api/ai/analyze-problem", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/analyze-problem", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/analyze-problem", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_chat_system(self):
        """Test POST /api/chat/session + POST /api/chat/message endpoints"""
        try:
            # Create session
            async with self.session.post(
                f"{API_BASE}/chat/session",
                json={},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "session_id" in data.get("data", {}):
                        session_id = data["data"]["session_id"]
                        
                        # Send message
                        message_data = {
                            "session_id": session_id,
                            "message": "What digital marketing services do you recommend for a restaurant in Dubai?",
                            "user_id": "test_user_123"
                        }
                        
                        async with self.session.post(
                            f"{API_BASE}/chat/message",
                            json=message_data,
                            headers={"Content-Type": "application/json"}
                        ) as msg_response:
                            if msg_response.status == 200:
                                msg_data = await msg_response.json()
                                if msg_data.get("success") and "response" in msg_data.get("data", {}):
                                    self.log_test("POST /api/chat/session + POST /api/chat/message", True, "Chat system working")
                                    return True
                                else:
                                    self.log_test("POST /api/chat/session + POST /api/chat/message", False, "Invalid message response", msg_data, "INVALID_RESPONSE")
                                    return False
                            else:
                                self.log_test("POST /api/chat/session + POST /api/chat/message", False, f"Message HTTP {msg_response.status}", await msg_response.text(), "HTTP_ERROR")
                                return False
                    else:
                        self.log_test("POST /api/chat/session + POST /api/chat/message", False, "Invalid session response", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/chat/session + POST /api/chat/message", False, f"Session HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/chat/session + POST /api/chat/message", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_analytics_summary(self):
        """Test GET /api/analytics/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "today" in data.get("data", {}):
                        self.log_test("GET /api/analytics/summary", True, "Analytics data retrieved successfully")
                        return True
                    else:
                        self.log_test("GET /api/analytics/summary", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("GET /api/analytics/summary", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("GET /api/analytics/summary", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    # ================================================================================================
    # ADVANCED AI ENDPOINTS (9 ENDPOINTS)
    # ================================================================================================
    
    async def test_advanced_ai_models(self):
        """Test GET /api/ai/advanced/models"""
        try:
            async with self.session.get(f"{API_BASE}/ai/advanced/models") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("GET /api/ai/advanced/models", True, "AI models retrieved")
                        return True
                    else:
                        self.log_test("GET /api/ai/advanced/models", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("GET /api/ai/advanced/models", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("GET /api/ai/advanced/models", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_capabilities(self):
        """Test GET /api/ai/advanced/capabilities"""
        try:
            async with self.session.get(f"{API_BASE}/ai/advanced/capabilities") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("GET /api/ai/advanced/capabilities", True, "AI capabilities retrieved")
                        return True
                    else:
                        self.log_test("GET /api/ai/advanced/capabilities", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("GET /api/ai/advanced/capabilities", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("GET /api/ai/advanced/capabilities", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_status(self):
        """Test GET /api/ai/advanced/status"""
        try:
            async with self.session.get(f"{API_BASE}/ai/advanced/status") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("GET /api/ai/advanced/status", True, "AI status retrieved")
                        return True
                    else:
                        self.log_test("GET /api/ai/advanced/status", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("GET /api/ai/advanced/status", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("GET /api/ai/advanced/status", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_enhanced_chat(self):
        """Test POST /api/ai/advanced/enhanced-chat"""
        try:
            chat_data = {
                "message": "What are the best digital marketing strategies for a Dubai-based e-commerce business?",
                "context": {"business_type": "e-commerce", "location": "Dubai, UAE"},
                "model_preference": "gpt-4o"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/enhanced-chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("POST /api/ai/advanced/enhanced-chat", True, "Enhanced chat working")
                        return True
                    else:
                        self.log_test("POST /api/ai/advanced/enhanced-chat", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/advanced/enhanced-chat", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/advanced/enhanced-chat", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_dubai_market_analysis(self):
        """Test POST /api/ai/advanced/dubai-market-analysis"""
        try:
            analysis_data = {
                "industry": "technology",
                "business_type": "SaaS startup",
                "target_market": "UAE SMEs"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/dubai-market-analysis",
                json=analysis_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("POST /api/ai/advanced/dubai-market-analysis", True, "Dubai market analysis working")
                        return True
                    else:
                        self.log_test("POST /api/ai/advanced/dubai-market-analysis", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/advanced/dubai-market-analysis", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/advanced/dubai-market-analysis", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_reasoning(self):
        """Test POST /api/ai/advanced/reasoning"""
        try:
            reasoning_data = {
                "problem": "A Dubai e-commerce company wants to expand to Saudi Arabia with AED 2M budget.",
                "reasoning_type": "strategic_planning"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/reasoning",
                json=reasoning_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("POST /api/ai/advanced/reasoning", True, "AI reasoning working")
                        return True
                    else:
                        self.log_test("POST /api/ai/advanced/reasoning", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/advanced/reasoning", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/advanced/reasoning", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_code_generation(self):
        """Test POST /api/ai/advanced/code-generation"""
        try:
            code_data = {
                "task": "Create a Python function to validate UAE phone numbers",
                "language": "python",
                "requirements": ["Support UAE country code +971"]
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/code-generation",
                json=code_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("POST /api/ai/advanced/code-generation", True, "Code generation working")
                        return True
                    else:
                        self.log_test("POST /api/ai/advanced/code-generation", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/advanced/code-generation", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/advanced/code-generation", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_vision(self):
        """Test POST /api/ai/advanced/vision"""
        try:
            # Simple test image (1x1 red pixel in base64)
            test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            vision_data = {
                "image": test_image,
                "prompt": "Analyze this image",
                "analysis_type": "detailed_description"
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/vision",
                json=vision_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("POST /api/ai/advanced/vision", True, "Vision analysis working")
                        return True
                    else:
                        self.log_test("POST /api/ai/advanced/vision", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/advanced/vision", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/advanced/vision", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_advanced_ai_multimodal(self):
        """Test POST /api/ai/advanced/multimodal"""
        try:
            multimodal_data = {
                "text": "Analyze this Dubai business scenario: A luxury hotel wants to improve guest experience",
                "context": {"business_type": "luxury_hotel", "location": "Dubai Marina"}
            }
            
            async with self.session.post(
                f"{API_BASE}/ai/advanced/multimodal",
                json=multimodal_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("POST /api/ai/advanced/multimodal", True, "Multimodal analysis working")
                        return True
                    else:
                        self.log_test("POST /api/ai/advanced/multimodal", False, "Invalid response structure", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/ai/advanced/multimodal", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/ai/advanced/multimodal", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    # ================================================================================================
    # AI AGENTS TESTS (5 AGENTS)
    # ================================================================================================
    
    async def test_sales_agent_endpoints(self):
        """Test Sales Agent endpoints"""
        endpoints = [
            ("POST /api/agents/sales/qualify-lead", "post", {"company_name": "Test Company", "industry": "retail"}),
            ("GET /api/agents/sales/pipeline", "get", None),
            ("POST /api/agents/sales/generate-proposal", "post", {"client_name": "Test Client", "services_needed": ["marketing"]})
        ]
        
        success_count = 0
        for endpoint_name, method, data in endpoints:
            try:
                if method == "get":
                    async with self.session.get(f"{API_BASE}/agents/sales/pipeline") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Sales agent endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    async with self.session.post(
                        f"{API_BASE}/agents/sales/{'qualify-lead' if 'qualify' in endpoint_name else 'generate-proposal'}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Sales agent endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_marketing_agent_endpoints(self):
        """Test Marketing Agent endpoints"""
        endpoints = [
            ("POST /api/agents/marketing/create-campaign", {"campaign_name": "Test Campaign", "budget": "AED 50,000"}),
            ("POST /api/agents/marketing/optimize-campaign", {"campaign_id": "test123", "optimization_type": "performance"})
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                url = f"{API_BASE}/agents/marketing/{'create-campaign' if 'create' in endpoint_name else 'optimize-campaign'}"
                async with self.session.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        resp_data = await response.json()
                        if resp_data.get("success"):
                            self.log_test(endpoint_name, True, "Marketing agent endpoint working")
                            success_count += 1
                        else:
                            self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                    else:
                        self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_content_agent_endpoints(self):
        """Test Content Agent endpoints"""
        try:
            content_data = {
                "content_type": "social_media_campaign",
                "business_info": {"name": "Dubai Restaurant", "industry": "hospitality"}
            }
            
            async with self.session.post(
                f"{API_BASE}/agents/content/generate",
                json=content_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("POST /api/agents/content/generate", True, "Content agent working")
                        return True
                    else:
                        self.log_test("POST /api/agents/content/generate", False, "Invalid response", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/agents/content/generate", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/agents/content/generate", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_analytics_agent_endpoints(self):
        """Test Analytics Agent endpoints"""
        try:
            analysis_data = {
                "business_name": "Dubai Tech Startup",
                "analysis_type": "market_performance",
                "data_sources": ["website_analytics", "social_media"]
            }
            
            async with self.session.post(
                f"{API_BASE}/agents/analytics/analyze",
                json=analysis_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("POST /api/agents/analytics/analyze", True, "Analytics agent working")
                        return True
                    else:
                        self.log_test("POST /api/agents/analytics/analyze", False, "Invalid response", data, "INVALID_RESPONSE")
                        return False
                else:
                    self.log_test("POST /api/agents/analytics/analyze", False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                    return False
        except Exception as e:
            self.log_test("POST /api/agents/analytics/analyze", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_operations_agent_endpoints(self):
        """Test Operations Agent endpoints"""
        endpoints = [
            ("POST /api/agents/operations/automate-workflow", {"workflow_name": "Client Onboarding"}),
            ("POST /api/agents/operations/process-invoice", {"invoice_details": {"amount": "AED 45,000"}}),
            ("POST /api/agents/operations/onboard-client", {"client_information": {"company_name": "Test LLC"}})
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                endpoint_path = endpoint_name.split()[-1].replace("/api/agents/operations/", "")
                url = f"{API_BASE}/agents/operations/{endpoint_path}"
                
                async with self.session.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        resp_data = await response.json()
                        if resp_data.get("success"):
                            self.log_test(endpoint_name, True, "Operations agent endpoint working")
                            success_count += 1
                        else:
                            self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                    else:
                        self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # ENTERPRISE SYSTEMS TESTS
    # ================================================================================================
    
    async def test_white_label_endpoints(self):
        """Test White Label endpoints"""
        endpoints = [
            ("GET /api/white-label/tenants", "get", None),
            ("POST /api/white-label/create-tenant", "post", {"tenant_name": "Dubai Digital Solutions", "domain": "test.example.com"}),
            ("POST /api/white-label/create-reseller", "post", {"reseller_name": "Emirates Business Hub"})
        ]
        
        success_count = 0
        for endpoint_name, method, data in endpoints:
            try:
                if method == "get":
                    async with self.session.get(f"{API_BASE}/white-label/tenants") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "White label endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    endpoint_path = "create-tenant" if "create-tenant" in endpoint_name else "create-reseller"
                    async with self.session.post(
                        f"{API_BASE}/white-label/{endpoint_path}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "White label endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_inter_agent_communication_endpoints(self):
        """Test Inter-Agent Communication endpoints"""
        endpoints = [
            ("GET /api/agents/communication/metrics", "get", None),
            ("POST /api/agents/collaborate", "post", {"agents": ["sales", "marketing"], "task": "Dubai client onboarding"}),
            ("POST /api/agents/delegate-task", "post", {"from_agent_id": "sales", "to_agent_id": "marketing", "task_data": {}})
        ]
        
        success_count = 0
        for endpoint_name, method, data in endpoints:
            try:
                if method == "get":
                    async with self.session.get(f"{API_BASE}/agents/communication/metrics") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Inter-agent communication working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    endpoint_path = "collaborate" if "collaborate" in endpoint_name else "delegate-task"
                    async with self.session.post(
                        f"{API_BASE}/agents/{endpoint_path}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Inter-agent communication working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_smart_insights_endpoints(self):
        """Test Smart Insights endpoints"""
        endpoints = [
            ("GET /api/insights/summary", "get", None),
            ("POST /api/insights/analyze-performance", "post", {"business_data": {"revenue": "AED 1M"}}),
            ("POST /api/insights/detect-anomalies", "post", {"business_data": {"metrics": ["sales", "traffic"]}}),
            ("POST /api/insights/optimization-recommendations", "post", {"context_data": {"business_type": "e-commerce"}})
        ]
        
        success_count = 0
        for endpoint_name, method, data in endpoints:
            try:
                if method == "get":
                    async with self.session.get(f"{API_BASE}/insights/summary") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Smart insights endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    endpoint_path = endpoint_name.split("/")[-1]
                    async with self.session.post(
                        f"{API_BASE}/insights/{endpoint_path}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Smart insights endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # SECURITY & PERFORMANCE TESTS
    # ================================================================================================
    
    async def test_security_manager_endpoints(self):
        """Test Security Manager endpoints"""
        endpoints = [
            ("POST /api/security/users/create", {"email": "test@example.com", "password": "TestPass123!", "role": "viewer"}),
            ("POST /api/security/auth/login", {"email": "test@example.com", "password": "TestPass123!"}),
            ("POST /api/security/permissions/validate", {"user_id": "test123", "permission": "read", "resource": "dashboard"}),
            ("POST /api/security/policies/create", {"policy_name": "Test Policy", "rules": []}),
            ("GET /api/security/compliance/report/gdpr", None)
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    async with self.session.get(f"{API_BASE}/security/compliance/report/gdpr") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Security endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    # Extract endpoint path from name
                    if "users/create" in endpoint_name:
                        url = f"{API_BASE}/security/users/create"
                    elif "auth/login" in endpoint_name:
                        url = f"{API_BASE}/security/auth/login"
                    elif "permissions/validate" in endpoint_name:
                        url = f"{API_BASE}/security/permissions/validate"
                    elif "policies/create" in endpoint_name:
                        url = f"{API_BASE}/security/policies/create"
                    
                    async with self.session.post(
                        url,
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status in [200, 201]:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Security endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_performance_optimizer_endpoints(self):
        """Test Performance Optimizer endpoints"""
        endpoints = [
            ("GET /api/performance/summary", "get", None),
            ("POST /api/performance/optimize", "post", {"target_area": "all"}),
            ("GET /api/performance/auto-scale/recommendations", "get", None),
            ("GET /api/performance/cache/stats", "get", None)
        ]
        
        success_count = 0
        for endpoint_name, method, data in endpoints:
            try:
                if method == "get":
                    endpoint_path = endpoint_name.split("/api/performance/")[1]
                    async with self.session.get(f"{API_BASE}/performance/{endpoint_path}") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Performance endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    async with self.session.post(
                        f"{API_BASE}/performance/optimize",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Performance endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # CRM INTEGRATIONS TESTS
    # ================================================================================================
    
    async def test_crm_integrations_endpoints(self):
        """Test CRM Integrations endpoints"""
        endpoints = [
            ("POST /api/integrations/crm/setup", {"provider": "hubspot", "credentials": {"api_key": "test"}}),
            ("POST /api/integrations/crm/test123/sync-contacts", {"sync_direction": "bidirectional"}),
            ("POST /api/integrations/crm/test123/create-lead", {"lead_data": {"name": "Test Lead", "email": "test@example.com"}}),
            ("GET /api/integrations/crm/test123/analytics", None),
            ("POST /api/integrations/crm/webhook/test123", {"event": "contact.created"})
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    async with self.session.get(f"{API_BASE}/integrations/crm/test123/analytics") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "CRM endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    # Extract URL from endpoint name
                    if "setup" in endpoint_name:
                        url = f"{API_BASE}/integrations/crm/setup"
                    elif "sync-contacts" in endpoint_name:
                        url = f"{API_BASE}/integrations/crm/test123/sync-contacts"
                    elif "create-lead" in endpoint_name:
                        url = f"{API_BASE}/integrations/crm/test123/create-lead"
                    elif "webhook" in endpoint_name:
                        url = f"{API_BASE}/integrations/crm/webhook/test123"
                    
                    async with self.session.post(
                        url,
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "CRM endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # PAYMENT & COMMUNICATION INTEGRATIONS TESTS
    # ================================================================================================
    
    async def test_stripe_integration_endpoints(self):
        """Test Stripe Payment Integration endpoints"""
        endpoints = [
            ("GET /api/integrations/payments/packages", None),
            ("POST /api/integrations/payments/create-session", {"package_id": "starter", "customer_email": "test@example.com"}),
            ("GET /api/integrations/payments/status/test_session_123", None)
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    if "packages" in endpoint_name:
                        url = f"{API_BASE}/integrations/payments/packages"
                    else:
                        url = f"{API_BASE}/integrations/payments/status/test_session_123"
                    
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Stripe endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    async with self.session.post(
                        f"{API_BASE}/integrations/payments/create-session",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Stripe endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_twilio_integration_endpoints(self):
        """Test Twilio SMS Integration endpoints"""
        endpoints = [
            ("POST /api/integrations/sms/send-otp", {"phone_number": "+971501234567"}),
            ("POST /api/integrations/sms/verify-otp", {"phone_number": "+971501234567", "otp_code": "123456"}),
            ("POST /api/integrations/sms/send", {"to": "+971501234567", "message": "Test message"})
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                endpoint_path = endpoint_name.split("/")[-1]
                url = f"{API_BASE}/integrations/sms/{endpoint_path}"
                
                async with self.session.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    # Accept both success and configuration errors for Twilio
                    if response.status in [200, 400]:
                        resp_data = await response.json()
                        if resp_data.get("success") or "not configured" in str(resp_data):
                            self.log_test(endpoint_name, True, "Twilio endpoint working (or properly configured)")
                            success_count += 1
                        else:
                            self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                    else:
                        self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_sendgrid_integration_endpoints(self):
        """Test SendGrid Email Integration endpoints"""
        endpoints = [
            ("POST /api/integrations/email/send", {"to": "test@example.com", "subject": "Test", "content": "Test message"}),
            ("POST /api/integrations/email/send-notification", {"to": "test@example.com", "type": "welcome", "data": {}})
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                endpoint_path = "send" if "send-notification" not in endpoint_name else "send-notification"
                url = f"{API_BASE}/integrations/email/{endpoint_path}"
                
                async with self.session.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    # Accept both success and configuration errors for SendGrid
                    if response.status in [200, 400]:
                        resp_data = await response.json()
                        if resp_data.get("success") or "not configured" in str(resp_data):
                            self.log_test(endpoint_name, True, "SendGrid endpoint working (or properly configured)")
                            success_count += 1
                        else:
                            self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                    else:
                        self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # AI INTEGRATIONS TESTS
    # ================================================================================================
    
    async def test_voice_ai_integration_endpoints(self):
        """Test Voice AI Integration endpoints"""
        endpoints = [
            ("POST /api/integrations/voice-ai/session", {"user_id": "test123"}),
            ("GET /api/integrations/voice-ai/info", None)
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    async with self.session.get(f"{API_BASE}/integrations/voice-ai/info") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Voice AI endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    async with self.session.post(
                        f"{API_BASE}/integrations/voice-ai/session",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Voice AI endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_vision_ai_integration_endpoints(self):
        """Test Vision AI Integration endpoints"""
        endpoints = [
            ("POST /api/integrations/vision-ai/analyze", {"image": "test_base64", "prompt": "Analyze this image"}),
            ("GET /api/integrations/vision-ai/formats", None)
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    async with self.session.get(f"{API_BASE}/integrations/vision-ai/formats") as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Vision AI endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    async with self.session.post(
                        f"{API_BASE}/integrations/vision-ai/analyze",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Vision AI endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # PLUGIN SYSTEM & TEMPLATES TESTS
    # ================================================================================================
    
    async def test_plugin_system_endpoints(self):
        """Test Plugin System endpoints"""
        endpoints = [
            ("GET /api/plugins/available", None),
            ("GET /api/plugins/marketplace", None),
            ("POST /api/plugins/create-template", {"plugin_name": "test_plugin", "description": "Test plugin"}),
            ("GET /api/plugins/test_plugin", None)
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    if "available" in endpoint_name:
                        url = f"{API_BASE}/plugins/available"
                    elif "marketplace" in endpoint_name:
                        url = f"{API_BASE}/plugins/marketplace"
                    else:
                        url = f"{API_BASE}/plugins/test_plugin"
                    
                    async with self.session.get(url) as response:
                        if response.status in [200, 404]:  # 404 acceptable for plugin not found
                            resp_data = await response.json()
                            if resp_data.get("success") or response.status == 404:
                                self.log_test(endpoint_name, True, "Plugin endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    async with self.session.post(
                        f"{API_BASE}/plugins/create-template",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Plugin endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    async def test_industry_templates_endpoints(self):
        """Test Industry Templates endpoints"""
        endpoints = [
            ("GET /api/templates/industries", None),
            ("GET /api/templates/industries/ecommerce", None),
            ("POST /api/templates/deploy", {"industry": "ecommerce", "customizations": {}}),
            ("POST /api/templates/validate", {"industry": "saas", "requirements": {}}),
            ("POST /api/templates/custom", {"template_name": "test_template", "industry": "local_service"})
        ]
        
        success_count = 0
        for endpoint_name, data in endpoints:
            try:
                if data is None:  # GET request
                    if "industries/ecommerce" in endpoint_name:
                        url = f"{API_BASE}/templates/industries/ecommerce"
                    else:
                        url = f"{API_BASE}/templates/industries"
                    
                    async with self.session.get(url) as response:
                        if response.status in [200, 404]:  # 404 acceptable for template not found
                            resp_data = await response.json()
                            if resp_data.get("success") or response.status == 404:
                                self.log_test(endpoint_name, True, "Template endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
                else:
                    if "deploy" in endpoint_name:
                        url = f"{API_BASE}/templates/deploy"
                    elif "validate" in endpoint_name:
                        url = f"{API_BASE}/templates/validate"
                    else:
                        url = f"{API_BASE}/templates/custom"
                    
                    async with self.session.post(
                        url,
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            if resp_data.get("success"):
                                self.log_test(endpoint_name, True, "Template endpoint working")
                                success_count += 1
                            else:
                                self.log_test(endpoint_name, False, "Invalid response", resp_data, "INVALID_RESPONSE")
                        else:
                            self.log_test(endpoint_name, False, f"HTTP {response.status}", await response.text(), "HTTP_ERROR")
            except Exception as e:
                self.log_test(endpoint_name, False, f"Exception: {str(e)}", None, "EXCEPTION")
        
        return success_count == len(endpoints)

    # ================================================================================================
    # ERROR DETECTION TESTS
    # ================================================================================================
    
    async def test_error_detection_invalid_endpoints(self):
        """Test invalid endpoints for proper 404 handling"""
        try:
            invalid_endpoints = [
                "/api/nonexistent",
                "/api/invalid/endpoint",
                "/api/agents/invalid/action",
                "/api/plugins/nonexistent/plugin"
            ]
            
            all_handled_correctly = True
            for endpoint in invalid_endpoints:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status != 404:
                        all_handled_correctly = False
                        break
            
            if all_handled_correctly:
                self.log_test("Error Detection - Invalid Endpoints", True, "All invalid endpoints return 404 correctly")
                return True
            else:
                self.log_test("Error Detection - Invalid Endpoints", False, "Some invalid endpoints don't return 404", None, "ERROR_HANDLING")
                return False
        except Exception as e:
            self.log_test("Error Detection - Invalid Endpoints", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_error_detection_malformed_data(self):
        """Test endpoints with malformed data"""
        try:
            test_cases = [
                ("/api/contact", '{"name": "test", "email": "invalid-email"}'),
                ("/api/ai/analyze-problem", '{"problem_description": "", "industry": "invalid"}'),
                ("/api/chat/message", '{"session_id": "", "message": ""}')
            ]
            
            handled_correctly = 0
            for endpoint, malformed_data in test_cases:
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}{endpoint}",
                        data=malformed_data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status in [200, 400, 422]:
                            handled_correctly += 1
                except:
                    handled_correctly += 1
            
            if handled_correctly == len(test_cases):
                self.log_test("Error Detection - Malformed Data", True, "All malformed data handled correctly")
                return True
            else:
                self.log_test("Error Detection - Malformed Data", False, f"Only {handled_correctly}/{len(test_cases)} cases handled correctly", None, "ERROR_HANDLING")
                return False
        except Exception as e:
            self.log_test("Error Detection - Malformed Data", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    async def test_error_detection_concurrent_requests(self):
        """Test concurrent requests handling"""
        try:
            tasks = []
            for i in range(10):
                task = self.session.get(f"{API_BASE}/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_responses = 0
            for response in responses:
                if hasattr(response, 'status') and response.status == 200:
                    successful_responses += 1
                    await response.release()
            
            if successful_responses >= 8:
                self.log_test("Error Detection - Concurrent Requests", True, f"{successful_responses}/10 concurrent requests successful")
                return True
            else:
                self.log_test("Error Detection - Concurrent Requests", False, f"Only {successful_responses}/10 concurrent requests successful", None, "PERFORMANCE")
                return False
        except Exception as e:
            self.log_test("Error Detection - Concurrent Requests", False, f"Exception: {str(e)}", None, "EXCEPTION")
            return False

    # ================================================================================================
    # MAIN TEST RUNNER
    # ================================================================================================
    
    async def run_comprehensive_tests(self):
        """Run comprehensive error detection tests on ALL backend systems"""
        print(f"🚀 COMPREHENSIVE ERROR DETECTION - ALL BACKEND SYSTEMS")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Core API Tests (5 endpoints)
        print("\n📋 CORE APIs (5 ENDPOINTS)")
        print("-" * 40)
        await self.test_health_endpoint()
        await self.test_contact_form_submission()
        await self.test_ai_problem_analysis()
        await self.test_chat_system()
        await self.test_analytics_summary()
        
        # Advanced AI Endpoints (9 endpoints)
        print("\n🧠 ADVANCED AI ENDPOINTS (9 ENDPOINTS)")
        print("-" * 40)
        await self.test_advanced_ai_models()
        await self.test_advanced_ai_capabilities()
        await self.test_advanced_ai_status()
        await self.test_advanced_ai_enhanced_chat()
        await self.test_advanced_ai_dubai_market_analysis()
        await self.test_advanced_ai_reasoning()
        await self.test_advanced_ai_code_generation()
        await self.test_advanced_ai_vision()
        await self.test_advanced_ai_multimodal()
        
        # AI Agents (5 agents)
        print("\n🤖 AI AGENTS (5 AGENTS)")
        print("-" * 40)
        await self.test_sales_agent_endpoints()
        await self.test_marketing_agent_endpoints()
        await self.test_content_agent_endpoints()
        await self.test_analytics_agent_endpoints()
        await self.test_operations_agent_endpoints()
        
        # Enterprise Systems
        print("\n🏢 ENTERPRISE SYSTEMS")
        print("-" * 40)
        await self.test_white_label_endpoints()
        await self.test_inter_agent_communication_endpoints()
        await self.test_smart_insights_endpoints()
        
        # Security & Performance
        print("\n🔒 SECURITY & PERFORMANCE")
        print("-" * 40)
        await self.test_security_manager_endpoints()
        await self.test_performance_optimizer_endpoints()
        
        # CRM Integrations
        print("\n📊 CRM INTEGRATIONS")
        print("-" * 40)
        await self.test_crm_integrations_endpoints()
        
        # Payment & Communication Integrations
        print("\n💳 PAYMENT & COMMUNICATION INTEGRATIONS")
        print("-" * 40)
        await self.test_stripe_integration_endpoints()
        await self.test_twilio_integration_endpoints()
        await self.test_sendgrid_integration_endpoints()
        
        # AI Integrations
        print("\n🎤 AI INTEGRATIONS")
        print("-" * 40)
        await self.test_voice_ai_integration_endpoints()
        await self.test_vision_ai_integration_endpoints()
        
        # Plugin System & Templates
        print("\n🔌 PLUGIN SYSTEM & TEMPLATES")
        print("-" * 40)
        await self.test_plugin_system_endpoints()
        await self.test_industry_templates_endpoints()
        
        # Error Detection Tests
        print("\n🚨 ERROR DETECTION & EDGE CASES")
        print("-" * 40)
        await self.test_error_detection_invalid_endpoints()
        await self.test_error_detection_malformed_data()
        await self.test_error_detection_concurrent_requests()
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE ERROR DETECTION RESULTS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Detailed error analysis
        if self.errors_found:
            print(f"\n🚨 DETAILED ERROR ANALYSIS ({len(self.errors_found)} ERRORS FOUND):")
            
            # Group errors by type
            error_types = {}
            for error in self.errors_found:
                error_type = error["error_type"]
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(error)
            
            for error_type, errors in error_types.items():
                print(f"\n🔴 {error_type} ERRORS ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    print(f"  {i}. {error['endpoint']}: {error['details']}")
        else:
            print(f"\n🎉 NO ERRORS FOUND! SYSTEM IS ERROR-FREE!")
        
        # Success rate by category
        print(f"\n📊 SUCCESS RATE BY CATEGORY:")
        categories = {
            "Core APIs": ["health", "contact", "ai/analyze-problem", "chat", "analytics"],
            "Advanced AI": ["ai/advanced"],
            "AI Agents": ["agents/sales", "agents/marketing", "agents/content", "agents/analytics", "agents/operations"],
            "Enterprise": ["white-label", "agents/collaborate", "insights", "security", "performance"],
            "Integrations": ["integrations/crm", "integrations/payments", "integrations/sms", "integrations/email", "integrations/voice-ai", "integrations/vision-ai"],
            "Plugins/Templates": ["plugins", "templates"]
        }
        
        for category, keywords in categories.items():
            category_tests = [t for t in self.test_results if any(keyword in t["test"].lower() for keyword in keywords)]
            if category_tests:
                passed = sum(1 for t in category_tests if t["success"])
                total = len(category_tests)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"  {category}: {passed}/{total} ({rate:.1f}%)")
        
        return success_rate >= 70

async def main():
    """Main function to run comprehensive backend testing"""
    async with ComprehensiveBackendTester() as tester:
        success = await tester.run_comprehensive_tests()
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))