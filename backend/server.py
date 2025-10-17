from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import os
import json
import asyncio
import uuid

# Import our modules
from config import settings
from database import connect_to_db, close_db_connection, get_database
from models import *
from services.email_service import email_service
from services.ai_service import ai_service

# Import agent system
from agents.agent_orchestrator import orchestrator
from agents.sales_agent import SalesAgent

# Import Phase 2 components
from core.plugin_manager import plugin_manager
from blueprints.industry_templates import template_manager, IndustryType

# Import Phase 3 & 4 components
from core.white_label_manager import white_label_manager, TenantConfig
from core.inter_agent_communication import inter_agent_comm, AgentMessage, MessageType
from core.insights_engine import insights_engine, InsightType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NOWHERE Digital API",
    description="Comprehensive digital marketing agency platform API",
    version="1.0.0",
    debug=settings.debug
)

# Security
security = HTTPBearer()

# Create API router
api_router = APIRouter(prefix=settings.api_prefix)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Analytics middleware
class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Track page views
        if request.method == "GET":
            await self.track_page_view()
        
        response = await call_next(request)
        
        # Log API calls
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response
    
    async def track_page_view(self):
        try:
            db = get_database()
            today = date.today().isoformat()  # Convert to string
            
            # Update or create today's analytics
            await db.analytics.update_one(
                {"analytics_date": today},
                {"$inc": {"page_views": 1}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")

app.add_middleware(AnalyticsMiddleware)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow(), "service": "nowhere-digital-api"}

# Contact Form Endpoints
@api_router.post("/contact", response_model=StandardResponse)
async def create_contact_form(
    contact_data: ContactFormCreate,
    background_tasks: BackgroundTasks
):
    """Submit contact form"""
    try:
        db = get_database()
        
        # Create contact form entry
        contact_form = ContactForm(**contact_data.dict())
        
        # Save to database
        await db.contact_forms.insert_one(contact_form.dict())
        
        # Send emails in background
        background_tasks.add_task(
            email_service.send_contact_form_notification, 
            contact_form.dict()
        )
        background_tasks.add_task(
            email_service.send_contact_confirmation, 
            contact_form.dict()
        )
        
        # Track analytics
        await db.analytics.update_one(
            {"analytics_date": date.today().isoformat()},
            {"$inc": {"contact_forms": 1}},
            upsert=True
        )
        
        return StandardResponse(
            success=True,
            message="Contact form submitted successfully. We'll get back to you soon!",
            data={"id": contact_form.id}
        )
        
    except Exception as e:
        logger.error(f"Error creating contact form: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit contact form")

@api_router.get("/contact", response_model=List[ContactForm])
async def get_contact_forms(
    status: Optional[ContactStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get contact forms (admin only)"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        if status:
            query["status"] = status
        
        # Get contact forms
        cursor = db.contact_forms.find(query).skip(skip).limit(limit).sort("created_at", -1)
        contact_forms = await cursor.to_list(length=limit)
        
        return [ContactForm(**form) for form in contact_forms]
        
    except Exception as e:
        logger.error(f"Error getting contact forms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contact forms")

@api_router.put("/contact/{contact_id}", response_model=StandardResponse)
async def update_contact_form(
    contact_id: str,
    update_data: ContactFormUpdate
):
    """Update contact form status"""
    try:
        db = get_database()
        
        # Update contact form
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await db.contact_forms.update_one(
            {"id": contact_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contact form not found")
        
        return StandardResponse(
            success=True,
            message="Contact form updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact form: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contact form")

# AI Chat Endpoints
@api_router.post("/chat/session", response_model=StandardResponse)
async def create_chat_session(
    user_id: Optional[str] = None
):
    """Create a new chat session"""
    try:
        db = get_database()
        
        # Create chat session
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id
        )
        
        # Save to database
        await db.chat_sessions.insert_one(session.dict())
        
        # Track analytics
        await db.analytics.update_one(
            {"analytics_date": date.today().isoformat()},
            {"$inc": {"chat_sessions": 1}},
            upsert=True
        )
        
        return StandardResponse(
            success=True,
            message="Chat session created successfully",
            data={"session_id": session.session_id}
        )
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@api_router.post("/chat/message", response_model=StandardResponse)
async def send_chat_message(
    message_data: ChatMessageCreate
):
    """Send a message to AI chat"""
    try:
        db = get_database()
        
        # Get AI response
        ai_response = await ai_service.send_chat_message(
            message_data.session_id,
            message_data.message
        )
        
        # Create chat message
        chat_message = ChatMessage(
            session_id=message_data.session_id,
            user_id=message_data.user_id,
            message=message_data.message,
            response=ai_response
        )
        
        # Save to database
        await db.chat_messages.insert_one(chat_message.dict())
        
        # Update session
        await db.chat_sessions.update_one(
            {"session_id": message_data.session_id},
            {"$inc": {"total_messages": 1}}
        )
        
        return StandardResponse(
            success=True,
            message="Message sent successfully",
            data={"response": ai_response}
        )
        
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get chat history for a session"""
    try:
        db = get_database()
        
        # Get chat messages
        cursor = db.chat_messages.find(
            {"session_id": session_id}
        ).skip(skip).limit(limit).sort("created_at", 1)
        
        messages = await cursor.to_list(length=limit)
        
        return [ChatMessage(**msg) for msg in messages]
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

# Content Generation Endpoints
@api_router.post("/content/generate", response_model=StandardResponse)
async def generate_content(
    content_request: ContentGenerationCreate,
    background_tasks: BackgroundTasks
):
    """Generate content using AI"""
    try:
        db = get_database()
        
        # Generate content
        generated_content = await ai_service.generate_content(
            content_request.content_type,
            content_request.description,
            content_request.tone,
            content_request.target_audience
        )
        
        # Store content generation record
        content_record = ContentGeneration(**content_request.dict(), content=generated_content)
        await db.content_generation.insert_one(content_record.dict())
        
        return StandardResponse(
            success=True,
            message="Content generated successfully",
            data={"content": generated_content, "id": content_record.id}
        )
        
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

# AI Problem Analysis Endpoint
@api_router.post("/ai/analyze-problem", response_model=StandardResponse)
async def analyze_business_problem(
    problem_data: Dict[str, Any]
):
    """Analyze business problem and provide AI-powered solutions"""
    try:
        problem_description = problem_data.get("problem_description", "")
        industry = problem_data.get("industry", "general")
        budget_range = problem_data.get("budget_range", "")
        
        # Generate comprehensive analysis using multiple AI capabilities
        recommendations = await ai_service.generate_service_recommendations(
            f"Industry: {industry}, Problem: {problem_description}, Budget: {budget_range}"
        )
        
        # Get market trends for the industry
        market_analysis = await ai_service.analyze_market_trends(industry)
        
        # Generate strategy proposal
        business_info = {
            "business_name": "Client Business",
            "industry": industry,
            "target_market": "UAE",
            "challenges": problem_description,
            "goals": "Solve the described problem",
            "budget": budget_range
        }
        strategy_proposal = await ai_service.generate_strategy_proposal(business_info)
        
        return StandardResponse(
            success=True,
            message="Problem analysis completed successfully",
            data={
                "analysis": {
                    "problem_description": problem_description,
                    "industry": industry,
                    "ai_analysis": recommendations,
                    "market_insights": market_analysis,
                    "strategy_proposal": strategy_proposal,
                    "estimated_roi": "200-400%",
                    "implementation_time": "2-8 weeks",
                    "budget_range": budget_range or "AED 15,000 - 50,000/month",
                    "priority_level": "HIGH"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing business problem: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze business problem")

@api_router.get("/content/recommendations")
async def get_service_recommendations(
    business_info: str = Query(..., description="Business information and needs")
):
    """Get AI-powered service recommendations"""
    try:
        recommendations = await ai_service.generate_service_recommendations(business_info)
        
        return StandardResponse(
            success=True,
            message="Recommendations generated successfully",
            data={"recommendations": recommendations}
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

# Portfolio Endpoints
@api_router.post("/portfolio", response_model=StandardResponse)
async def create_portfolio_item(
    portfolio_data: PortfolioCreate
):
    """Create a new portfolio item"""
    try:
        db = get_database()
        
        # Create portfolio item
        portfolio_item = Portfolio(**portfolio_data.dict())
        
        # Save to database
        await db.portfolio.insert_one(portfolio_item.dict())
        
        return StandardResponse(
            success=True,
            message="Portfolio item created successfully",
            data={"id": portfolio_item.id}
        )
        
    except Exception as e:
        logger.error(f"Error creating portfolio item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portfolio item")

@api_router.get("/portfolio", response_model=List[Portfolio])
async def get_portfolio_items(
    service_type: Optional[ServiceType] = None,
    is_featured: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """Get portfolio items"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        if service_type:
            query["service_type"] = service_type
        if is_featured is not None:
            query["is_featured"] = is_featured
        
        # Get portfolio items
        cursor = db.portfolio.find(query).skip(skip).limit(limit).sort("created_at", -1)
        portfolio_items = await cursor.to_list(length=limit)
        
        return [Portfolio(**item) for item in portfolio_items]
        
    except Exception as e:
        logger.error(f"Error getting portfolio items: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio items")

@api_router.put("/portfolio/{portfolio_id}", response_model=StandardResponse)
async def update_portfolio_item(
    portfolio_id: str,
    update_data: PortfolioUpdate
):
    """Update portfolio item"""
    try:
        db = get_database()
        
        # Update portfolio item
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await db.portfolio.update_one(
            {"id": portfolio_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Portfolio item not found")
        
        return StandardResponse(
            success=True,
            message="Portfolio item updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating portfolio item: {e}")
        raise HTTPException(status_code=500, detail="Failed to update portfolio item")

# Services Endpoints
@api_router.get("/services", response_model=List[Service])
async def get_services(
    category: Optional[ServiceType] = None,
    is_active: Optional[bool] = True
):
    """Get services"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        if is_active is not None:
            query["is_active"] = is_active
        
        # Get services
        cursor = db.services.find(query).sort("created_at", -1)
        services = await cursor.to_list(length=100)
        
        return [Service(**service) for service in services]
        
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail="Failed to get services")

@api_router.post("/services", response_model=StandardResponse)
async def create_service(
    service_data: ServiceCreate
):
    """Create a new service"""
    try:
        db = get_database()
        
        # Create service
        service = Service(**service_data.dict())
        
        # Save to database
        await db.services.insert_one(service.dict())
        
        return StandardResponse(
            success=True,
            message="Service created successfully",
            data={"id": service.id}
        )
        
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        raise HTTPException(status_code=500, detail="Failed to create service")

# Booking Endpoints
@api_router.post("/bookings", response_model=StandardResponse)
async def create_booking(
    booking_data: BookingCreate,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None
):
    """Create a new booking"""
    try:
        db = get_database()
        
        # Create booking
        booking = Booking(
            user_id=user_id or str(uuid.uuid4()),
            **booking_data.dict()
        )
        
        # Save to database
        await db.bookings.insert_one(booking.dict())
        
        # Send confirmation email in background
        if user_id:
            user = await db.users.find_one({"id": user_id})
            if user:
                background_tasks.add_task(
                    email_service.send_booking_confirmation,
                    booking.dict(),
                    user["email"]
                )
        
        # Track analytics
        await db.analytics.update_one(
            {"analytics_date": date.today().isoformat()},
            {"$inc": {"bookings": 1}},
            upsert=True
        )
        
        return StandardResponse(
            success=True,
            message="Booking created successfully",
            data={"id": booking.id}
        )
        
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to create booking")

@api_router.get("/bookings", response_model=List[Booking])
async def get_bookings(
    user_id: Optional[str] = None,
    status: Optional[BookingStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get bookings"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        if user_id:
            query["user_id"] = user_id
        if status:
            query["status"] = status
        
        # Get bookings
        cursor = db.bookings.find(query).skip(skip).limit(limit).sort("created_at", -1)
        bookings = await cursor.to_list(length=limit)
        
        return [Booking(**booking) for booking in bookings]
        
    except Exception as e:
        logger.error(f"Error getting bookings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bookings")

# Testimonials Endpoints
@api_router.get("/testimonials", response_model=List[Testimonial])
async def get_testimonials(
    is_featured: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """Get testimonials"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        if is_featured is not None:
            query["is_featured"] = is_featured
        
        # Get testimonials
        cursor = db.testimonials.find(query).skip(skip).limit(limit).sort("rating", -1)
        testimonials = await cursor.to_list(length=limit)
        
        return [Testimonial(**testimonial) for testimonial in testimonials]
        
    except Exception as e:
        logger.error(f"Error getting testimonials: {e}")
        raise HTTPException(status_code=500, detail="Failed to get testimonials")

@api_router.post("/testimonials", response_model=StandardResponse)
async def create_testimonial(
    testimonial_data: TestimonialCreate
):
    """Create a new testimonial"""
    try:
        db = get_database()
        
        # Create testimonial
        testimonial = Testimonial(**testimonial_data.dict())
        
        # Save to database
        await db.testimonials.insert_one(testimonial.dict())
        
        return StandardResponse(
            success=True,
            message="Testimonial created successfully",
            data={"id": testimonial.id}
        )
        
    except Exception as e:
        logger.error(f"Error creating testimonial: {e}")
        raise HTTPException(status_code=500, detail="Failed to create testimonial")

# Analytics Endpoints
@api_router.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    try:
        db = get_database()
        
        # Get today's analytics
        today = date.today().isoformat()
        today_analytics = await db.analytics.find_one({"analytics_date": today})
        
        # Get total counts
        total_contacts = await db.contact_forms.count_documents({})
        total_bookings = await db.bookings.count_documents({})
        total_chat_sessions = await db.chat_sessions.count_documents({})
        total_portfolio = await db.portfolio.count_documents({})
        
        # Get recent activity
        recent_contacts = await db.contact_forms.count_documents({
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        summary = {
            "today": {
                "page_views": today_analytics.get("page_views", 0) if today_analytics else 0,
                "contact_forms": today_analytics.get("contact_forms", 0) if today_analytics else 0,
                "bookings": today_analytics.get("bookings", 0) if today_analytics else 0,
                "chat_sessions": today_analytics.get("chat_sessions", 0) if today_analytics else 0,
            },
            "total": {
                "contacts": total_contacts,
                "bookings": total_bookings,
                "chat_sessions": total_chat_sessions,
                "portfolio_items": total_portfolio,
            },
            "recent": {
                "contacts_today": recent_contacts,
            }
        }
        
        return StandardResponse(
            success=True,
            message="Analytics summary retrieved successfully",
            data=summary
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")

# ================================================================================================
# AGENT SYSTEM ENDPOINTS - AI-POWERED BUSINESS AUTOMATION
# ================================================================================================

# Agent Management Endpoints
@api_router.get("/agents/status", response_model=StandardResponse)
async def get_agents_status():
    """Get status of all agents in the system"""
    try:
        status = await orchestrator.get_agent_status()
        return StandardResponse(
            success=True,
            message="Agent status retrieved successfully",
            data=status
        )
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent status")

@api_router.get("/agents/{agent_id}/status", response_model=StandardResponse)
async def get_agent_status(agent_id: str):
    """Get status of specific agent"""
    try:
        status = await orchestrator.get_agent_status(agent_id)
        return StandardResponse(
            success=True,
            message="Agent status retrieved successfully",
            data=status
        )
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent status")

@api_router.get("/agents/metrics", response_model=StandardResponse)
async def get_orchestrator_metrics():
    """Get orchestrator performance metrics"""
    try:
        metrics = orchestrator.get_metrics()
        return StandardResponse(
            success=True,
            message="Orchestrator metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        logger.error(f"Error getting orchestrator metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

# Sales Agent Endpoints
@api_router.post("/agents/sales/qualify-lead", response_model=StandardResponse)
async def qualify_lead_with_sales_agent(lead_data: Dict[str, Any]):
    """Qualify a lead using the AI Sales Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'qualify_lead',
            'data': lead_data
        }, agent_type='sales')
        
        return StandardResponse(
            success=True,
            message="Lead qualification task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error submitting lead qualification task: {e}")
        raise HTTPException(status_code=500, detail="Failed to qualify lead")

@api_router.get("/agents/sales/pipeline", response_model=StandardResponse)
async def get_sales_pipeline_analysis():
    """Get sales pipeline analysis from Sales Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'analyze_sales_pipeline',
            'data': {}
        }, agent_type='sales')
        
        return StandardResponse(
            success=True,
            message="Pipeline analysis task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error getting pipeline analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze sales pipeline")

@api_router.post("/agents/sales/generate-proposal", response_model=StandardResponse)
async def generate_proposal_with_sales_agent(proposal_data: Dict[str, Any]):
    """Generate service proposal using AI Sales Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'generate_proposal',
            'data': proposal_data
        }, agent_type='sales')
        
        return StandardResponse(
            success=True,
            message="Proposal generation task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate proposal")

# Marketing Agent Endpoints
@api_router.post("/agents/marketing/create-campaign", response_model=StandardResponse)
async def create_marketing_campaign(campaign_data: Dict[str, Any]):
    """Create marketing campaign using AI Marketing Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'create_campaign',
            'data': campaign_data
        }, agent_type='marketing')
        
        return StandardResponse(
            success=True,
            message="Campaign creation task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to create campaign")

@api_router.post("/agents/marketing/optimize-campaign", response_model=StandardResponse)
async def optimize_marketing_campaign(optimization_data: Dict[str, Any]):
    """Optimize marketing campaign using AI Marketing Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'optimize_campaign',
            'data': optimization_data
        }, agent_type='marketing')
        
        return StandardResponse(
            success=True,
            message="Campaign optimization task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error optimizing campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize campaign")

# Content Agent Endpoints
@api_router.post("/agents/content/generate", response_model=StandardResponse)
async def generate_content_with_agent(content_data: Dict[str, Any]):
    """Generate content using AI Content Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'generate_content',
            'data': content_data
        }, agent_type='content')
        
        return StandardResponse(
            success=True,
            message="Content generation task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

# Analytics Agent Endpoints  
@api_router.post("/agents/analytics/analyze", response_model=StandardResponse)
async def analyze_data_with_agent(analysis_data: Dict[str, Any]):
    """Analyze data using AI Analytics Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'analyze_data',
            'data': analysis_data
        }, agent_type='analytics')
        
        return StandardResponse(
            success=True,
            message="Data analysis task submitted successfully", 
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze data")

# Task Management Endpoints
@api_router.get("/agents/tasks/history", response_model=StandardResponse)
async def get_task_history(
    agent_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100)
):
    """Get task execution history"""
    try:
        history = await orchestrator.get_task_history(agent_id, limit)
        return StandardResponse(
            success=True,
            message="Task history retrieved successfully",
            data={"tasks": history}
        )
    except Exception as e:
        logger.error(f"Error getting task history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task history")

# Agent Control Endpoints
@api_router.post("/agents/{agent_id}/pause", response_model=StandardResponse)
async def pause_agent(agent_id: str):
    """Pause a specific agent"""
    try:
        success = await orchestrator.pause_agent(agent_id)
        if success:
            return StandardResponse(
                success=True,
                message=f"Agent {agent_id} paused successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to pause agent")

@api_router.post("/agents/{agent_id}/resume", response_model=StandardResponse)
async def resume_agent(agent_id: str):
    """Resume a specific agent"""
    try:
        success = await orchestrator.resume_agent(agent_id)
        if success:
            return StandardResponse(
                success=True,
                message=f"Agent {agent_id} resumed successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume agent")

@api_router.post("/agents/{agent_id}/reset", response_model=StandardResponse)
async def reset_agent(agent_id: str):
    """Reset a specific agent"""
    try:
        success = await orchestrator.reset_agent(agent_id)
        if success:
            return StandardResponse(
                success=True,
                message=f"Agent {agent_id} reset successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset agent")

# Operations Agent Endpoints
@api_router.post("/agents/operations/automate-workflow", response_model=StandardResponse)
async def automate_workflow(workflow_data: Dict[str, Any]):
    """Automate business workflow using Operations Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'automate_workflow',
            'data': workflow_data
        }, agent_type='operations')
        
        return StandardResponse(
            success=True,
            message="Workflow automation task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error automating workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to automate workflow")

@api_router.post("/agents/operations/process-invoice", response_model=StandardResponse)
async def process_invoice_automation(invoice_data: Dict[str, Any]):
    """Process invoice using Operations Agent automation"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'process_invoice',
            'data': invoice_data
        }, agent_type='operations')
        
        return StandardResponse(
            success=True,
            message="Invoice processing task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error processing invoice: {e}")
        raise HTTPException(status_code=500, detail="Failed to process invoice")

@api_router.post("/agents/operations/onboard-client", response_model=StandardResponse)
async def automate_client_onboarding(client_data: Dict[str, Any]):
    """Automate client onboarding using Operations Agent"""
    try:
        task_id = await orchestrator.submit_task({
            'type': 'onboard_client',
            'data': client_data
        }, agent_type='operations')
        
        return StandardResponse(
            success=True,
            message="Client onboarding automation task submitted successfully",
            data={"task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Error automating client onboarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to automate client onboarding")

# ================================================================================================
# PLUGIN SYSTEM ENDPOINTS - EXTENSIBILITY & MARKETPLACE
# ================================================================================================

@api_router.get("/plugins/available", response_model=StandardResponse)
async def get_available_plugins():
    """Get all available plugins"""
    try:
        plugins_info = await plugin_manager.get_plugin_info()
        return StandardResponse(
            success=True,
            message="Available plugins retrieved successfully",
            data=plugins_info
        )
    except Exception as e:
        logger.error(f"Error getting available plugins: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available plugins")

@api_router.get("/plugins/{plugin_name}", response_model=StandardResponse)
async def get_plugin_info(plugin_name: str):
    """Get information about a specific plugin"""
    try:
        plugin_info = await plugin_manager.get_plugin_info(plugin_name)
        return StandardResponse(
            success=True,
            message="Plugin information retrieved successfully",
            data=plugin_info
        )
    except Exception as e:
        logger.error(f"Error getting plugin info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plugin information")

@api_router.post("/plugins/{plugin_name}/load", response_model=StandardResponse)
async def load_plugin(plugin_name: str, config: Dict[str, Any] = None):
    """Load a specific plugin"""
    try:
        success = await plugin_manager.load_plugin(plugin_name, config or {})
        if success:
            return StandardResponse(
                success=True,
                message=f"Plugin {plugin_name} loaded successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to load plugin")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading plugin: {e}")
        raise HTTPException(status_code=500, detail="Failed to load plugin")

@api_router.post("/plugins/{plugin_name}/unload", response_model=StandardResponse)
async def unload_plugin(plugin_name: str):
    """Unload a specific plugin"""
    try:
        success = await plugin_manager.unload_plugin(plugin_name)
        if success:
            return StandardResponse(
                success=True,
                message=f"Plugin {plugin_name} unloaded successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Plugin not loaded")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unloading plugin: {e}")
        raise HTTPException(status_code=500, detail="Failed to unload plugin")

@api_router.post("/plugins/create-template", response_model=StandardResponse)
async def create_plugin_template(plugin_info: Dict[str, Any]):
    """Create a new plugin template for development"""
    try:
        result = await plugin_manager.create_plugin_template(plugin_info)
        return StandardResponse(
            success=True,
            message="Plugin template created successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error creating plugin template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create plugin template")

@api_router.get("/plugins/marketplace", response_model=StandardResponse)
async def get_marketplace_plugins():
    """Get available plugins from marketplace"""
    try:
        marketplace_data = await plugin_manager.get_marketplace_plugins()
        return StandardResponse(
            success=True,
            message="Marketplace plugins retrieved successfully",
            data=marketplace_data
        )
    except Exception as e:
        logger.error(f"Error getting marketplace plugins: {e}")
        raise HTTPException(status_code=500, detail="Failed to get marketplace plugins")

# ================================================================================================
# INDUSTRY TEMPLATES & BLUEPRINTS ENDPOINTS 
# ================================================================================================

@api_router.get("/templates/industries", response_model=StandardResponse)
async def get_industry_templates():
    """Get all available industry templates"""
    try:
        templates_data = template_manager.get_all_templates()
        return StandardResponse(
            success=True,
            message="Industry templates retrieved successfully",
            data=templates_data
        )
    except Exception as e:
        logger.error(f"Error getting industry templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get industry templates")

@api_router.get("/templates/industries/{industry}", response_model=StandardResponse)
async def get_specific_industry_template(industry: str):
    """Get template for specific industry"""
    try:
        industry_enum = IndustryType(industry.lower())
        template_data = template_manager.get_template(industry_enum)
        
        if template_data:
            return StandardResponse(
                success=True,
                message=f"Template for {industry} retrieved successfully",
                data=template_data
            )
        else:
            raise HTTPException(status_code=404, detail="Industry template not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid industry type")
    except Exception as e:
        logger.error(f"Error getting industry template: {e}")
        raise HTTPException(status_code=500, detail="Failed to get industry template")

@api_router.post("/templates/deploy", response_model=StandardResponse)
async def deploy_industry_template(deployment_request: Dict[str, Any]):
    """Deploy an industry template configuration"""
    try:
        industry_str = deployment_request.get('industry')
        customizations = deployment_request.get('customizations', {})
        
        industry_enum = IndustryType(industry_str.lower())
        deployment_config = template_manager.generate_deployment_config(industry_enum, customizations)
        
        return StandardResponse(
            success=True,
            message=f"Deployment configuration generated for {industry_str}",
            data=deployment_config
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid industry type")
    except Exception as e:
        logger.error(f"Error deploying template: {e}")
        raise HTTPException(status_code=500, detail="Failed to deploy template")

@api_router.post("/templates/validate", response_model=StandardResponse)
async def validate_template_compatibility(validation_request: Dict[str, Any]):
    """Validate template compatibility with requirements"""
    try:
        industry_str = validation_request.get('industry')
        requirements = validation_request.get('requirements', {})
        
        industry_enum = IndustryType(industry_str.lower())
        validation_result = template_manager.validate_template_compatibility(industry_enum, requirements)
        
        return StandardResponse(
            success=True,
            message="Template compatibility validation completed",
            data=validation_result
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid industry type")
    except Exception as e:
        logger.error(f"Error validating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate template")

@api_router.post("/templates/custom", response_model=StandardResponse)
async def create_custom_template(template_data: Dict[str, Any]):
    """Create a custom industry template"""
    try:
        result = template_manager.create_custom_template(template_data)
        return StandardResponse(
            success=True,
            message="Custom template created successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error creating custom template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create custom template")

# ================================================================================================
# PHASE 3 & 4 - WHITE LABEL, INTER-AGENT COMMUNICATION & SMART INSIGHTS
# ================================================================================================

# White Label & Multi-Tenancy Endpoints
@api_router.post("/white-label/create-tenant", response_model=StandardResponse)
async def create_white_label_tenant(tenant_data: Dict[str, Any]):
    """Create a new white-label tenant configuration"""
    try:
        result = await white_label_manager.create_tenant(tenant_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="White-label tenant created successfully",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating white-label tenant: {e}")
        raise HTTPException(status_code=500, detail="Failed to create tenant")

@api_router.get("/white-label/tenants", response_model=StandardResponse)
async def get_all_tenants(status: Optional[str] = None):
    """Get list of all white-label tenants"""
    try:
        tenants = await white_label_manager.get_all_tenants(status)
        return StandardResponse(
            success=True,
            message="Tenants retrieved successfully",
            data={"tenants": tenants, "total": len(tenants)}
        )
    except Exception as e:
        logger.error(f"Error getting tenants: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tenants")

@api_router.get("/white-label/tenant/{tenant_id}/branding", response_model=StandardResponse)
async def get_tenant_branding(tenant_id: str):
    """Get tenant-specific branding configuration"""
    try:
        branding = await white_label_manager.get_tenant_branding(tenant_id)
        return StandardResponse(
            success=True,
            message="Tenant branding retrieved successfully",
            data=branding
        )
    except Exception as e:
        logger.error(f"Error getting tenant branding: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tenant branding")

@api_router.post("/white-label/create-reseller", response_model=StandardResponse)
async def create_reseller_package(reseller_data: Dict[str, Any]):
    """Create a reseller package with custom branding"""
    try:
        result = await white_label_manager.create_reseller_package(reseller_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="Reseller package created successfully",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reseller package: {e}")
        raise HTTPException(status_code=500, detail="Failed to create reseller package")

# Inter-Agent Communication Endpoints
@api_router.post("/agents/collaborate", response_model=StandardResponse)
async def initiate_agent_collaboration(collaboration_request: Dict[str, Any]):
    """Initiate a collaborative task between multiple agents"""
    try:
        collaboration_id = await inter_agent_comm.request_collaboration(collaboration_request)
        
        if not collaboration_id:
            raise HTTPException(status_code=400, detail="Failed to initiate collaboration")
        
        return StandardResponse(
            success=True,
            message="Agent collaboration initiated successfully",
            data={"collaboration_id": collaboration_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate collaboration")

@api_router.get("/agents/collaborate/{collaboration_id}", response_model=StandardResponse)
async def get_collaboration_status(collaboration_id: str):
    """Get status of an active collaboration"""
    try:
        status = await inter_agent_comm.get_collaboration_status(collaboration_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        return StandardResponse(
            success=True,
            message="Collaboration status retrieved successfully",
            data=status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collaboration status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collaboration status")

@api_router.post("/agents/delegate-task", response_model=StandardResponse)
async def delegate_task_between_agents(delegation_request: Dict[str, Any]):
    """Delegate a task from one agent to another"""
    try:
        from_agent_id = delegation_request.get('from_agent_id')
        to_agent_id = delegation_request.get('to_agent_id')
        task_data = delegation_request.get('task_data', {})
        
        message_id = await inter_agent_comm.delegate_task(from_agent_id, to_agent_id, task_data)
        
        if not message_id:
            raise HTTPException(status_code=400, detail="Failed to delegate task")
        
        return StandardResponse(
            success=True,
            message="Task delegated successfully",
            data={"delegation_id": message_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error delegating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delegate task")

@api_router.get("/agents/communication/metrics", response_model=StandardResponse)
async def get_communication_metrics():
    """Get inter-agent communication system metrics"""
    try:
        metrics = inter_agent_comm.get_metrics()
        return StandardResponse(
            success=True,
            message="Communication metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        logger.error(f"Error getting communication metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get communication metrics")

# Smart Insights & Analytics Endpoints
@api_router.post("/insights/analyze-performance", response_model=StandardResponse)
async def analyze_system_performance(performance_data: Dict[str, Any]):
    """Analyze system performance and generate AI insights"""
    try:
        insights = await insights_engine.analyze_system_performance(performance_data)
        
        return StandardResponse(
            success=True,
            message="Performance analysis completed successfully",
            data={
                "insights_generated": len(insights),
                "insights": [
                    {
                        "id": insight.insight_id,
                        "type": insight.type.value,
                        "severity": insight.severity.value,
                        "title": insight.title,
                        "description": insight.description,
                        "recommendations": insight.recommendations,
                        "confidence": insight.confidence_score,
                        "impact": insight.impact_estimate
                    }
                    for insight in insights
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error analyzing performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze performance")

@api_router.post("/insights/analyze-agent/{agent_id}", response_model=StandardResponse)
async def analyze_agent_performance(agent_id: str, agent_metrics: Dict[str, Any]):
    """Analyze individual agent performance and generate improvement suggestions"""
    try:
        insights = await insights_engine.analyze_agent_performance(agent_id, agent_metrics)
        
        return StandardResponse(
            success=True,
            message="Agent performance analysis completed successfully",
            data={
                "agent_id": agent_id,
                "insights_generated": len(insights),
                "insights": [
                    {
                        "id": insight.insight_id,
                        "type": insight.type.value,
                        "severity": insight.severity.value,
                        "title": insight.title,
                        "description": insight.description,
                        "recommendations": insight.recommendations,
                        "confidence": insight.confidence_score,
                        "impact": insight.impact_estimate
                    }
                    for insight in insights
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error analyzing agent performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze agent performance")

@api_router.post("/insights/detect-anomalies", response_model=StandardResponse)
async def detect_business_anomalies(business_data: Dict[str, Any]):
    """Detect anomalies in business metrics and operations"""
    try:
        insights = await insights_engine.detect_business_anomalies(business_data)
        
        return StandardResponse(
            success=True,
            message="Anomaly detection completed successfully",
            data={
                "anomalies_detected": len(insights),
                "insights": [
                    {
                        "id": insight.insight_id,
                        "type": insight.type.value,
                        "severity": insight.severity.value,
                        "title": insight.title,
                        "description": insight.description,
                        "recommendations": insight.recommendations,
                        "confidence": insight.confidence_score
                    }
                    for insight in insights
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")

@api_router.post("/insights/optimization-recommendations", response_model=StandardResponse)
async def generate_optimization_recommendations(context_data: Dict[str, Any]):
    """Generate AI-powered optimization recommendations"""
    try:
        insights = await insights_engine.generate_optimization_recommendations(context_data)
        
        return StandardResponse(
            success=True,
            message="Optimization recommendations generated successfully",
            data={
                "recommendations_generated": len(insights),
                "insights": [
                    {
                        "id": insight.insight_id,
                        "type": insight.type.value,
                        "severity": insight.severity.value,
                        "title": insight.title,
                        "description": insight.description,
                        "recommendations": insight.recommendations,
                        "confidence": insight.confidence_score,
                        "impact": insight.impact_estimate
                    }
                    for insight in insights
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error generating optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@api_router.get("/insights/summary", response_model=StandardResponse)
async def get_insights_summary(days: int = Query(7, ge=1, le=90)):
    """Get summary of recent insights and analytics"""
    try:
        summary = await insights_engine.get_insights_summary(days)
        return StandardResponse(
            success=True,
            message="Insights summary retrieved successfully",
            data=summary
        )
    except Exception as e:
        logger.error(f"Error getting insights summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights summary")

# Include the API router
app.include_router(api_router)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and agent orchestrator on startup"""
    await connect_to_db()
    
    # Initialize agent orchestrator
    await orchestrator.initialize()
    logger.info("Agent orchestrator initialized")
    
    # Initialize Phase 3 & 4 systems
    inter_agent_comm.orchestrator = orchestrator  # Set orchestrator reference
    await inter_agent_comm.start()
    logger.info("Inter-agent communication system started")
    
    logger.info("NOWHERE Digital API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection and shutdown all systems"""
    await inter_agent_comm.stop()
    await orchestrator.shutdown()
    await close_db_connection()
    logger.info("NOWHERE Digital API shutdown")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "NOWHERE Digital API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
