from typing import Dict, Any, List

from src.agents.job_market_agent.job_market_agent import JobMarketAgent
from src.agents.course_catalog_agent.course_catalog_agent import CourseCatalogAgent
from src.agents.career_matching_agent.career_matching_agent import CareerMatchingAgent
from src.agents.project_advisor_agent.project_advisor_agent import ProjectAdvisorAgent

class AgentOrchestrator:
    """
    Orchestrator that coordinates interactions between specialized agents
    to provide comprehensive career advisory services to UTD students.
    """

    def __init__(self):
        """Initialize the Agent Orchestrator with all specialized agents"""
        self.job_market_agent = JobMarketAgent()
        self.course_catalog_agent = CourseCatalogAgent()
        self.project_advisor_agent = ProjectAdvisorAgent()
        
        # Initialize Career Matching Agent with other agents for coordination
        self.career_matching_agent = CareerMatchingAgent(
            job_market_agent=self.job_market_agent,
            course_catalog_agent=self.course_catalog_agent
        )

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user request by coordinating between specialized agents

        Args:
            request (Dict[str, Any]): User request

        Returns:
            Dict[str, Any]: Comprehensive response
        """
        request_type = request.get("request_type", "career_advice")

        if request_type == "career_advice":
            return await self._process_career_advice_request(request)
        elif request_type == "job_market_analysis":
            return await self._process_job_market_request(request)
        elif request_type == "course_search":
            return self._process_course_search_request(request)
        elif request_type == "get_all_courses":
            return self._process_get_all_courses_request(request)
        elif request_type == "project_recommendations":
            return await self._process_project_request(request)
        else:
            return {"error": "Invalid request type"}

    async def _process_career_advice_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a comprehensive career advice request using the Career Matching Agent
        
        • Takes user career goals and coordinates with other agents
        • Analyzes job requirements vs. available coursework
        • Generates personalized course recommendations with explanations

        Args:
            request (Dict[str, Any]): Career advice request

        Returns:
            Dict[str, Any]: Comprehensive career advice response
        """
        print("🎯 Processing career advice request through Career Matching Agent...")
        
        # Extract career goal from request
        career_goal = request.get("career_goal", "")
        
        # Use the Career Matching Agent to coordinate everything
        career_matching_response = await self.career_matching_agent.process_request(request)
        
        # If Career Matching Agent succeeded, return its comprehensive response
        if career_matching_response.get("success"):
            # Generate project recommendations FIRST (can't await inside dict literal)
            project_recommendations = await self._generate_project_recommendations(
                career_goal, 
                request.get("current_skills", []), 
                career_matching_response.get("course_recommendations", [])
            )
            
            return {
                "success": True,
                "career_goal": career_matching_response.get("career_goal"),
                "location": career_matching_response.get("location"),
                
                # Job market insights
                "job_insights": [
                    f"Found {career_matching_response['job_market_analysis']['total_jobs']} job opportunities",
                    f"Average salary: ${career_matching_response['job_market_analysis']['salary_info'].get('overall_average', 0):,.0f}",
                    f"Top trending skills: {', '.join(career_matching_response['job_market_analysis']['trending_skills'][:3])}"
                ],
                
                # Market insights with job trends and hot skills
                "market_insights": career_matching_response.get("market_insights", {}),
                
                # Curriculum comparison: Job market vs course alignment
                "curriculum_comparison": career_matching_response.get("curriculum_comparison", {}),
                
                # Skill gap analysis
                "skill_analysis": {
                    "current_coverage": f"{career_matching_response['skill_gap_analysis']['skill_coverage']:.1f}%",
                    "skills_to_develop": career_matching_response['skill_gap_analysis']['skills_to_develop'],
                    "missing_skills": [skill['skill'] for skill in career_matching_response['skill_gap_analysis']['missing_skills'][:5]]
                },
                
                # Course recommendations with explanations
                "course_recommendations": career_matching_response.get("course_recommendations", []),
                
                # Learning path
                "learning_path": career_matching_response.get("learning_path", {}),
                
                # Project recommendations
                "project_recommendations": project_recommendations,
                
                # Summary
                "summary": {
                    "total_courses_recommended": career_matching_response.get("total_recommended_courses", 0),
                    "estimated_completion": career_matching_response.get("estimated_completion_time", "Unknown"),
                    "next_steps": [
                        "Review the recommended courses and their explanations",
                        "Check prerequisites for your first semester courses", 
                        "Consider your current schedule and course load",
                        "Meet with an academic advisor to finalize your plan"
                    ]
                }
            }
        
        # Fallback if Career Matching Agent failed
        return {
            "success": False,
            "error": "Career matching analysis failed",
            "career_goal": request.get("career_goal", ""),
            "location": request.get("location", ""),
            "message": "Please try again or contact support"
        }

    async def _process_job_market_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a job market analysis request

        Args:
            request (Dict[str, Any]): Job market request

        Returns:
            Dict[str, Any]: Job market analysis
        """
        return await self.job_market_agent.process_request(request)

    def _process_course_search_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a course search request

        Args:
            request (Dict[str, Any]): Course search request

        Returns:
            Dict[str, Any]: Course search results
        """
        return self.course_catalog_agent.process_request(request)
    
    async def _process_project_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a project recommendation request
        
        Args:
            request (Dict[str, Any]): Project request with career_goal, skills, etc.
            
        Returns:
            Dict[str, Any]: Project recommendations
        """
        try:
            project_response = await self.project_advisor_agent.process_request(request)
            
            if project_response.get("success"):
                return {
                    "success": True,
                    "career_goal": project_response.get("career_goal"),
                    "skill_level": project_response.get("skill_level"),
                    "projects": project_response.get("projects", []),
                    "total_projects": project_response.get("total_projects", 0),
                    "implementation_timeline": project_response.get("implementation_timeline"),
                    "summary": {
                        "purpose": "Build practical skills and create portfolio pieces",
                        "approach": "Progress from foundational to advanced projects",
                        "benefit": "Demonstrate competency to employers with tangible work"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate project recommendations"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Project recommendation failed: {str(e)}"
            }

    async def _generate_project_recommendations(
        self, 
        career_goal: str, 
        current_skills: List[str], 
        course_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate project recommendations using the Project Advisor Agent
        
        Args:
            career_goal: User's career goal
            current_skills: User's current skills
            course_recommendations: Recommended courses
            
        Returns:
            List[Dict[str, Any]]: Project recommendations
        """
        try:
            # Extract target skills from course recommendations
            target_skills = []
            for course in course_recommendations:
                skills_addressed = course.get("skills_addressed", [])
                target_skills.extend(skills_addressed)
            
            # Remove duplicates
            target_skills = list(set(target_skills))
            
            # Create project recommendation request
            project_request = {
                "request_type": "project_recommendations",
                "career_goal": career_goal,
                "current_skills": current_skills,
                "target_skills": target_skills[:10],  # Limit to top 10 skills
                "skill_level": "intermediate",  # Default level
                "recommended_courses": course_recommendations[:5]  # Top 5 courses
            }
            
            # Get project recommendations
            result = await self.project_advisor_agent.process_request(project_request)
            
            if result.get("success") and result.get("projects"):
                print(f"✅ Generated {len(result['projects'])} project recommendations")
                return result["projects"]
            else:
                # Return empty list if no projects found
                print(f"⚠️ No projects returned from advisor. Result: {result.get('error', 'Unknown')}")
                return []
                
        except Exception as e:
            print(f"❌ Error generating project recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _process_get_all_courses_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all courses from the UTD course catalog
        
        Args:
            request (Dict[str, Any]): Request (no parameters needed)
            
        Returns:
            Dict[str, Any]: All courses response
        """
        try:
            all_courses = self.course_catalog_agent.get_all_courses()
            
            return {
                "success": True,
                "courses": all_courses,
                "total_courses": len(all_courses),
                "message": f"Retrieved {len(all_courses)} courses from UTD catalog"
            }
        except Exception as e:
            print(f"⚠️ Error fetching all courses: {e}")
            return {
                "success": False,
                "courses": [],
                "total_courses": 0,
                "error": str(e)
            }

    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """
        Get capabilities of all agents

        Returns:
            Dict[str, List[str]]: Dictionary mapping agent names to capabilities
        """
        return {
            "job_market_agent": self.job_market_agent.get_capabilities(),
            "course_catalog_agent": self.course_catalog_agent.get_capabilities(),
            "career_matching_agent": self.career_matching_agent.get_capabilities(),
            "project_advisor_agent": self.project_advisor_agent.get_capabilities()
        }
