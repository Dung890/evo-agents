from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
import os
from pathlib import Path
from src.agents.orchestrator import AgentOrchestrator
from src.auth.linkedin_auth import require_linkedin_auth, linkedin_auth
from src.api.user_onboarding import (
    ComprehensiveUserProfile, QuickStartProfile, UserOnboardingService,
    CAREER_GOALS, SKILL_OPTIONS, DEPARTMENT_OPTIONS, INDUSTRY_OPTIONS
)

# Initialize FastAPI app
app = FastAPI(
    title="UTD Career Guidance AI System",
    description="Autonomous agent system for data-driven career guidance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"  # Allow all origins for production CloudFront deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent orchestrator
orchestrator = AgentOrchestrator()

# Initialize user onboarding service
onboarding_service = UserOnboardingService()

# Serve static frontend files if they exist (for integrated deployment)
frontend_dist_path = Path(__file__).parent.parent.parent / "frontend_dist"
if frontend_dist_path.exists() and frontend_dist_path.is_dir():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")

# Define request models
class CareerQueryRequest(BaseModel):
    query: str
    location: Optional[str] = "Dallas, TX"

class CareerQueryResponse(BaseModel):
    success: bool
    career_goal: Optional[str] = None
    job_market: Optional[Dict] = None
    course_recommendations: Optional[list] = None
    insights: Optional[Dict] = None
    next_steps: Optional[list] = None
    error: Optional[str] = None
    processing_time_seconds: Optional[float] = None


class JobMarketRequest(BaseModel):
    job_title: str
    location: Optional[str] = ""
    limit: Optional[int] = 10

class CourseSearchRequest(BaseModel):
    search_term: Optional[str] = None
    department: Optional[str] = None
    skill: Optional[str] = None

class ProjectRecommendationRequest(BaseModel):
    career_goal: str
    current_skills: Optional[List[str]] = []
    target_skills: Optional[List[str]] = []
    skill_level: Optional[str] = "intermediate"
    recommended_courses: Optional[List[Dict[str, Any]]] = []

class ProjectRequest(BaseModel):
    career_goal: str
    technical_skills: Optional[List[str]] = []
    target_skills: Optional[List[str]] = []
    courses: Optional[List[Dict[str, Any]]] = []
    experience_level: Optional[str] = "beginner"

# API endpoints
@app.get("/")
async def root():
    """Welcome to the UTD Career Guidance AI System API"""
    return {
        "service": "UTD Career Guidance AI",
        "status": "operational",
        "version": "1.0.0",
        "linkedin_auth_required": True,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            # Authentication
            "/auth/linkedin",
            "/auth/status", 
            "/auth/logout",
            
            # Career Guidance
            "/api/career-guidance",
            "/api/onboarding/quick-start",
            "/api/onboarding/comprehensive",
            "/api/onboarding/options",
            "/api/onboarding/suggest-careers",
            "/api/onboarding/validate-profile",
            "/api/onboarding/smart-questions/{career_goal}",
            
            # Job Market & Courses
            "/job-market",
            "/course-search",
            "/api/courses/all",
            
            # Projects & Agents
            "/api/project-recommendations",
            "/api/agents/status",
            "/agent-capabilities",
            
            # System
            "/health",
            "/api/stats",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "bedrock": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/auth/linkedin")
async def authenticate_linkedin():
    """Authenticate with LinkedIn - required before using the system"""
    try:
        success = await require_linkedin_auth()
        if success:
            return {
                "success": True,
                "message": "LinkedIn authentication successful",
                "status": "authenticated"
            }
        else:
            return {
                "success": False,
                "message": "LinkedIn authentication failed",
                "status": "not_authenticated"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.get("/auth/status")
async def get_auth_status():
    """Get current LinkedIn authentication status"""
    try:
        status = linkedin_auth.get_auth_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

@app.post("/auth/logout")
async def logout_linkedin():
    """Logout and clear LinkedIn session"""
    try:
        success = linkedin_auth.logout()
        return {
            "success": success,
            "message": "LinkedIn session cleared" if success else "Logout failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")

@app.post("/api/career-guidance", response_model=CareerQueryResponse)
async def get_career_guidance(request: CareerQueryRequest):
    """
    Main endpoint: Process career query and return guidance.
    Requires LinkedIn authentication for real job market data.
    
    Example request:
    {
        "query": "I want to become a data scientist",
        "location": "Dallas, TX"
    }
    """
    # Check LinkedIn authentication first
    if not linkedin_auth.is_authenticated():
        raise HTTPException(
            status_code=401, 
            detail="LinkedIn authentication required. Please authenticate first using /auth/linkedin"
        )
    
    start_time = datetime.utcnow()
    
    try:
        # Call orchestrator agent
        result = await orchestrator.process_request({
            "request_type": "career_advice",
            "career_goal": request.query,
            "location": request.location
        })
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        return CareerQueryResponse(
            success=True,
            career_goal=result.get('career_goal'),
            job_market=result.get('job_market_analysis'),
            course_recommendations=result.get('course_recommendations'),
            insights=result.get('learning_path'),
            next_steps=result.get('project_recommendations'),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process career query: {str(e)}"
        )


@app.post("/job-market")
async def get_job_market_analysis(request: JobMarketRequest):
    """Get job market analysis for a specific job title - requires LinkedIn authentication"""
    # Check LinkedIn authentication first
    if not linkedin_auth.is_authenticated():
        raise HTTPException(
            status_code=401, 
            detail="LinkedIn authentication required for real job market data. Please authenticate first using /auth/linkedin"
        )
    
    try:
        orchestrator_request = {
            "request_type": "job_market_analysis",
            **request.dict()
        }
        response = await orchestrator.process_request(orchestrator_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/course-search")
async def search_courses(request: CourseSearchRequest):
    """Search for UTD courses by term, department, or skill"""
    try:
        if not request.search_term and not request.department and not request.skill:
            raise HTTPException(status_code=400, detail="At least one search parameter is required")

        orchestrator_request = {
            "request_type": "course_search",
            **request.dict()
        }
        response = await orchestrator.process_request(orchestrator_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/courses/all")
async def get_all_courses():
    """Get all available UTD courses from the catalog"""
    try:
        orchestrator_request = {
            "request_type": "get_all_courses"
        }
        response = await orchestrator.process_request(orchestrator_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courses: {str(e)}")

@app.post("/api/project-recommendations")
async def get_project_recommendations(request: ProjectRecommendationRequest):
    """
    Get personalized project recommendations to build portfolio and skills
    
    **Why Projects Matter:**
    - Create tangible portfolio pieces for job applications
    - Demonstrate practical skills to employers
    - Reinforce theoretical knowledge from courses
    - Show initiative and self-directed learning
    
    **Returns**: 3-5 project ideas with difficulty levels, timelines, and skill mappings
    
    **Example Request Body:**
    ```json
    {
        "career_goal": "Data Scientist",
        "current_skills": ["Python", "Statistics"],
        "target_skills": ["Machine Learning", "SQL"],
        "skill_level": "intermediate"
    }
    ```
    """
    try:
        # Validate required fields
        if not request.career_goal or not request.career_goal.strip():
            raise HTTPException(
                status_code=400, 
                detail="career_goal is required and cannot be empty. Please provide a valid career goal like 'Data Scientist', 'Software Engineer', etc."
            )
        
        # Ensure lists are not None
        current_skills = request.current_skills or []
        target_skills = request.target_skills or []
        recommended_courses = request.recommended_courses or []
        
        orchestrator_request = {
            "request_type": "project_recommendations",
            "career_goal": request.career_goal.strip(),
            "current_skills": current_skills,
            "target_skills": target_skills,
            "skill_level": request.skill_level or "intermediate",
            "recommended_courses": recommended_courses
        }
        
        result = await orchestrator.process_request(orchestrator_request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating project recommendations: {str(e)}")

@app.get("/api/agents/status")
async def get_agent_status():
    """Check status of all agents"""
    return {
        "career_matching_agent": "operational",
        "job_market_agent": "operational", 
        "course_catalog_agent": "operational",
        "project_advisor_agent": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

# =============================================================================
# STREAMLINED USER ONBOARDING ENDPOINTS
# =============================================================================

@app.get("/api/onboarding/options")
async def get_onboarding_options():
    """
    Get all available options for user onboarding forms
    
    Returns predefined options for dropdowns, multi-selects, etc.
    """
    return {
        "career_goals": CAREER_GOALS,
        "skills": SKILL_OPTIONS,
        "departments": DEPARTMENT_OPTIONS,
        "industries": INDUSTRY_OPTIONS,
        "academic_years": ["freshman", "sophomore", "junior", "senior", "graduate"],
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "learning_styles": ["hands-on", "theoretical", "mixed", "project-based"],
        "time_commitments": ["light", "moderate", "intensive"],
        "company_sizes": ["startup", "mid-size", "large", "enterprise"]
    }

@app.post("/api/onboarding/quick-start")
async def quick_start_career_guidance(profile: QuickStartProfile):
    """
    Quick start career guidance with minimal information
    
    Perfect for users who want to get started immediately with just:
    - Career goal
    - Current skills (optional)
    - Academic year (optional)
    - Location (optional)
    """
    try:
        # Convert quick start profile to full career advice request
        career_request = {
            "request_type": "career_advice",
            "career_goal": profile.career_goal,
            "location": profile.location,
            "current_skills": profile.current_skills,
            "completed_courses": [],  # Will be inferred
            "experience_level": "intermediate"  # Default
        }
        
        # Get comprehensive career guidance
        result = await orchestrator.process_request(career_request)
        
        # Add quick start context
        result["quick_start"] = True
        result["profile_completeness"] = "minimal"
        result["next_steps"] = [
            "Review your personalized course recommendations",
            "Check the job market insights for your career goal",
            "Consider completing your profile for more personalized advice"
        ]
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick start failed: {str(e)}")

@app.post("/api/onboarding/comprehensive")
async def comprehensive_career_guidance(profile: ComprehensiveUserProfile):
    """
    Comprehensive career guidance with full user profile
    
    Uses all available information for highly personalized recommendations
    """
    try:
        # Validate profile completeness
        validation = onboarding_service.validate_profile(profile)
        
        # Convert comprehensive profile to career advice request
        career_request = {
            "request_type": "career_advice",
            "career_goal": profile.career_goal,
            "location": profile.preferred_location,
            "current_skills": profile.current_skills,
            "completed_courses": profile.completed_courses,
            "experience_level": profile.skill_level.value
        }
        
        # Get comprehensive career guidance
        result = await orchestrator.process_request(career_request)
        
        # Add comprehensive context and validation results
        result["profile_validation"] = validation.dict()
        result["comprehensive"] = True
        result["personalization_level"] = "high"
        
        # Add smart follow-up questions if profile is incomplete
        if not validation.is_valid or validation.completeness_score < 80:
            result["smart_questions"] = onboarding_service.generate_smart_questions(profile)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive guidance failed: {str(e)}")

@app.post("/api/onboarding/suggest-careers")
async def suggest_career_goals(major: str, interests: List[str] = []):
    """
    Suggest career goals based on major and interests
    
    Helps users discover relevant career paths
    """
    try:
        suggestions = onboarding_service.suggest_career_goals(major, interests)
        return {
            "suggestions": suggestions,
            "major": major,
            "interests": interests,
            "total_suggestions": len(suggestions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Career suggestion failed: {str(e)}")

@app.post("/api/onboarding/validate-profile")
async def validate_user_profile(profile: ComprehensiveUserProfile):
    """
    Validate user profile and get recommendations for improvement
    """
    try:
        validation = onboarding_service.validate_profile(profile)
        return validation.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile validation failed: {str(e)}")

@app.get("/api/onboarding/smart-questions/{career_goal}")
async def get_smart_questions(career_goal: str):
    """
    Get smart follow-up questions based on career goal
    
    Helps guide users through profile completion
    """
    try:
        # Create a minimal profile with just the career goal
        profile = ComprehensiveUserProfile(career_goal=career_goal)
        questions = onboarding_service.generate_smart_questions(profile)
        
        return {
            "career_goal": career_goal,
            "questions": questions,
            "total_questions": len(questions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart questions failed: {str(e)}")

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics for demo"""
    # In production, fetch from DynamoDB
    return {
        "total_queries_processed": 0,
        "total_jobs_scraped": 0,
        "total_courses_analyzed": 0,
        "avg_response_time_seconds": 0,
        "last_job_scrape": None,
        "last_catalog_update": None
    }

@app.get("/agent-capabilities")
async def get_agent_capabilities():
    """Get capabilities of all agents in the system"""
    return orchestrator.get_agent_capabilities()

# Serve frontend index.html for integrated deployment
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve the frontend application for integrated deployment"""
    from fastapi.responses import FileResponse

    frontend_dist_path = Path(__file__).parent.parent.parent / "frontend_dist"
    if not frontend_dist_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")

    # Serve index.html for all non-API routes (SPA routing)
    index_path = frontend_dist_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend index.html not found")

if __name__ == "__main__":
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
