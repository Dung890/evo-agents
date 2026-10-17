"""
Project Advisor Agent
Provides personalized project recommendations using AWS Bedrock LLM
"""
import json
from typing import Dict, Any, List, Optional
from src.core.aws.bedrock_service import BedrockService


class ProjectAdvisorAgent:
    """
    AI Agent that recommends practical projects to build skills
    
    Uses AWS Bedrock Claude Haiku for cost-effective, intelligent project suggestions
    that align with career goals, course curriculum, and job market demands.
    """
    
    def __init__(self):
        """Initialize the Project Advisor Agent with Bedrock LLM"""
        self.bedrock_service = BedrockService()
        self.agent_name = "Project Advisor Agent"
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized project recommendations
        
        Args:
            request: Dict containing:
                - career_goal (str): Target career (e.g., "Data Scientist")
                - current_skills (List[str]): Skills user already has
                - target_skills (List[str]): Skills to develop from job market
                - recommended_courses (List[Dict]): Courses the user should take
                - skill_level (str): beginner/intermediate/advanced
                
        Returns:
            Dict with project recommendations and explanations
        """
        career_goal = request.get("career_goal", "Software Engineer")
        current_skills = request.get("current_skills", [])
        target_skills = request.get("target_skills", [])
        recommended_courses = request.get("recommended_courses", [])
        skill_level = request.get("skill_level", "intermediate")
        
        print(f"\n🎯 {self.agent_name} analyzing project needs for: {career_goal}")
        
        try:
            # Generate LLM-powered project recommendations
            projects = await self._generate_project_recommendations(
                career_goal=career_goal,
                current_skills=current_skills,
                target_skills=target_skills,
                recommended_courses=recommended_courses,
                skill_level=skill_level
            )
            
            return {
                "success": True,
                "career_goal": career_goal,
                "skill_level": skill_level,
                "projects": projects,
                "total_projects": len(projects),
                "implementation_timeline": self._estimate_timeline(projects)
            }
            
        except Exception as e:
            print(f"⚠️ Error generating project recommendations: {e}")
            # Fallback to rule-based recommendations
            return self._get_fallback_projects(career_goal, target_skills, skill_level)
    
    async def _generate_project_recommendations(
        self,
        career_goal: str,
        current_skills: List[str],
        target_skills: List[str],
        recommended_courses: List[Dict],
        skill_level: str
    ) -> List[Dict[str, Any]]:
        """
        Use AWS Bedrock Claude Haiku to generate intelligent project recommendations
        
        Returns:
            List of project recommendations with details
        """
        # Create prompt for the LLM
        prompt = self._create_project_prompt(
            career_goal, current_skills, target_skills, recommended_courses, skill_level
        )
        
        try:
            # Call Bedrock LLM
            response = await self.bedrock_service.invoke_model_async(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7  # Slightly creative for project ideas
            )
            
            # Parse LLM response
            projects = self._parse_project_response(response)
            
            if projects:
                print(f"✅ Generated {len(projects)} LLM-powered project recommendations")
                return projects
            else:
                print("⚠️ LLM response parsing failed, using fallback")
                return self._get_rule_based_projects(career_goal, target_skills, skill_level)
                
        except Exception as e:
            print(f"⚠️ LLM invocation failed: {e}, using fallback")
            return self._get_rule_based_projects(career_goal, target_skills, skill_level)
    
    def _create_project_prompt(
        self,
        career_goal: str,
        current_skills: List[str],
        target_skills: List[str],
        recommended_courses: List[Dict],
        skill_level: str
    ) -> str:
        """Create a detailed prompt for the LLM"""
        
        course_names = [course.get("title", course.get("course_code", "")) for course in recommended_courses[:5]]
        
        prompt = f"""You are an expert career advisor helping a student become a {career_goal}.

**Student Profile:**
- Career Goal: {career_goal}
- Current Skill Level: {skill_level}
- Current Skills: {', '.join(current_skills[:10]) if current_skills else 'None listed'}
- Skills to Develop: {', '.join(target_skills[:10])}
- Recommended Courses: {', '.join(course_names)}

**Task:** Generate 4 practical project recommendations that will:
1. Build the required skills for {career_goal} positions
2. Create portfolio pieces for job applications
3. Demonstrate competency in the target skills
4. Progress from easier to more complex

**Requirements:**
- Each project should target 2-3 specific skills from the target skills list
- Projects should be completable in 2-8 weeks each
- Include real-world applicability
- Should be impressive to employers

