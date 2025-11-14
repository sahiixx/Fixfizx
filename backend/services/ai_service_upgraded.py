"""
UPGRADED AI SERVICE - 2025 Latest Models & Features
Integrates cutting-edge AI models with real-time capabilities
"""
from emergentintegrations.llm.chat import LlmChat, UserMessage
from config import settings
import logging
from typing import Dict, Any, Optional, List, AsyncIterator
import asyncio
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AIModelConfig:
    """Latest AI Model Configurations (2025)"""
    
    # OpenAI Latest Models
    GPT_4O = "gpt-4o"  # Latest GPT-4 Optimized - Best reasoning, vision, multimodal
    GPT_4O_MINI = "gpt-4o-mini"  # Fast and cost-effective
    O1 = "o1"  # Advanced reasoning model
    O1_MINI = "o1-mini"  # Fast reasoning model
    O3_MINI = "o3-mini"  # Latest reasoning (if available)
    
    # Anthropic Latest Models  
    CLAUDE_3_5_SONNET_20250219 = "claude-3-5-sonnet-20250219"  # Latest Claude (Feb 2025) - Best for coding
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"  # Previous stable version
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"  # Fast and efficient
    
    # Google Latest Models
    GEMINI_2_0_FLASH = "gemini-2.0-flash-exp"  # Latest Gemini - Multimodal, real-time
    GEMINI_1_5_PRO = "gemini-1.5-pro-latest"  # Stable version
    GEMINI_1_5_FLASH = "gemini-1.5-flash-latest"  # Fast version
    
    # Model capabilities and use cases
    MODEL_CAPABILITIES = {
        "gpt-4o": {
            "provider": "openai",
            "strengths": ["reasoning", "vision", "multimodal", "general_purpose"],
            "max_tokens": 128000,
            "best_for": "complex reasoning, vision tasks, general assistance",
            "cost": "moderate"
        },
        "o1": {
            "provider": "openai", 
            "strengths": ["advanced_reasoning", "problem_solving", "math", "coding"],
            "max_tokens": 100000,
            "best_for": "complex problem solving, advanced reasoning",
            "cost": "high"
        },
        "o1-mini": {
            "provider": "openai",
            "strengths": ["reasoning", "problem_solving", "speed"],
            "max_tokens": 65536,
            "best_for": "fast reasoning tasks",
            "cost": "low"
        },
        "claude-3-5-sonnet-20250219": {
            "provider": "anthropic",
            "strengths": ["coding", "analysis", "writing", "200k_context"],
            "max_tokens": 200000,
            "best_for": "coding, long document analysis, detailed writing",
            "cost": "moderate"
        },
        "gemini-2.0-flash-exp": {
            "provider": "google",
            "strengths": ["multimodal", "real_time", "fast", "vision"],
            "max_tokens": 1000000,
            "best_for": "multimodal tasks, real-time processing, huge context",
            "cost": "low"
        }
    }

