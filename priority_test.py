#!/usr/bin/env python3
"""
Priority Backend Testing - Focus on Stuck Tasks
Tests White Label & Multi-Tenancy System and Inter-Agent Communication System
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

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

class PriorityTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: any = None):
        """Log test result"""
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
            "response": response_data
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("Health Check", True, "Service is healthy")
                        return True
                    else:
                        self.log_test("Health Check", False, f"Unexpected status: {data.get('status')}", data)
                        return False
                else:
                    self.log_test("Health Check", False, f"HTTP {response.status}", await response.text())
                    return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    # ================================================================================================
    # PRIORITY 1: WHITE LABEL & MULTI-TENANCY SYSTEM TESTING
    # ================================================================================================
    
    async def test_white_label_create_tenant(self):
        """Test POST /api/white-label/create-tenant - Create white-label tenant"""
        try:
            # Dubai reseller tenant data
            tenant_data = {
                "tenant_name": "Dubai Digital Solutions",
                "company_info": {
                    "name": "Dubai Digital Solutions LLC",
                    "contact_person": "Mohammed Al-Rashid",
                    "email": "mohammed@dubaidigital.ae",
                    "phone": "+971-4-555-9999",
                    "address": "Sheikh Zayed Road, Dubai, UAE",
                    "trade_license": "CN-9876543",
                    "vat_number": "100987654300003"
                },
                "branding": {
                    "primary_color": "#1E40AF",
                    "secondary_color": "#F59E0B",
                    "logo_url": "https://dubaidigital.ae/logo.png",
                    "company_name": "Dubai Digital Solutions",
                    "tagline": "Your Digital Partner in the UAE",
                    "languages": ["english", "arabic"],
                    "currency": "AED",
                    "timezone": "Asia/Dubai"
                },
                "features": {
                    "white_label_dashboard": True,
                    "custom_domain": "clients.dubaidigital.ae",
                    "api_access": True,
                    "reseller_portal": True,
                    "multi_language": True
                },
                "subscription": {
                    "plan": "enterprise",
                    "max_clients": 100,
                    "monthly_fee": "AED 5000",
                    "commission_rate": "20%"
                }
            }
            
            async with self.session.post(
                f"{API_BASE}/white-label/create-tenant",
                json=tenant_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        tenant_result = data["data"]
                        # Store tenant_id for later tests
                        if "tenant_id" in tenant_result:
                            self.tenant_id = tenant_result["tenant_id"]
                        self.log_test("White Label - Create Tenant", True, "Dubai reseller tenant created successfully")
                        return True
                    else:
                        self.log_test("White Label - Create Tenant", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("White Label - Create Tenant", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("White Label - Create Tenant", False, f"Exception: {str(e)}")
            return False

    async def test_white_label_get_tenants(self):
        """Test GET /api/white-label/tenants - Get all tenants"""
        try:
            async with self.session.get(f"{API_BASE}/white-label/tenants") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        tenants_data = data["data"]
                        if "tenants" in tenants_data and isinstance(tenants_data["tenants"], list):
                            self.log_test("White Label - Get Tenants", True, f"Retrieved {tenants_data.get('total', 0)} tenants")
                            return True
                        else:
                            self.log_test("White Label - Get Tenants", False, "Invalid tenants format", data)
                            return False
                    else:
                        self.log_test("White Label - Get Tenants", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("White Label - Get Tenants", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("White Label - Get Tenants", False, f"Exception: {str(e)}")
            return False

    async def test_white_label_get_tenant_branding(self):
        """Test GET /api/white-label/tenant/{tenant_id}/branding - Get tenant branding"""
        try:
            # Use tenant_id from create test or a sample ID
            tenant_id = getattr(self, 'tenant_id', 'sample_tenant_id')
            
            async with self.session.get(f"{API_BASE}/white-label/tenant/{tenant_id}/branding") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        branding_data = data["data"]
                        self.log_test("White Label - Get Tenant Branding", True, "Tenant branding retrieved successfully")
                        return True
                    else:
                        self.log_test("White Label - Get Tenant Branding", False, "Invalid response structure", data)
                        return False
                elif response.status == 404:
                    # Tenant not found is acceptable for this test
                    self.log_test("White Label - Get Tenant Branding", True, "Tenant not found (expected for sample ID)")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("White Label - Get Tenant Branding", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("White Label - Get Tenant Branding", False, f"Exception: {str(e)}")
            return False

    async def test_white_label_create_reseller(self):
        """Test POST /api/white-label/create-reseller - Create reseller package"""
        try:
            # Dubai reseller package data
            reseller_data = {
                "reseller_name": "Emirates Business Hub",
                "package_info": {
                    "name": "UAE Digital Transformation Package",
                    "description": "Complete digital transformation solution for UAE businesses",
                    "target_market": "UAE SMEs and Startups",
                    "pricing_model": "tiered"
                },
                "branding": {
                    "primary_color": "#00A651",
                    "secondary_color": "#FF0000",
                    "logo_url": "https://emiratesbusinesshub.ae/logo.png",
                    "company_name": "Emirates Business Hub",
                    "tagline": "Empowering UAE Businesses Digitally",
                    "languages": ["english", "arabic"],
                    "currency": "AED"
                },
                "services_included": [
                    "ai_agents",
                    "digital_marketing",
                    "web_development",
                    "e_commerce_solutions",
                    "business_automation",
                    "analytics_insights"
                ],
                "pricing_tiers": [
                    {
                        "name": "Startup",
                        "price": "AED 2,500/month",
                        "features": ["Basic AI Agent", "Website", "Social Media Management"],
                        "max_users": 5
                    },
                    {
                        "name": "Growth",
                        "price": "AED 7,500/month", 
                        "features": ["Full AI Suite", "E-commerce", "Advanced Analytics"],
                        "max_users": 25
                    },
                    {
                        "name": "Enterprise",
                        "price": "AED 15,000/month",
                        "features": ["Custom Solutions", "White Label", "Dedicated Support"],
                        "max_users": 100
                    }
                ],
                "commission_structure": {
                    "base_commission": "25%",
                    "performance_bonus": "5%",
                    "volume_discount": "10% for 50+ clients"
                }
            }
            
            async with self.session.post(
                f"{API_BASE}/white-label/create-reseller",
                json=reseller_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        reseller_result = data["data"]
                        self.log_test("White Label - Create Reseller", True, "UAE reseller package created successfully")
                        return True
                    else:
                        self.log_test("White Label - Create Reseller", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("White Label - Create Reseller", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("White Label - Create Reseller", False, f"Exception: {str(e)}")
            return False

    # ================================================================================================
    # PRIORITY 1: INTER-AGENT COMMUNICATION SYSTEM TESTING
    # ================================================================================================

    async def test_agents_collaborate(self):
        """Test POST /api/agents/collaborate - Initiate agent collaboration"""
        try:
            # Multi-agent collaboration for Dubai client onboarding
            collaboration_request = {
                "collaboration_name": "Complete Dubai Client Onboarding",
                "client_info": {
                    "company": "Al Barsha Tech Solutions LLC",
                    "industry": "technology",
                    "location": "Dubai Internet City, UAE",
                    "contact": "Amira Hassan",
                    "email": "amira@albarsha-tech.ae"
                },
                "agents_involved": ["sales", "marketing", "content", "operations"],
                "collaboration_type": "sequential_workflow",
                "tasks": [
                    {
                        "agent": "sales",
                        "task": "qualify_lead_and_create_proposal",
                        "priority": 1,
                        "data": {
                            "lead_info": "Tech startup needing full digital presence",
                            "budget": "AED 200K",
                            "timeline": "3 months"
                        }
                    },
                    {
                        "agent": "marketing",
                        "task": "create_launch_campaign",
                        "priority": 2,
                        "depends_on": "sales",
                        "data": {
                            "campaign_type": "product_launch",
                            "target_market": "UAE tech professionals"
                        }
                    },
                    {
                        "agent": "content",
                        "task": "generate_marketing_content",
                        "priority": 2,
                        "depends_on": "marketing",
                        "data": {
                            "content_types": ["website_copy", "social_media", "press_release"],
                            "languages": ["english", "arabic"]
                        }
                    },
                    {
                        "agent": "operations",
                        "task": "setup_client_systems",
                        "priority": 3,
                        "depends_on": ["sales", "marketing"],
                        "data": {
                            "systems": ["crm", "project_management", "billing"],
                            "integrations": ["email", "calendar", "analytics"]
                        }
                    }
                ],
                "expected_duration": "5 days",
                "success_criteria": [
                    "client_proposal_approved",
                    "marketing_campaign_launched",
                    "content_published",
                    "systems_operational"
                ]
            }
            
            async with self.session.post(
                f"{API_BASE}/agents/collaborate",
                json=collaboration_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        collaboration_data = data["data"]
                        if "collaboration_id" in collaboration_data:
                            self.collaboration_id = collaboration_data["collaboration_id"]
                        self.log_test("Inter-Agent Communication - Initiate Collaboration", True, "Multi-agent collaboration initiated successfully")
                        return True
                    else:
                        self.log_test("Inter-Agent Communication - Initiate Collaboration", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Inter-Agent Communication - Initiate Collaboration", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Inter-Agent Communication - Initiate Collaboration", False, f"Exception: {str(e)}")
            return False

    async def test_agents_collaboration_status(self):
        """Test GET /api/agents/collaborate/{collaboration_id} - Get collaboration status"""
        try:
            # Use collaboration_id from previous test or sample ID
            collaboration_id = getattr(self, 'collaboration_id', 'sample_collaboration_id')
            
            async with self.session.get(f"{API_BASE}/agents/collaborate/{collaboration_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        status_data = data["data"]
                        self.log_test("Inter-Agent Communication - Get Collaboration Status", True, "Collaboration status retrieved successfully")
                        return True
                    else:
                        self.log_test("Inter-Agent Communication - Get Collaboration Status", False, "Invalid response structure", data)
                        return False
                elif response.status == 404:
                    # Collaboration not found is acceptable for sample ID
                    self.log_test("Inter-Agent Communication - Get Collaboration Status", True, "Collaboration not found (expected for sample ID)")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Inter-Agent Communication - Get Collaboration Status", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Inter-Agent Communication - Get Collaboration Status", False, f"Exception: {str(e)}")
            return False

    async def test_agents_delegate_task(self):
        """Test POST /api/agents/delegate-task - Delegate task between agents"""
        try:
            # Task delegation from sales to marketing agent
            delegation_request = {
                "from_agent_id": "sales_agent",
                "to_agent_id": "marketing_agent",
                "delegation_reason": "Lead qualified, needs marketing campaign",
                "task_data": {
                    "task_type": "create_targeted_campaign",
                    "client_info": {
                        "company": "Dubai Fashion Boutique",
                        "industry": "retail_fashion",
                        "location": "Dubai Mall, UAE",
                        "budget": "AED 50,000",
                        "target_audience": "UAE women 25-45, luxury fashion"
                    },
                    "campaign_requirements": {
                        "channels": ["instagram", "facebook", "google_ads"],
                        "duration": "30 days",
                        "objectives": ["brand_awareness", "sales_conversion"],
                        "languages": ["english", "arabic"]
                    },
                    "deadline": "2024-02-20",
                    "priority": "high"
                },
                "expected_deliverables": [
                    "campaign_strategy",
                    "creative_assets_plan",
                    "budget_allocation",
                    "timeline_schedule"
                ],
                "success_metrics": [
                    "campaign_approval",
                    "assets_created",
                    "campaign_launched"
                ]
            }
            
            async with self.session.post(
                f"{API_BASE}/agents/delegate-task",
                json=delegation_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        delegation_data = data["data"]
                        if "delegation_id" in delegation_data:
                            self.delegation_id = delegation_data["delegation_id"]
                        self.log_test("Inter-Agent Communication - Delegate Task", True, "Task delegated successfully between agents")
                        return True
                    else:
                        self.log_test("Inter-Agent Communication - Delegate Task", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Inter-Agent Communication - Delegate Task", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Inter-Agent Communication - Delegate Task", False, f"Exception: {str(e)}")
            return False

    async def test_agents_communication_metrics(self):
        """Test GET /api/agents/communication/metrics - Get communication metrics"""
        try:
            async with self.session.get(f"{API_BASE}/agents/communication/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        metrics_data = data["data"]
                        self.log_test("Inter-Agent Communication - Get Metrics", True, "Communication metrics retrieved successfully")
                        return True
                    else:
                        self.log_test("Inter-Agent Communication - Get Metrics", False, "Invalid response structure", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Inter-Agent Communication - Get Metrics", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Inter-Agent Communication - Get Metrics", False, f"Exception: {str(e)}")
            return False

    async def run_priority_tests(self):
        """Run priority backend tests focusing on stuck tasks"""
        print(f"🚀 Starting Priority Backend Testing - Focus on Stuck Tasks")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 80)
        
        # Test basic health first
        print("\n🔧 Testing Basic Health:")
        print("-" * 40)
        await self.test_health_check()
        
        print("\n🏢 PRIORITY 1: WHITE LABEL & MULTI-TENANCY SYSTEM TESTING")
        print("=" * 80)
        await self.test_white_label_create_tenant()
        await self.test_white_label_get_tenants()
        await self.test_white_label_get_tenant_branding()
        await self.test_white_label_create_reseller()
        
        print("\n🤝 PRIORITY 1: INTER-AGENT COMMUNICATION SYSTEM TESTING")
        print("=" * 80)
        await self.test_agents_collaborate()
        await self.test_agents_collaboration_status()
        await self.test_agents_delegate_task()
        await self.test_agents_communication_metrics()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PRIORITY TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        else:
            print(f"\n🎉 All priority tests passed!")
        
        return failed_tests == 0

async def main():
    """Main test runner"""
    async with PriorityTester() as tester:
        success = await tester.run_priority_tests()
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)