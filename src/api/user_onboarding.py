"""
User Onboarding Module
Collects crucial information upfront for smooth user experience
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"

class AcademicYear(str, Enum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    GRADUATE = "graduate"

class ComprehensiveUserProfile(BaseModel):
    """
    Comprehensive user profile that collects all crucial information upfront
    for minimal interaction and smooth user experience
    """
    
    # Core Career Information
    career_goal: str = Field(..., description="Primary career goal (e.g., 'Data Scientist', 'Software Engineer')")
    alternative_careers: Optional[List[str]] = Field(default=[], description="Alternative career interests")
    
    # Location & Market
    preferred_location: str = Field(default="Dallas, TX", description="Preferred job location")
    remote_work_interest: bool = Field(default=True, description="Open to remote work")
    
    # Academic Information
    academic_year: AcademicYear = Field(default=AcademicYear.SOPHOMORE, description="Current academic year")
    major: Optional[str] = Field(default=None, description="Primary major/field of study")
    minor: Optional[str] = Field(default=None, description="Minor or secondary field")
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0, description="Current GPA (optional)")
    
    # Skills Assessment
    current_skills: List[str] = Field(default=[], description="Skills you currently have")
    target_skills: List[str] = Field(default=[], description="Skills you want to develop")
    skill_level: ExperienceLevel = Field(default=ExperienceLevel.INTERMEDIATE, description="Overall skill level")
    
    # Course History
    completed_courses: List[str] = Field(default=[], description="Courses you've already taken")
    courses_in_progress: List[str] = Field(default=[], description="Courses you're currently taking")
    preferred_departments: List[str] = Field(default=[], description="Departments you're interested in")
    
    # Career Preferences
    salary_expectations: Optional[str] = Field(default=None, description="Salary range expectations")
    company_size_preference: Optional[str] = Field(default=None, description="Startup, mid-size, or large company preference")
    industry_interests: List[str] = Field(default=[], description="Industries of interest")
    
    # Learning Preferences
    learning_style: Optional[str] = Field(default="hands-on", description="Preferred learning style")
    time_commitment: Optional[str] = Field(default="moderate", description="Time available for skill development")
    project_preferences: List[str] = Field(default=[], description="Types of projects you're interested in")
    
    # Goals & Timeline
    graduation_timeline: Optional[str] = Field(default=None, description="Expected graduation timeline")
    career_timeline: Optional[str] = Field(default=None, description="When you want to start your career")
    internship_interest: bool = Field(default=True, description="Interested in internships")
    
    # Additional Context
    special_circumstances: Optional[str] = Field(default=None, description="Any special circumstances or constraints")
    previous_experience: Optional[str] = Field(default=None, description="Previous work/internship experience")
    portfolio_items: List[str] = Field(default=[], description="Existing portfolio projects")

class QuickStartProfile(BaseModel):
    """
    Minimal profile for users who want to get started quickly
    """
    career_goal: str = Field(..., description="What career do you want to pursue?")
    current_skills: List[str] = Field(default=[], description="What skills do you already have?")
    academic_year: AcademicYear = Field(default=AcademicYear.SOPHOMORE, description="What year are you?")
    location: str = Field(default="Dallas, TX", description="Where do you want to work?")

class ProfileValidationResult(BaseModel):
    """Result of profile validation"""
    is_valid: bool
    missing_fields: List[str] = []
    recommendations: List[str] = []
    completeness_score: float = 0.0

class UserOnboardingService:
    """
    Service to handle user onboarding and profile creation
    """
    
    def __init__(self):
        self.required_core_fields = ["career_goal"]
        self.recommended_fields = [
            "current_skills", "target_skills", "academic_year", 
            "preferred_location", "completed_courses"
        ]
    
    def validate_profile(self, profile: ComprehensiveUserProfile) -> ProfileValidationResult:
        """
        Validate user profile completeness and provide recommendations
        """
        missing_fields = []
        recommendations = []
        
        # Check required fields
        if not profile.career_goal or not profile.career_goal.strip():
            missing_fields.append("career_goal")
        
        # Check recommended fields
        if not profile.current_skills:
            recommendations.append("Add your current skills for better course recommendations")
        
        if not profile.target_skills:
            recommendations.append("Specify target skills to develop for your career goal")
        
        if not profile.completed_courses:
            recommendations.append("List completed courses to avoid duplicate recommendations")
        
        if not profile.preferred_location:
            recommendations.append("Set your preferred work location for job market analysis")
        
        # Calculate completeness score
        total_fields = len(self.required_core_fields) + len(self.recommended_fields)
        filled_fields = len([f for f in self.required_core_fields if getattr(profile, f, None)])
        filled_fields += len([f for f in self.recommended_fields if getattr(profile, f, None) and getattr(profile, f)])
        
        completeness_score = (filled_fields / total_fields) * 100
        
        is_valid = len(missing_fields) == 0 and completeness_score >= 50
        
        return ProfileValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            recommendations=recommendations,
            completeness_score=completeness_score
        )
    
    def create_quick_start_profile(self, career_goal: str, **kwargs) -> QuickStartProfile:
        """
        Create a minimal profile for quick start
        """
        return QuickStartProfile(
            career_goal=career_goal,
            current_skills=kwargs.get("current_skills", []),
            academic_year=kwargs.get("academic_year", AcademicYear.SOPHOMORE),
            location=kwargs.get("location", "Dallas, TX")
        )
    
    def suggest_career_goals(self, major: str, interests: List[str]) -> List[str]:
        """
        Suggest career goals based on major and interests
        """
        career_suggestions = {
            "computer science": [
                "Software Engineer", "Data Scientist", "DevOps Engineer", 
                "Cybersecurity Analyst", "Product Manager", "Full Stack Developer"
            ],
            "data science": [
                "Data Scientist", "Data Analyst", "Machine Learning Engineer",
                "Business Intelligence Analyst", "Data Engineer", "Research Scientist"
            ],
            "business": [
                "Business Analyst", "Product Manager", "Management Consultant",
                "Investment Analyst", "Marketing Manager", "Operations Manager"
            ],
            "engineering": [
                "Software Engineer", "Systems Engineer", "DevOps Engineer",
                "Product Manager", "Technical Consultant", "Engineering Manager"
            ],
            "neuroscience": [
                "Research Scientist", "Neurobiologist", "Data Scientist",
                "Clinical Research Coordinator", "Biotech Analyst", "AI Researcher"
            ]
        }
        
        major_lower = major.lower()
        suggestions = []
        
        for field, careers in career_suggestions.items():
            if field in major_lower:
                suggestions.extend(careers)
        
        # Add general suggestions based on interests
        if "data" in interests or "analytics" in interests:
            suggestions.extend(["Data Scientist", "Data Analyst", "Business Intelligence Analyst"])
        
        if "software" in interests or "programming" in interests:
            suggestions.extend(["Software Engineer", "Full Stack Developer", "DevOps Engineer"])
        
        if "business" in interests or "management" in interests:
            suggestions.extend(["Product Manager", "Business Analyst", "Management Consultant"])
        
        return list(set(suggestions))[:8]  # Return top 8 unique suggestions
    
    def generate_smart_questions(self, profile: ComprehensiveUserProfile) -> List[Dict[str, str]]:
        """
        Generate smart follow-up questions based on current profile
        """
        questions = []
        
        if not profile.current_skills:
            questions.append({
                "question": "What programming languages or technical skills do you already know?",
                "field": "current_skills",
                "type": "multi_select",
                "options": ["Python", "Java", "JavaScript", "SQL", "R", "C++", "HTML/CSS", "Git", "Excel", "PowerBI"]
            })
        
        if not profile.target_skills:
            questions.append({
                "question": "What skills do you want to develop for your career goal?",
                "field": "target_skills", 
                "type": "multi_select",
                "options": ["Machine Learning", "Data Analysis", "Web Development", "Cloud Computing", "Project Management"]
            })
        
        if not profile.completed_courses:
            questions.append({
                "question": "What UTD courses have you already taken?",
                "field": "completed_courses",
                "type": "search_select",
                "placeholder": "Search for courses (e.g., CS 1337, MATH 2414)"
            })
        
        if not profile.industry_interests:
            questions.append({
                "question": "What industries interest you?",
                "field": "industry_interests",
                "type": "multi_select",
                "options": ["Technology", "Finance", "Healthcare", "Education", "Consulting", "Startups", "Government"]
            })
        
        return questions[:3]  # Limit to 3 questions to avoid overwhelming

# Predefined options for form fields
CAREER_GOALS = [
    "Data Scientist", "Software Engineer", "Product Manager", "Business Analyst",
    "DevOps Engineer", "Data Analyst", "Full Stack Developer", "Cybersecurity Analyst",
    "Machine Learning Engineer", "Investment Analyst", "Management Consultant",
    "Research Scientist", "Technical Consultant", "Operations Manager"
]

SKILL_OPTIONS = [
    "Python", "Java", "JavaScript", "SQL", "R", "C++", "HTML/CSS", "Git",
    "Machine Learning", "Data Analysis", "Web Development", "Cloud Computing",
    "Project Management", "Excel", "PowerBI", "Tableau", "Docker", "AWS"
]

DEPARTMENT_OPTIONS = [
    "Computer Science", "Data Science", "Business", "Engineering", "Mathematics",
    "Statistics", "Neuroscience", "Psychology", "Economics", "Finance"
]

INDUSTRY_OPTIONS = [
    "Technology", "Finance", "Healthcare", "Education", "Consulting", 
    "Startups", "Government", "Non-profit", "Manufacturing", "Retail"
]