**Output Format (JSON):**
```json
[
  {{
    "title": "Project Name",
    "difficulty": "beginner/intermediate/advanced",
    "duration_weeks": 2-8,
    "description": "Brief description of what the project does",
    "skills_practiced": ["Skill1", "Skill2", "Skill3"],
    "why_valuable": "Why this project will impress employers",
    "key_features": ["Feature 1", "Feature 2", "Feature 3"],
    "portfolio_impact": "How this strengthens the student's portfolio"
  }}
]
```

Generate exactly 4 projects. Make them specific, practical, and aligned with {career_goal} job requirements."""
        
        return prompt
    
    def _parse_project_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured project recommendations"""
        try:
            # Try to extract JSON from the response
            # LLM often wraps JSON in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find array directly
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                else:
                    return []
            
            projects = json.loads(json_str)
            
            # Validate and enhance project data
            validated_projects = []
            for i, project in enumerate(projects):
                if isinstance(project, dict) and "title" in project:
                    # Ensure all required fields exist
                    validated_project = {
                        "project_number": i + 1,
                        "title": project.get("title", f"Project {i+1}"),
                        "difficulty": project.get("difficulty", "intermediate"),
                        "duration_weeks": project.get("duration_weeks", 4),
                        "description": project.get("description", ""),
                        "skills_practiced": project.get("skills_practiced", []),
                        "why_valuable": project.get("why_valuable", ""),
                        "key_features": project.get("key_features", []),
                        "portfolio_impact": project.get("portfolio_impact", ""),
                        "source": "LLM-Generated"
                    }
                    validated_projects.append(validated_project)
            
            return validated_projects
            
        except Exception as e:
            print(f"⚠️ Error parsing LLM response: {e}")
            return []
    
    def _get_rule_based_projects(
        self,
        career_goal: str,
        target_skills: List[str],
        skill_level: str
    ) -> List[Dict[str, Any]]:
        """Fallback: Rule-based project recommendations"""
        
        career_lower = career_goal.lower()
        
        # Project templates by career type
        if "data scientist" in career_lower or "data analyst" in career_lower:
            projects = [
                {
                    "project_number": 1,
                    "title": "Customer Churn Prediction Dashboard",
                    "difficulty": "intermediate",
                    "duration_weeks": 3,
                    "description": "Build an interactive dashboard that predicts customer churn using machine learning and displays insights with visualizations.",
                    "skills_practiced": ["Python", "Machine Learning", "Data Visualization", "SQL"],
                    "why_valuable": "Demonstrates end-to-end data science skills that companies need - data collection, modeling, and business insights.",
                    "key_features": ["ML model training", "Interactive Plotly/Dash dashboard", "SQL database integration", "Model performance metrics"],
                    "portfolio_impact": "Shows you can solve real business problems with data",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 2,
                    "title": "Real-Time Stock Market Analysis Tool",
                    "difficulty": "advanced",
                    "duration_weeks": 5,
                    "description": "Create a tool that fetches live stock data, performs technical analysis, and provides trading signals using statistical models.",
                    "skills_practiced": ["Python", "APIs", "Statistical Analysis", "Data Visualization"],
                    "why_valuable": "Combines data engineering (APIs), analysis (statistics), and visualization - the full data science stack.",
                    "key_features": ["Real-time API integration", "Technical indicators (RSI, MACD)", "Historical backtesting", "Alert system"],
                    "portfolio_impact": "Demonstrates you can work with real-time data and financial modeling",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 3,
                    "title": "Social Media Sentiment Analyzer",
                    "difficulty": "intermediate",
                    "duration_weeks": 4,
                    "description": "Analyze sentiment from Twitter/Reddit posts about brands or topics using NLP and visualize trends over time.",
                    "skills_practiced": ["NLP", "Python", "API Integration", "Data Visualization"],
                    "why_valuable": "NLP is in high demand, and this shows you can extract insights from unstructured text data.",
                    "key_features": ["Twitter API integration", "Sentiment classification", "Trend analysis", "Word clouds and visualizations"],
                    "portfolio_impact": "Shows expertise in text analytics, a highly sought-after skill",
                    "source": "Rule-Based"
                }
            ]
        
        elif "financial analyst" in career_lower or "finance" in career_lower:
            projects = [
                {
                    "project_number": 1,
                    "title": "Personal Investment Portfolio Optimizer",
                    "difficulty": "intermediate",
                    "duration_weeks": 3,
                    "description": "Build a tool that optimizes investment portfolios using Modern Portfolio Theory and Monte Carlo simulations.",
                    "skills_practiced": ["Python", "Financial Modeling", "Statistical Analysis", "Excel Integration"],
                    "why_valuable": "Shows you understand core finance concepts (risk/return) and can implement them programmatically.",
                    "key_features": ["Risk-return optimization", "Monte Carlo simulation", "Efficient frontier visualization", "Historical backtesting"],
                    "portfolio_impact": "Demonstrates quantitative finance skills employers value",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 2,
                    "title": "Financial Statement Analysis Dashboard",
                    "difficulty": "beginner",
                    "duration_weeks": 2,
                    "description": "Create an automated dashboard that pulls financial statements and calculates key ratios for company analysis.",
                    "skills_practiced": ["Excel", "Financial Analysis", "Data Visualization", "Python"],
                    "why_valuable": "Financial statement analysis is fundamental to analyst roles - automating it shows efficiency.",
                    "key_features": ["API integration (Alpha Vantage)", "Ratio calculations (P/E, ROE, etc.)", "Comparative analysis", "Trend visualizations"],
                    "portfolio_impact": "Shows you can automate tedious analyst tasks",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 3,
                    "title": "DCF Valuation Model with Scenario Analysis",
                    "difficulty": "advanced",
                    "duration_weeks": 4,
                    "description": "Build a comprehensive Discounted Cash Flow model with multiple scenario analysis and sensitivity testing.",
                    "skills_practiced": ["Financial Modeling", "Valuation", "Excel", "Scenario Analysis"],
                    "why_valuable": "DCF is the gold standard for valuation - mastering it is essential for finance careers.",
                    "key_features": ["3-statement model", "WACC calculation", "Scenario analysis", "Sensitivity tables"],
                    "portfolio_impact": "Core skill for investment banking and equity research roles",
                    "source": "Rule-Based"
                }
            ]
        
        elif "software" in career_lower or "developer" in career_lower:
            projects = [
                {
                    "project_number": 1,
                    "title": "Task Management Web App with Real-Time Collaboration",
                    "difficulty": "intermediate",
                    "duration_weeks": 4,
                    "description": "Build a full-stack web application where teams can manage tasks with real-time updates using WebSockets.",
                    "skills_practiced": ["React", "Node.js", "WebSockets", "Database Design", "REST APIs"],
                    "why_valuable": "Demonstrates full-stack development skills and modern web technologies that companies use.",
                    "key_features": ["User authentication", "Real-time updates", "Drag-and-drop UI", "RESTful API", "PostgreSQL database"],
                    "portfolio_impact": "Shows you can build production-ready applications",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 2,
                    "title": "Mobile-First E-Commerce Platform",
                    "difficulty": "advanced",
                    "duration_weeks": 6,
                    "description": "Create a responsive e-commerce site with payment integration, cart management, and admin dashboard.",
                    "skills_practiced": ["React", "Payment APIs", "Database", "Cloud Deployment", "Security"],
                    "why_valuable": "E-commerce projects show you understand complex business logic and payment systems.",
                    "key_features": ["Stripe payment integration", "Product catalog", "Order management", "Admin panel", "AWS deployment"],
                    "portfolio_impact": "Demonstrates ability to handle complex, real-world applications",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 3,
                    "title": "CI/CD Pipeline with Automated Testing",
                    "difficulty": "intermediate",
                    "duration_weeks": 3,
                    "description": "Set up a complete CI/CD pipeline with automated testing, code quality checks, and deployment.",
                    "skills_practiced": ["DevOps", "Git", "Docker", "Testing", "Automation"],
                    "why_valuable": "Shows you understand modern development workflows beyond just coding.",
                    "key_features": ["GitHub Actions", "Unit/integration tests", "Docker containers", "Automated deployment", "Code coverage reports"],
                    "portfolio_impact": "DevOps skills are highly valued - sets you apart from code-only developers",
                    "source": "Rule-Based"
                }
            ]
        
        elif "neuroscience" in career_lower or "neuro" in career_lower:
            projects = [
                {
                    "project_number": 1,
                    "title": "EEG Signal Processing and Classification",
                    "difficulty": "advanced",
                    "duration_weeks": 5,
                    "description": "Process EEG data, extract features, and build a classifier to detect different brain states or patterns.",
                    "skills_practiced": ["Signal Processing", "Python", "Machine Learning", "Data Analysis"],
                    "why_valuable": "Shows you can work with real neuroscience data and apply computational methods.",
                    "key_features": ["Noise filtering", "Feature extraction", "ML classification", "Visualization of brain activity"],
                    "portfolio_impact": "Demonstrates practical neuroscience research skills",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 2,
                    "title": "Neural Network Simulation of Brain Circuits",
                    "difficulty": "advanced",
                    "duration_weeks": 6,
                    "description": "Build a computational model simulating neural circuits and their behavior under different conditions.",
                    "skills_practiced": ["Computational Neuroscience", "Python", "Modeling", "Research"],
                    "why_valuable": "Computational modeling is essential for modern neuroscience research.",
                    "key_features": ["Integrate-and-fire neurons", "Synaptic plasticity", "Circuit dynamics", "Parameter exploration"],
                    "portfolio_impact": "Shows strong theoretical and computational foundations",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 3,
                    "title": "Behavioral Data Analysis Pipeline",
                    "difficulty": "intermediate",
                    "duration_weeks": 4,
                    "description": "Create an automated pipeline for analyzing behavioral experiment data with statistical tests and visualizations.",
                    "skills_practiced": ["Data Analysis", "Statistics", "Python", "Research Methods"],
                    "why_valuable": "Behavioral analysis is core to neuroscience - automating it shows efficiency.",
                    "key_features": ["Automated data cleaning", "Statistical testing", "Publication-quality plots", "Report generation"],
                    "portfolio_impact": "Demonstrates research skills employers and labs value",
                    "source": "Rule-Based"
                }
            ]
        
        else:
            # Generic projects
            projects = [
                {
                    "project_number": 1,
                    "title": "Personal Portfolio Website with CMS",
                    "difficulty": "beginner",
                    "duration_weeks": 2,
                    "description": "Build a professional portfolio website with a content management system to showcase your work.",
                    "skills_practiced": ["Web Development", "Design", "CMS", "Deployment"],
                    "why_valuable": "Every professional needs a strong online presence - this demonstrates your web skills.",
                    "key_features": ["Responsive design", "Project showcase", "Blog/content system", "Contact form"],
                    "portfolio_impact": "Creates a home for all your other projects",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 2,
                    "title": "Industry-Specific Analysis Tool",
                    "difficulty": "intermediate",
                    "duration_weeks": 4,
                    "description": "Create a tool that solves a specific problem in your target industry using relevant technologies.",
                    "skills_practiced": target_skills[:4] if target_skills else ["Analysis", "Programming", "Problem Solving"],
                    "why_valuable": "Industry-specific projects show you understand the domain and its challenges.",
                    "key_features": ["Data collection", "Analysis engine", "Visualization dashboard", "Reporting"],
                    "portfolio_impact": "Demonstrates domain knowledge and technical skills",
                    "source": "Rule-Based"
                },
                {
                    "project_number": 3,
                    "title": "Open Source Contribution",
                    "difficulty": "intermediate",
                    "duration_weeks": 3,
                    "description": "Make meaningful contributions to an established open-source project in your field.",
                    "skills_practiced": ["Collaboration", "Git", "Code Review", "Documentation"],
                    "why_valuable": "Open source contributions demonstrate your ability to work on large codebases and collaborate.",
                    "key_features": ["Bug fixes", "Feature additions", "Documentation improvements", "Code review participation"],
                    "portfolio_impact": "Shows you can work in real-world development environments",
                    "source": "Rule-Based"
                }
            ]
        
        # Adjust difficulty based on skill level
        if skill_level == "beginner":
            projects = [p for p in projects if p["difficulty"] in ["beginner", "intermediate"]]
        elif skill_level == "advanced":
            projects = [p for p in projects if p["difficulty"] in ["intermediate", "advanced"]]
        
        return projects[:4]  # Return max 4 projects
    
    def _get_fallback_projects(
        self,
        career_goal: str,
        target_skills: List[str],
        skill_level: str
    ) -> Dict[str, Any]:
        """Return fallback response when everything fails"""
        projects = self._get_rule_based_projects(career_goal, target_skills, skill_level)
        
        return {
            "success": True,
            "career_goal": career_goal,
            "skill_level": skill_level,
            "projects": projects,
            "total_projects": len(projects),
            "implementation_timeline": self._estimate_timeline(projects),
            "note": "Using rule-based project recommendations"
        }
    
    def _estimate_timeline(self, projects: List[Dict[str, Any]]) -> str:
        """Estimate total time to complete all projects"""
        total_weeks = sum(p.get("duration_weeks", 4) for p in projects)
        months = total_weeks // 4
        remaining_weeks = total_weeks % 4
        
        if months > 0 and remaining_weeks > 0:
            return f"{months} months and {remaining_weeks} weeks"
        elif months > 0:
            return f"{months} months"
        else:
            return f"{total_weeks} weeks"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": self.agent_name,
            "capabilities": [
                "LLM-powered project recommendations",
                "Career-specific project ideas",
                "Skill-aligned project planning",
                "Portfolio building guidance",
                "Difficulty-appropriate suggestions"
            ],
            "llm_model": "Claude 3 Haiku (via AWS Bedrock)",
            "fallback": "Rule-based project templates"
        }