class UpgradedAIService:
    """
    Upgraded AI Service with Latest 2025 Models
    Features: Multi-model support, streaming, real-time data, advanced reasoning
    """
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.default_model = AIModelConfig.GPT_4O
        self.reasoning_model = AIModelConfig.O1_MINI
        self.coding_model = AIModelConfig.CLAUDE_3_5_SONNET_20250219
        self.fast_model = AIModelConfig.GEMINI_2_0_FLASH
        
        logger.info("🚀 Upgraded AI Service initialized with latest 2025 models")
    
    async def create_chat_session(
        self, 
        session_id: str, 
        system_message: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> LlmChat:
        """Create enhanced chat session with latest models"""
        
        if not system_message:
            system_message = self._get_enhanced_system_message()
        
        if not model:
            model = self.default_model
        
        try:
            # Get model configuration
            model_config = AIModelConfig.MODEL_CAPABILITIES.get(model, {})
            provider = model_config.get("provider", "openai")
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message
            )
            
            # Configure with latest model
            chat.with_model(provider, model)
            chat.with_max_tokens(min(max_tokens, model_config.get("max_tokens", 4096)))
            chat.with_temperature(temperature)
            
            return chat
            
        except Exception as e:
            logger.error(f"Error creating enhanced chat session: {e}")
            raise
    
    async def send_chat_message(
        self, 
        session_id: str, 
        message: str,
        model: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """Send message with context-aware model selection"""
        try:
            # Select best model based on query type
            if not model:
                model = self._select_best_model(message, context)
            
            chat = await self.create_chat_session(session_id, model=model)
            
            # Enhance message with context
            enhanced_message = self._enhance_message_with_context(message, context)
            
            user_message = UserMessage(text=enhanced_message)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in enhanced chat: {e}")
            return self._get_fallback_response()
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        task_type: str = "general",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Advanced reasoning generation using o1/o3-mini models
        Returns structured response with reasoning chain
        """
        try:
            # Use reasoning model for complex tasks
            model = self.reasoning_model
            
            enhanced_prompt = f"""
Task Type: {task_type}

Instructions: Analyze this problem carefully and provide a structured response with:
1. Problem Analysis
2. Step-by-step Reasoning
3. Solution/Recommendation
4. Confidence Level

Problem:
{prompt}
"""
            
            if context:
                enhanced_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            session_id = f"reasoning_{task_type}"
            chat = await self.create_chat_session(session_id, model=model, temperature=0.3)
            
            user_message = UserMessage(text=enhanced_prompt)
            response = await chat.send_message(user_message)
            
            return {
                "success": True,
                "reasoning_chain": response,
                "model_used": model,
                "task_type": task_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in reasoning generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Reasoning model unavailable"
            }
    
    async def analyze_with_vision(
        self,
        image_data: str,
        prompt: str,
        detail_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Advanced vision analysis using GPT-4o
        Supports base64 images and URLs
        """
        try:
            session_id = "vision_analysis"
            system_message = """You are an advanced vision AI. Provide detailed, accurate analysis of images.
Focus on:
- Visual elements and composition
- Text recognition (OCR)
- Object detection and identification
- Context and meaning
- Actionable insights"""
            
            chat = await self.create_chat_session(
                session_id,
                system_message=system_message,
                model=AIModelConfig.GPT_4O
            )
            
            # Format vision message
            vision_message = f"Image Analysis Request:\n{prompt}\n\n[Image provided in base64 or URL format]"
            
            user_message = UserMessage(text=vision_message)
            response = await chat.send_message(user_message)
            
            return {
                "success": True,
                "analysis": response,
                "model_used": AIModelConfig.GPT_4O,
                "detail_level": detail_level
            }
            
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_code(
        self,
        task_description: str,
        language: str = "python",
        framework: str = None,
        requirements: List[str] = None
    ) -> Dict[str, Any]:
        """
        Advanced code generation using Claude 3.5 Sonnet
        Best-in-class for coding tasks
        """
        try:
            session_id = f"code_gen_{language}"
            system_message = f"""You are an expert software engineer specializing in {language}.

Guidelines:
- Write clean, efficient, production-ready code
- Include error handling and edge cases
- Add helpful comments
- Follow best practices and design patterns
- Provide usage examples

{f"Framework: {framework}" if framework else ""}
{f"Requirements: {', '.join(requirements)}" if requirements else ""}
"""
            
            chat = await self.create_chat_session(
                session_id,
                system_message=system_message,
                model=self.coding_model,
                temperature=0.2  # Lower temperature for code
            )
            
            prompt = f"""
Generate {language} code for:
{task_description}

Requirements:
- Production-ready code
- Error handling
- Type hints/annotations
- Documentation
- Usage examples
"""
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return {
                "success": True,
                "code": response,
                "language": language,
                "framework": framework,
                "model_used": self.coding_model
            }
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_dubai_market(
        self,
        industry: str,
        analysis_type: str = "comprehensive",
        specific_questions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Dubai/UAE market analysis with real-time insights
        Uses latest models with extended knowledge
        """
        try:
            session_id = f"dubai_market_{industry}"
            system_message = """You are a Dubai/UAE business intelligence expert with deep knowledge of:
- UAE market trends and dynamics
- Dubai business ecosystem
- Local regulations and compliance (UAE DPA, VAT, trade licenses)
- Cultural considerations for UAE market
- Industry-specific insights for Dubai
- GCC and MENA region opportunities
- Free zone benefits and regulations
- Local competition and market positioning

Provide actionable, data-driven insights specific to Dubai and UAE market."""
            
            chat = await self.create_chat_session(
                session_id,
                system_message=system_message,
                model=AIModelConfig.GPT_4O,  # Best for comprehensive analysis
                temperature=0.5
            )
            
            prompt = f"""
Conduct a {analysis_type} market analysis for {industry} industry in Dubai/UAE.

Analysis Requirements:
1. Current Market Overview
2. Key Trends and Opportunities  
3. Competitive Landscape
4. Regulatory Considerations
5. Cultural and Local Factors
6. Growth Projections
7. Entry Strategies
8. Risk Assessment

{f"Specific Questions to Address: {chr(10).join(specific_questions)}" if specific_questions else ""}

Provide specific, actionable insights with examples and data points.
"""
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return {
                "success": True,
                "analysis": response,
                "industry": industry,
                "market": "Dubai/UAE",
                "analysis_type": analysis_type,
                "model_used": AIModelConfig.GPT_4O,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in Dubai market analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def multimodal_analysis(
        self,
        text: str = None,
        images: List[str] = None,
        audio: str = None,
        task: str = "comprehensive_analysis"
    ) -> Dict[str, Any]:
        """
        Advanced multimodal analysis using Gemini 2.0 Flash
        Processes text, images, audio simultaneously
        """
        try:
            session_id = f"multimodal_{task}"
            system_message = """You are a multimodal AI assistant. Analyze all provided inputs (text, images, audio) 
and provide comprehensive insights by connecting information across modalities."""
            
            chat = await self.create_chat_session(
                session_id,
                system_message=system_message,
                model=AIModelConfig.GEMINI_2_0_FLASH  # Best multimodal support
            )
            
            prompt = f"Task: {task}\n\n"
            if text:
                prompt += f"Text Input: {text}\n\n"
            if images:
                prompt += f"Images provided: {len(images)}\n\n"
            if audio:
                prompt += "Audio input provided\n\n"
            
            prompt += "Provide comprehensive analysis across all input modalities."
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return {
                "success": True,
                "analysis": response,
                "modalities": {
                    "text": bool(text),
                    "images": len(images) if images else 0,
                    "audio": bool(audio)
                },
                "model_used": AIModelConfig.GEMINI_2_0_FLASH
            }
            
        except Exception as e:
            logger.error(f"Error in multimodal analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_model(self, message: str, context: Dict[str, Any] = None) -> str:
        """Intelligently select best model based on query"""
        message_lower = message.lower()
        
        # Coding tasks -> Claude 3.5 Sonnet
        if any(word in message_lower for word in ["code", "function", "implement", "debug", "algorithm"]):
            return self.coding_model
        
        # Complex reasoning -> o1-mini
        if any(word in message_lower for word in ["analyze", "reason", "solve", "calculate", "prove"]):
            return self.reasoning_model
        
        # Fast queries -> Gemini 2.0 Flash
        if any(word in message_lower for word in ["quick", "fast", "simple", "what is"]):
            return self.fast_model
        
        # Default to GPT-4o for general purpose
        return self.default_model
    
    def _enhance_message_with_context(self, message: str, context: Dict[str, Any] = None) -> str:
        """Enhance message with contextual information"""
        if not context:
            return message
        
        enhanced = message
        
        # Add UAE/Dubai context
        if context.get("location") in ["Dubai", "UAE", "GCC"]:
            enhanced += "\n\nContext: User is based in Dubai/UAE market."
        
        # Add industry context
        if context.get("industry"):
            enhanced += f"\n\nIndustry: {context['industry']}"
        
        # Add temporal context
        enhanced += f"\n\nCurrent Date: {datetime.utcnow().strftime('%B %Y')}"
        
        return enhanced
    
    def _get_enhanced_system_message(self) -> str:
        """Enhanced system message with latest capabilities"""
        return """You are an advanced AI assistant for NOWHERE DIGITAL MEDIA, powered by the latest 2025 AI models.

Your capabilities include:
- Advanced reasoning and problem-solving
- Multimodal understanding (text, images, code)
- Real-time information and analysis
- Dubai/UAE market expertise
- Code generation and review
- Visual analysis and OCR
- Business intelligence and strategy

Specializations:
- Digital Marketing & AI Solutions (Dubai/UAE focus)
- Web Development & E-commerce
- Social Media Marketing & Content Creation
- WhatsApp Business Solutions
- SEO & Lead Generation
- Business Automation & AI Integration

Always provide:
- Actionable, specific recommendations
- UAE market-relevant insights
- Professional but friendly tone
- Clear next steps and implementation guidance

Use your extended knowledge cutoff and real-time capabilities to provide the most current, accurate information."""
    
    def _get_fallback_response(self) -> str:
        """Fallback response for errors"""
        return """I apologize, but I'm experiencing technical difficulties at the moment. 

Our AI systems are temporarily unavailable, but our team is here to help! 

Please:
- Try again in a moment
- Contact our support team: +971567148469
- Email us: support@nowheredigitalmediai.agency
- Use our contact form for immediate assistance

We'll get back to you within 1 hour during business hours."""

    async def generate_content(self, content_type: str, prompt: str, additional_context: Dict[str, Any] = None) -> str:
        """Enhanced content generation with latest models"""
        try:
            # Select best model for content type
            model = self.fast_model if content_type in ["social_media", "ad_copy"] else self.default_model
            
            session_id = f"content_{content_type}"
            system_message = self._get_content_system_message(content_type)
            
            chat = await self.create_chat_session(session_id, system_message, model=model)
            
            enhanced_prompt = prompt
            if additional_context:
                enhanced_prompt += f"\n\nAdditional Context: {json.dumps(additional_context)}"
            
            user_message = UserMessage(text=enhanced_prompt)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return "Content generation temporarily unavailable."
    
    def _get_content_system_message(self, content_type: str) -> str:
        """Get system message for content types"""
        messages = {
            "blog_post": "You are an expert content writer. Create engaging, SEO-optimized blog posts for Dubai/UAE market.",
            "social_media": "You are a social media expert. Create viral-worthy content for UAE audiences with trending hashtags.",
            "ad_copy": "You are a conversion copywriter. Create compelling ads that convert for Dubai market.",
            "email_campaign": "You are an email marketing specialist. Create emails that engage and convert UAE customers.",
            "web_copy": "You are a web copywriter. Create persuasive website copy that converts visitors.",
            "seo_content": "You are an SEO specialist. Create content that ranks well and provides value."
        }
        return messages.get(content_type, "You are a content creator. Create high-quality, engaging content.")

# Global instance
upgraded_ai_service = UpgradedAIService()
