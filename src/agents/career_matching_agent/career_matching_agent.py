from typing import Dict, Any, List
import json
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from src.agents.base_agent import BaseAgent
from src.core.llm.career_llm_service import career_llm_service

# Configure logging
logger = logging.getLogger(__name__)

class CareerMatchingAgent(BaseAgent):
    """
    Agent responsible for taking user career goals, coordinating with other agents,
    analyzing job requirements vs. available coursework, and generating personalized
    course recommendations with explanations.
    
    This agent:
    • Takes user career goals and coordinates with other agents
    • Analyzes job requirements vs. available coursework  
    • Generates personalized course recommendations with explanations
    """

    def __init__(self, job_market_agent=None, course_catalog_agent=None):
        """Initialize the Career Matching Agent"""
        super().__init__(
            name="Career Matching Agent",
            description="Matches career goals with courses and provides personalized recommendations"
        )
        self.job_market_agent = job_market_agent
        self.course_catalog_agent = course_catalog_agent

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a career matching request by coordinating with other agents
        
        • Takes user career goals and coordinates with other agents
        • Analyzes job requirements vs. available coursework
        • Generates personalized course recommendations with explanations

        Args:
            request (Dict[str, Any]): Request with career goal and user info

        Returns:
            Dict[str, Any]: Career matching recommendations
        """
        career_goal = request.get("career_goal", "")
        location = request.get("location", "")
        current_skills = request.get("current_skills", [])
        completed_courses = request.get("completed_courses", [])

        if not career_goal:
            return {"error": "Career goal is required"}

        print(f"🎯 Career Matching Agent processing: {career_goal}")
        
        # Store career goal for LLM context
        self._current_career_goal = career_goal
        
        # Step 1: Coordinate with Job Market Agent to get real job requirements
        print("📊 Coordinating with Job Market Agent...")
        job_market_data = await self._get_job_market_requirements(career_goal, location)
        
        # Step 2: Coordinate with Course Catalog Agent to get available courses
        print("📚 Coordinating with Course Catalog Agent...")
        available_courses = await self._get_available_courses()
        
        # Step 3: Analyze job requirements vs. available coursework
        print("🔍 Analyzing job requirements vs. available coursework...")
        skill_gap_analysis = self._analyze_skill_gaps(job_market_data, current_skills)
        
        # Step 4: Generate personalized course recommendations with explanations
        print("💡 Generating personalized course recommendations...")
        course_recommendations = self._generate_course_recommendations(
            skill_gap_analysis, available_courses, completed_courses
        )
        
        # Step 5: Create learning path
        print("🗺️ Creating personalized learning path...")
        learning_path = self._create_learning_path(course_recommendations, current_skills)
        
        # Step 6: Extract job trends and hot skills
        print("📈 Analyzing job market trends and hot skills...")
        market_insights = self._extract_market_insights(job_market_data, skill_gap_analysis, career_goal)
        
        # Step 7: Create job-to-course mapping analysis
        print("🔗 Creating job market to course curriculum comparison...")
        curriculum_comparison = self._create_curriculum_comparison(
            job_market_data,
            course_recommendations,
            skill_gap_analysis
        )

        return {
            "success": True,
            "career_goal": career_goal,
            "location": location,
            "job_market_analysis": {
                "total_jobs": job_market_data.get("job_count", 0),
                "required_skills": job_market_data.get("skills", {}),
                "salary_info": job_market_data.get("salaries", {}),
                "trending_skills": list(job_market_data.get("skills", {}).keys())[:10]
            },
            "market_insights": market_insights,
            "curriculum_comparison": curriculum_comparison,
            "skill_gap_analysis": skill_gap_analysis,
            "course_recommendations": course_recommendations,
            "learning_path": learning_path,
            "total_recommended_courses": len(course_recommendations),
            "estimated_completion_time": f"{len(course_recommendations) // 2 + 1} semesters"
        }

    async def _get_job_market_requirements(self, career_goal: str, location: str) -> Dict[str, Any]:
        """
        Coordinate with Job Market Agent to get real job requirements
        
        Args:
            career_goal (str): Career goal
            location (str): Preferred location
            
        Returns:
            Dict[str, Any]: Job market data with requirements
        """
        if not self.job_market_agent:
            print("⚠️ Job Market Agent not available, using fallback data")
            return self._get_fallback_job_requirements(career_goal)
        
        try:
            # Call Job Market Agent to get real job data (optimized for top 2 jobs)
            job_request = {
                "job_title": career_goal,
                "location": location,
                "limit": 2  # Optimized to only get top 2 jobs for efficiency
            }
            job_data = await self.job_market_agent.process_request(job_request)
            return job_data
        except Exception as e:
            print(f"❌ Error coordinating with Job Market Agent: {e}")
            return self._get_fallback_job_requirements(career_goal)
    
    def _get_fallback_job_requirements(self, career_goal: str) -> Dict[str, Any]:
        """Fallback job requirements when Job Market Agent is unavailable"""
        # Common skills for different career goals
        skill_mapping = {
            "data scientist": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas", "NumPy"],
            "software engineer": ["Python", "JavaScript", "Git", "SQL", "React", "Node.js"],
            "devops engineer": ["AWS", "Docker", "Kubernetes", "Linux", "Python", "Jenkins"],
            "data engineer": ["Python", "SQL", "Apache Spark", "AWS", "ETL", "Kafka"],
            "machine learning engineer": ["Python", "TensorFlow", "PyTorch", "MLOps", "Docker", "AWS"]
        }
        
        # Get skills for the career goal (case insensitive)
        goal_lower = career_goal.lower()
        skills = {}
        for key, skill_list in skill_mapping.items():
            if key in goal_lower:
                for skill in skill_list:
                    skills[skill] = 3  # Mock frequency
                break
        
        if not skills:
            # Default skills for any technical role
            skills = {"Python": 3, "SQL": 2, "Git": 2, "Problem Solving": 3}
        
        return {
            "job_count": 5,
            "skills": skills,
            "salaries": {"count": 3, "average_min": 70000, "average_max": 120000, "overall_average": 95000},
            "trends": ["Remote work", "Cloud computing", "AI/ML"]
        }

    async def _get_available_courses(self) -> List[Dict[str, Any]]:
        """
        Coordinate with Course Catalog Agent to get available courses
        
        Returns:
            List[Dict[str, Any]]: Available courses
        """
        if not self.course_catalog_agent:
            print("⚠️ Course Catalog Agent not available, using fallback data")
            return self._get_fallback_courses()
        
        try:
            # Get all available courses directly from Course Catalog Agent
            # Use direct access to courses instead of process_request for getting all courses
            return self.course_catalog_agent.courses
        except Exception as e:
            print(f"❌ Error coordinating with Course Catalog Agent: {e}")
            return self._get_fallback_courses()
    
    def _get_fallback_courses(self) -> List[Dict[str, Any]]:
        """Fallback course data when Course Catalog Agent is unavailable"""
        return [
            {
                "course_code": "CS 1336",
                "title": "Programming Fundamentals",
                "description": "Introduction to programming concepts using Java",
                "skills": ["Java", "Programming", "Problem Solving"],
                "prerequisites": "None"
            },
            {
                "course_code": "CS 2336",
                "title": "Computer Science II",
                "description": "Object-oriented programming and data structures",
                "skills": ["Java", "Data Structures", "OOP"],
                "prerequisites": "CS 1336"
            },
            {
                "course_code": "CS 3345",
                "title": "Data Structures and Introduction to Algorithmic Analysis",
                "description": "Advanced data structures and algorithm analysis",
                "skills": ["Algorithms", "Data Structures", "Analysis"],
                "prerequisites": "CS 2336"
            },
            {
                "course_code": "CS 4349",
                "title": "Advanced Algorithm Design and Analysis",
                "description": "Design and analysis of efficient algorithms",
                "skills": ["Algorithms", "Complexity Analysis", "Problem Solving"],
                "prerequisites": "CS 3345"
            },
            {
                "course_code": "CS 4337",
                "title": "Organization of Programming Languages",
                "description": "Study of programming language concepts and paradigms",
                "skills": ["Programming Languages", "Compilers", "Language Design"],
                "prerequisites": "CS 3345"
            },
            {
                "course_code": "CS 4348",
                "title": "Operating Systems Concepts",
                "description": "Operating system design and implementation",
                "skills": ["Operating Systems", "System Programming", "Concurrency"],
                "prerequisites": "CS 3345"
            },
            {
                "course_code": "CS 4375",
                "title": "Introduction to Machine Learning",
                "description": "Fundamentals of machine learning algorithms and applications",
                "skills": ["Machine Learning", "Python", "Statistics", "Data Analysis"],
                "prerequisites": "CS 3345"
            },
            {
                "course_code": "CS 4395",
                "title": "Human Language Technologies",
                "description": "Natural language processing and computational linguistics",
                "skills": ["NLP", "Python", "Machine Learning", "Text Processing"],
                "prerequisites": "CS 3345"
            }
        ]
    
    def _analyze_skill_gaps(self, job_market_data: Dict[str, Any], current_skills: List[str]) -> Dict[str, Any]:
        """
        Analyze skill gaps between job requirements and current skills
        
        Args:
            job_market_data (Dict[str, Any]): Job market data with required skills
            current_skills (List[str]): User's current skills
            
        Returns:
            Dict[str, Any]: Skill gap analysis with prioritization and recommendations
        """
        required_skills = job_market_data.get("skills", {})
        
        # Convert current_skills to lowercase for comparison
        current_skills_lower = [skill.lower() for skill in current_skills]
        
        # Identify missing skills
        missing_skills = []
        existing_skills = []
        
        for skill, frequency in required_skills.items():
            if skill.lower() in current_skills_lower:
                existing_skills.append({
                    "skill": skill,
                    "frequency": frequency,
                    "status": "already_have",
                    "confidence": "verified"
                })
            else:
                # Enhanced priority calculation
                if frequency >= 4:
                    priority = "critical"
                elif frequency >= 3:
                    priority = "high"
                elif frequency >= 2:
                    priority = "medium"
                else:
                    priority = "low"
                
                missing_skills.append({
                    "skill": skill,
                    "frequency": frequency,
                    "priority": priority,
                    "urgency_score": frequency * 10  # For ranking
                })
        
        # Sort missing skills by frequency (priority) and urgency
        missing_skills.sort(key=lambda x: (-x["frequency"], x["skill"]))
        
        # Calculate skill coverage percentage
        total_skills = len(existing_skills) + len(missing_skills)
        skill_coverage = (len(existing_skills) / total_skills * 100) if total_skills > 0 else 0
        
        # Generate skill development recommendations
        skill_recommendations = []
        for skill in missing_skills[:5]:  # Top 5 missing skills
            skill_recommendations.append({
                "skill": skill["skill"],
                "priority": skill["priority"],
                "action": f"Learn {skill['skill']} through coursework and hands-on projects",
                "market_demand": "High" if skill["frequency"] >= 3 else "Medium"
            })
        
        return {
            "missing_skills": missing_skills,
            "existing_skills": existing_skills,
            "skill_coverage": round(skill_coverage, 1),
            "total_required_skills": len(required_skills),
            "skills_to_develop": len(missing_skills),
            "skill_recommendations": skill_recommendations,
            "readiness_level": "Excellent" if skill_coverage >= 80 else "Good" if skill_coverage >= 60 else "Developing" if skill_coverage >= 40 else "Beginner"
        }

    def _generate_course_recommendations(
        self,
        skill_gap_analysis: Dict[str, Any],
        available_courses: List[Dict[str, Any]],
        completed_courses: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized course recommendations based on ACTUAL job market skills
        
        Args:
            skill_gap_analysis (Dict[str, Any]): Skill gap analysis with real LinkedIn data
            available_courses (List[Dict[str, Any]]): Available courses
            completed_courses (List[str]): User's completed courses
            
        Returns:
            List[Dict[str, Any]]: Course recommendations matched to job market demands
        """
        print("🎯 Matching courses to REAL job market demands from LinkedIn data...")

        # Prefer embedding search: it matches on meaning, so it works without skill tags
        semantic_recommendations = self._semantic_course_recommendations(skill_gap_analysis, completed_courses)
        if semantic_recommendations:
            return semantic_recommendations

        # Get missing skills from job market analysis (these are REAL skills from LinkedIn)
        missing_skills = skill_gap_analysis.get("missing_skills", [])

        if not missing_skills:
            print("⚠️ No missing skills identified, using fallback recommendations")
            return self._fallback_course_recommendations(skill_gap_analysis, available_courses, completed_courses)
        
        # Check if courses have skills - if not, use fallback
        sample_course = available_courses[0] if available_courses else {}
        if not sample_course.get("skills"):
            print("⚠️ Courses don't have skills extracted, using fallback recommendations")
            return self._fallback_course_recommendations(skill_gap_analysis, available_courses, completed_courses)
        
        print(f"📊 Job Market Analysis: Found {len(missing_skills)} skills needed from LinkedIn jobs")
        for skill in missing_skills[:5]:
            print(f"  - {skill['skill']} (Priority: {skill['priority']}, Frequency: {skill['frequency']})")
        
        # Score courses based on how well they match the ACTUAL job market skills
        course_scores = []
        completed_lower = set([course.lower() for course in completed_courses])
        
        for course in available_courses:
            course_code = course.get("course_code", "")
            
            # Skip completed courses
            if course_code.lower() in completed_lower:
                continue
            
            course_skills = course.get("skills", [])
            score = 0
            matched_skills = []
            highest_priority = "low"
            
            # Calculate score based on skill matching with job market data
            for missing_skill_info in missing_skills:
                job_skill = missing_skill_info["skill"]
                skill_priority = missing_skill_info["priority"]
                skill_frequency = missing_skill_info["frequency"]
                
                # Check if course teaches this job-required skill
                for course_skill in course_skills:
                    # Fuzzy matching: check if job skill is in course skill or vice versa
                    if (job_skill.lower() in course_skill.lower() or 
                        course_skill.lower() in job_skill.lower()):
                        
                        # Weight by priority and frequency from REAL job data
                        priority_weight = {
                            "critical": 10,
                            "high": 7,
                            "medium": 4,
                            "low": 2
                        }.get(skill_priority, 1)
                        
                        score += priority_weight * skill_frequency
                        matched_skills.append(job_skill)
                        
                        # Track highest priority skill matched
                        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
                        if priority_order.get(skill_priority, 4) < priority_order.get(highest_priority, 4):
                            highest_priority = skill_priority
            
            # Only include courses that match at least one job market skill
            if score > 0:
                course_scores.append({
                    "course": course,
                    "score": score,
                    "matched_skills": list(set(matched_skills)),  # Remove duplicates
                    "priority": highest_priority
                })
        
        # Sort by score (highest first)
        course_scores.sort(key=lambda x: (-x["score"], x["course"].get("course_code", "")))
        
        print(f"✅ Found {len(course_scores)} courses matching job market skills")
        
        # Build recommendations
        recommendations = []
        for course_score in course_scores[:6]:  # Top 6 courses
            course = course_score["course"]
            matched_skills = course_score["matched_skills"]
            priority = course_score["priority"]
            
            # Generate explanation based on matched skills
            if len(matched_skills) > 1:
                explanation = f"Teaches {len(matched_skills)} in-demand skills from LinkedIn jobs: {', '.join(matched_skills[:3])}{'...' if len(matched_skills) > 3 else ''}. These skills appear frequently in real {self._current_career_goal} job postings."
            else:
                explanation = f"Teaches {matched_skills[0]}, a {priority}-priority skill identified in real LinkedIn job postings for {self._current_career_goal}."
            
            recommendations.append({
                "course_code": course.get("course_code", ""),
                "title": course.get("title", ""),
                "description": course.get("description", ""),
                "skills_addressed": matched_skills[:5],  # Show matched skills
                "priority": priority,
                "explanation": explanation,
                "prerequisites": course.get("prerequisites", "None listed"),
                "semester_credit_hours": course.get("semester_credit_hours", "3"),
                "relevance_score": min(10, int(course_score["score"] / 5)),  # Normalize to 0-10
                "job_market_aligned": True,
                "total_course_skills": len(course.get("skills", []))
            })
        
        # If not enough courses found, add some fallback recommendations
        if len(recommendations) < 3:
            print("🔄 Adding fallback recommendations to reach minimum 3 courses...")
            fallback_recs = self._fallback_course_recommendations(skill_gap_analysis, available_courses, completed_courses)
            existing_codes = {rec["course_code"] for rec in recommendations}
            
            for fallback_rec in fallback_recs:
                if fallback_rec["course_code"] not in existing_codes and len(recommendations) < 6:
                    fallback_rec["job_market_aligned"] = False
                    recommendations.append(fallback_rec)
        
        print(f"📚 Final recommendation: {len(recommendations)} courses aligned with LinkedIn job market data")
        return recommendations
    
    def _semantic_course_recommendations(
        self,
        skill_gap_analysis: Dict[str, Any],
        completed_courses: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Recommend courses by embedding similarity between the career goal + missing
        skills and each course's title/description.

        Returns an empty list (so the caller falls back to keyword matching) when
        embeddings aren't built or Bedrock is unavailable.
        """
        catalog = self.course_catalog_agent
        if not catalog or not catalog.has_semantic_search():
            return []

        # Missing skills are already sorted by how often employers ask for them
        top_skills = [s["skill"] for s in skill_gap_analysis.get("missing_skills", [])[:8]]
        priority_by_skill = {s["skill"]: s["priority"] for s in skill_gap_analysis.get("missing_skills", [])}

        query = f"Career goal: {self._current_career_goal}."
        if top_skills:
            query += f" Required skills: {', '.join(top_skills)}."

        try:
            print(f"🧠 Semantic course search: {query}")
            results = catalog.semantic_search(query, top_k=6, exclude_codes=completed_courses)

            # Embed each skill separately to explain which skills a course covers
            label_skills = top_skills[:5]
            with ThreadPoolExecutor(max_workers=len(label_skills) or 1) as pool:
                skill_vectors = list(pool.map(catalog.embed_query, label_skills))
        except Exception as e:
            print(f"⚠️ Semantic search failed, falling back to keyword matching: {e}")
            return []

        if not results:
            return []

        best_similarity = results[0]["similarity"]
        recommendations = []
        for rank, result in enumerate(results):
            course = result["course"]
            course_vector = catalog.course_embeddings[result["index"]]

            # Top 3 skills closest to this course
            skill_sims = sorted(
                ((float(course_vector @ vec), skill) for skill, vec in zip(label_skills, skill_vectors)),
                reverse=True
            )
            matched_skills = [skill for _, skill in skill_sims[:3]]

            if matched_skills:
                priority = priority_by_skill.get(matched_skills[0], "medium")
                explanation = f"Course content closely matches {', '.join(matched_skills)}, skills that appear in real {self._current_career_goal} job postings."
            else:
                priority = "high" if rank < 2 else "medium"
                explanation = f"Course content is among the closest matches in the UTD catalog for a {self._current_career_goal} career."

            recommendations.append({
                "course_code": course.get("course_code", ""),
                "title": course.get("title", ""),
                "description": course.get("description", ""),
                "skills_addressed": matched_skills,
                "priority": priority,
                "explanation": explanation,
                "prerequisites": course.get("prerequisites") or "None listed",
                "semester_credit_hours": course.get("credits", "3"),
                "relevance_score": round(10 * result["similarity"] / best_similarity) if best_similarity > 0 else 0,
                "similarity": round(result["similarity"], 3),
                "job_market_aligned": bool(top_skills),
                "total_course_skills": len(matched_skills)
            })

        print(f"✅ Semantic search recommended {len(recommendations)} courses")
        return recommendations

    def _fallback_course_recommendations(
        self,
        skill_gap_analysis: Dict[str, Any],
        available_courses: List[Dict[str, Any]],
        completed_courses: List[str]
    ) -> List[Dict[str, Any]]:
        """Fallback course recommendations based on career goals when skills matching fails"""
        print("🔄 Using intelligent fallback course recommendations...")
        
        career_goal = self._current_career_goal.lower()
        recommendations = []
        
        # Convert completed courses to lowercase for comparison
        completed_lower = [course.lower() for course in completed_courses]
        
        # Career-specific course mappings
        career_course_mappings = {
            "data scientist": {
                "keywords": ["data", "statistics", "machine learning", "python", "analytics"],
                "departments": ["CS", "MATH", "STAT", "DATA"],
                "priority_courses": ["CS 3345", "CS 4352", "MATH 2414", "STAT 4351"]
            },
            "software engineer": {
                "keywords": ["programming", "software", "computer", "algorithms", "systems"],
                "departments": ["CS", "SE"],
                "priority_courses": ["CS 1337", "CS 2336", "CS 3345", "CS 4347"]
            },
            "data analyst": {
                "keywords": ["data", "analysis", "statistics", "business", "excel"],
                "departments": ["CS", "MATH", "STAT", "BUSI"],
                "priority_courses": ["CS 3345", "MATH 2414", "STAT 4351", "BUSI 3311"]
            },
            "product manager": {
                "keywords": ["business", "management", "strategy", "marketing", "economics"],
                "departments": ["BUSI", "MKT", "ECON", "CS"],
                "priority_courses": ["BUSI 3311", "MKT 3300", "ECON 2301", "CS 3345"]
            },
            "machine learning engineer": {
                "keywords": ["machine learning", "ai", "neural", "deep learning", "python"],
                "departments": ["CS", "MATH", "STAT"],
                "priority_courses": ["CS 4352", "CS 4347", "MATH 2414", "STAT 4351"]
            },
            "devops engineer": {
                "keywords": ["systems", "cloud", "infrastructure", "deployment", "automation"],
                "departments": ["CS", "SE"],
                "priority_courses": ["CS 4347", "CS 4352", "CS 4348", "CS 4354"]
            },
            "business analyst": {
                "keywords": ["business", "analysis", "finance", "accounting", "economics"],
                "departments": ["BUSI", "ACCT", "ECON", "FIN"],
                "priority_courses": ["BUSI 3311", "ACCT 2301", "ECON 2301", "FIN 3320"]
            },
            "financial analyst": {
                "keywords": ["finance", "accounting", "economics", "investment", "financial"],
                "departments": ["FIN", "ACCT", "ECON", "BUSI"],
                "priority_courses": ["FIN 3320", "ACCT 2301", "ECON 2301", "BUSI 3311"]
            }
        }
        
        # Find matching career pattern
        career_config = None
        for pattern, config in career_course_mappings.items():
            if pattern in career_goal or any(keyword in career_goal for keyword in config["keywords"]):
                career_config = config
                break
        
        if not career_config:
            # Generic fallback for unknown careers
            career_config = {
                "keywords": ["computer", "business", "analysis"],
                "departments": ["CS", "BUSI"],
                "priority_courses": ["CS 1337", "BUSI 3311", "MATH 2414"]
            }
        
        print(f"🎯 Career pattern matched: {career_goal} -> {career_config['keywords']}")
        
        # Find courses by department and keywords
        matching_courses = []
        for course in available_courses:
            course_code = course.get("course_code", "").upper()
            course_title = course.get("title", "").lower()
            course_desc = course.get("description", "").lower()
            
            # Skip completed courses
            if course_code.lower() in completed_lower:
                continue
            
            # Check department match
            dept_match = any(dept in course_code for dept in career_config["departments"])
            
            # Check keyword match in title or description
            keyword_match = any(keyword in course_title or keyword in course_desc 
                              for keyword in career_config["keywords"])
            
            # Check priority courses
            priority_match = course_code in career_config["priority_courses"]
            
            if dept_match or keyword_match or priority_match:
                score = 0
                if priority_match:
                    score += 10
                if dept_match:
                    score += 5
                if keyword_match:
                    score += 3
                
                matching_courses.append((course, score))
        
        # Sort by score and take top courses
        matching_courses.sort(key=lambda x: x[1], reverse=True)
        
        for course, score in matching_courses[:6]:
            # Determine priority based on score
            if score >= 10:
                priority = "high"
            elif score >= 5:
                priority = "medium"
            else:
                priority = "low"
            
            # Generate skills addressed based on career goal
            skills_addressed = []
            if "data" in career_goal:
                skills_addressed = ["Data Analysis", "Statistics", "Python"]
            elif "software" in career_goal:
                skills_addressed = ["Programming", "Algorithms", "Software Development"]
            elif "business" in career_goal or "manager" in career_goal:
                skills_addressed = ["Business Analysis", "Management", "Strategy"]
            else:
                skills_addressed = ["Technical Skills", "Problem Solving", "Analysis"]
            
            recommendation = {
                "course_code": course.get("course_code", ""),
                "title": course.get("title", ""),
                "description": course.get("description", ""),
                "skills_addressed": skills_addressed,
                "priority": priority,
                "explanation": f"This course is essential for {self._current_career_goal} careers, covering key concepts and practical skills you'll need in the industry.",
                "prerequisites": course.get("prerequisites", "None listed"),
                "semester_credit_hours": course.get("credits", "3"),
                "relevance_score": min(10, score),
                "job_market_aligned": True,
                "total_course_skills": len(skills_addressed)
            }
            
            recommendations.append(recommendation)
        
        print(f"✅ Generated {len(recommendations)} fallback course recommendations")
        return recommendations
    
    def _create_learning_path(
        self,
        course_recommendations: List[Dict[str, Any]],
        current_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Create a personalized learning path with semester-by-semester progression
        
        Args:
            course_recommendations (List[Dict[str, Any]]): Course recommendations
            current_skills (List[str]): User's current skills
            
        Returns:
            Dict[str, Any]: Learning path with semesters, rationale, and milestones
        """
        if not course_recommendations:
            return {
                "semesters": [],
                "rationale": "No course recommendations available to create a learning path.",
                "milestones": []
            }
        
        # Group courses by priority (including "critical" priority)
        critical_priority = [c for c in course_recommendations if c.get("priority") == "critical"]
        high_priority = [c for c in course_recommendations if c.get("priority") == "high"]
        medium_priority = [c for c in course_recommendations if c.get("priority") == "medium"]
        low_priority = [c for c in course_recommendations if c.get("priority") == "low"]
        
        semesters = []
        semester_count = 1
        courses_per_semester = 2
        
        # Create semesters starting with critical and high priority courses
        all_courses = critical_priority + high_priority + medium_priority + low_priority
        
        # Calculate total credit hours
        total_credit_hours = sum(int(c.get("semester_credit_hours", "3")) for c in all_courses)
        
        for i in range(0, len(all_courses), courses_per_semester):
            semester_courses = all_courses[i:i + courses_per_semester]
            
            if semester_courses:
                semester_name = f"Semester {semester_count}"
                semester_credits = sum(int(c.get("semester_credit_hours", "3")) for c in semester_courses)
                
                semesters.append({
                    "semester_name": semester_name,
                    "courses": [
                        {
                            "course_code": course["course_code"],
                            "title": course["title"],
                            "priority": course["priority"],
                            "skills_gained": course.get("skills_addressed", [])[:3],
                            "credit_hours": course.get("semester_credit_hours", "3")
                        }
                        for course in semester_courses
                    ],
                    "total_credits": semester_credits,
                    "focus_area": self._determine_semester_focus(semester_courses)
                })
                semester_count += 1
        
        # Create milestones
        milestones = []
        if critical_priority or high_priority:
            milestones.append({
                "name": "Foundation Phase",
                "description": "Complete critical and high-priority courses to build strong fundamentals",
                "semesters": list(range(1, min(3, len(semesters) + 1)))
            })
        if medium_priority:
            milestones.append({
                "name": "Intermediate Phase",
                "description": "Develop specialized skills through medium-priority courses",
                "semesters": list(range(max(2, len(critical_priority) + len(high_priority) // 2), len(semesters)))
            })
        if low_priority:
            milestones.append({
                "name": "Advanced Phase",
                "description": "Master additional skills for career advancement",
                "semesters": [len(semesters)]
            })
        
        # Enhanced rationale
        rationale = f"""
        This learning path is strategically designed to build your expertise systematically:
        
        📊 Course Distribution:
        • Critical priority: {len(critical_priority)} courses (immediate skills needed)
        • High priority: {len(high_priority)} courses (core competencies)
        • Medium priority: {len(medium_priority)} courses (specialized knowledge)
        • Low priority: {len(low_priority)} courses (complementary skills)
        
        🎯 Learning Strategy:
        • Each semester includes {courses_per_semester} courses for optimal learning pace
        • Total credit hours: {total_credit_hours}
        • Estimated completion: {len(semesters)} semesters ({len(semesters) / 2:.1f} years)
        • Progressive skill building from fundamentals to advanced topics
        
        💡 Why This Path Works:
        Critical skills are addressed immediately to ensure job readiness, followed by
        specialized courses that align with your career goals. The pace allows for
        deep learning and practical application of each skill before moving forward.
        """
        
        return {
            "semesters": semesters,
            "rationale": rationale.strip(),
            "total_semesters": len(semesters),
            "total_courses": len(course_recommendations),
            "total_credit_hours": total_credit_hours,
            "estimated_years": round(len(semesters) / 2, 1),
            "milestones": milestones,
            "completion_timeline": f"{len(semesters)} semesters ({len(semesters) / 2:.1f} years)"
        }
    
    def _create_curriculum_comparison(
        self,
        job_market_data: Dict[str, Any],
        course_recommendations: List[Dict[str, Any]],
        skill_gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a detailed comparison between job market requirements and course curriculum
        
        Args:
            job_market_data (Dict[str, Any]): Real job market data from LinkedIn
            course_recommendations (List[Dict[str, Any]]): Recommended courses
            skill_gap_analysis (Dict[str, Any]): Skill gap analysis
            
        Returns:
            Dict[str, Any]: Detailed comparison showing alignment between jobs and courses
        """
        job_skills = job_market_data.get("skills", {})
        missing_skills = skill_gap_analysis.get("missing_skills", [])
        
        # Create skill-to-course mapping
        skill_coverage_map = {}
        for skill_info in missing_skills:
            skill = skill_info["skill"]
            skill_coverage_map[skill] = {
                "job_priority": skill_info["priority"],
                "job_frequency": skill_info["frequency"],
                "courses_teaching": [],
                "covered": False
            }
        
        # Map courses to skills
        for course in course_recommendations:
            course_skills = course.get("skills_addressed", [])
            for course_skill in course_skills:
                # Check which job skills this course addresses
                for job_skill in skill_coverage_map.keys():
                    if (job_skill.lower() in course_skill.lower() or 
                        course_skill.lower() in job_skill.lower()):
                        skill_coverage_map[job_skill]["courses_teaching"].append({
                            "course_code": course.get("course_code"),
                            "course_title": course.get("title"),
                            "priority": course.get("priority")
                        })
                        skill_coverage_map[job_skill]["covered"] = True
        
        # Calculate coverage statistics
        covered_skills = sum(1 for skill_data in skill_coverage_map.values() if skill_data["covered"])
        uncovered_skills = len(skill_coverage_map) - covered_skills
        coverage_percentage = (covered_skills / len(skill_coverage_map) * 100) if len(skill_coverage_map) > 0 else 0
        
        # Identify well-covered vs poorly-covered skills
        well_covered_skills = []
        poorly_covered_skills = []
        uncovered_skill_list = []
        
        for skill, data in skill_coverage_map.items():
            course_count = len(data["courses_teaching"])
            if course_count >= 2:
                well_covered_skills.append({
                    "skill": skill,
                    "job_priority": data["job_priority"],
                    "courses_count": course_count,
                    "courses": data["courses_teaching"]
                })
            elif course_count == 1:
                poorly_covered_skills.append({
                    "skill": skill,
                    "job_priority": data["job_priority"],
                    "course": data["courses_teaching"][0]
                })
            else:
                uncovered_skill_list.append({
                    "skill": skill,
                    "job_priority": data["job_priority"],
                    "job_frequency": data["job_frequency"]
                })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        well_covered_skills.sort(key=lambda x: priority_order.get(x["job_priority"], 4))
        poorly_covered_skills.sort(key=lambda x: priority_order.get(x["job_priority"], 4))
        uncovered_skill_list.sort(key=lambda x: (priority_order.get(x["job_priority"], 4), -x["job_frequency"]))
        
        # Generate comparison summary
        summary = f"""
        📊 Job Market to Course Curriculum Alignment Analysis
        
        ✅ Coverage: {covered_skills}/{len(skill_coverage_map)} job-required skills ({coverage_percentage:.1f}%)
        
        🎯 Skills Well-Covered by Curriculum: {len(well_covered_skills)} skills
        ⚠️  Skills Partially Covered: {len(poorly_covered_skills)} skills
        ❌ Skills Not Covered: {len(uncovered_skill_list)} skills
        
        📚 Course-to-Job Alignment Score: {coverage_percentage:.0f}/100
        """
        
        # Generate recommendations for gaps
        gap_recommendations = []
        if uncovered_skill_list:
            gap_recommendations.append(
                f"Consider self-study or external resources for {len(uncovered_skill_list)} uncovered skills: {', '.join([s['skill'] for s in uncovered_skill_list[:3]])}..."
            )
        if poorly_covered_skills:
            gap_recommendations.append(
                f"{len(poorly_covered_skills)} skills have limited course coverage - consider additional projects or certifications"
            )
        if coverage_percentage >= 80:
            gap_recommendations.append(
                "Excellent alignment! The recommended courses cover most job requirements"
            )
        elif coverage_percentage >= 60:
            gap_recommendations.append(
                "Good alignment. Supplement with practical projects to fill remaining gaps"
            )
        else:
            gap_recommendations.append(
                "Moderate alignment. Consider additional learning resources alongside courses"
            )
        
        return {
            "summary": summary.strip(),
            "coverage_percentage": round(coverage_percentage, 1),
            "covered_skills_count": covered_skills,
            "total_required_skills": len(skill_coverage_map),
            "well_covered_skills": well_covered_skills[:5],  # Top 5
            "poorly_covered_skills": poorly_covered_skills[:5],  # Top 5
            "uncovered_skills": uncovered_skill_list[:5],  # Top 5
            "alignment_score": round(coverage_percentage),
            "gap_recommendations": gap_recommendations,
            "skill_to_course_map": [
                {
                    "skill": skill,
                    "job_priority": data["job_priority"],
                    "job_frequency": data["job_frequency"],
                    "covered": data["covered"],
                    "courses": data["courses_teaching"]
                }
                for skill, data in sorted(
                    skill_coverage_map.items(),
                    key=lambda x: (priority_order.get(x[1]["job_priority"], 4), -x[1]["job_frequency"])
                )
            ][:10]  # Top 10 most important skills
        }
    
    def _determine_semester_focus(self, courses: List[Dict[str, Any]]) -> str:
        """
        Determine the focus area for a semester based on course skills
        
        Args:
            courses (List[Dict[str, Any]]): Courses in the semester
            
        Returns:
            str: Focus area description
        """
        all_skills = []
        for course in courses:
            all_skills.extend(course.get("skills_addressed", []))
        
        if not all_skills:
            return "General Skills"
        
        # Determine primary focus based on common skill patterns
        skill_str = " ".join(all_skills).lower()
        
        if any(term in skill_str for term in ["python", "programming", "java"]):
            return "Programming Fundamentals"
        elif any(term in skill_str for term in ["data", "analytics", "statistics"]):
            return "Data Analysis & Statistics"
        elif any(term in skill_str for term in ["machine learning", "ai", "ml"]):
            return "Machine Learning & AI"
        elif any(term in skill_str for term in ["database", "sql"]):
            return "Database Management"
        elif any(term in skill_str for term in ["web", "frontend", "backend"]):
            return "Web Development"
        elif any(term in skill_str for term in ["algorithms", "data structures"]):
            return "Computer Science Fundamentals"
        else:
            return "Core Technical Skills"
    
    def _extract_market_insights(
        self,
        job_market_data: Dict[str, Any],
        skill_gap_analysis: Dict[str, Any],
        career_goal: str
    ) -> Dict[str, Any]:
        """
        Extract job market trends and hot skills based on market analysis
        
        Args:
            job_market_data (Dict[str, Any]): Job market data from Job Market Agent
            skill_gap_analysis (Dict[str, Any]): Skill gap analysis results
            career_goal (str): User's career goal
            
        Returns:
            Dict[str, Any]: Market insights including trends and hot skills
        """
        # Extract skills data
        skills_data = job_market_data.get("skills", {})
        
        # Identify hot skills (skills with high frequency/demand)
        hot_skills = []
        for skill, frequency in sorted(skills_data.items(), key=lambda x: x[1], reverse=True):
            demand_level = "Very High" if frequency >= 4 else "High" if frequency >= 3 else "Medium"
            hot_skills.append({
                "skill": skill,
                "demand": demand_level,
                "frequency": frequency,
                "in_demand": frequency >= 3
            })
        
        # Limit to top 10 hot skills
        hot_skills = hot_skills[:10]
        
        # Extract job trends from market data
        job_trends = job_market_data.get("trends", [])
        
        # Determine career-specific trends if not provided
        if not job_trends:
            job_trends = self._get_career_specific_trends(career_goal)
        
        # Calculate market health indicators
        total_jobs = job_market_data.get("job_count", 0)
        market_health = "Excellent" if total_jobs >= 100 else "Good" if total_jobs >= 50 else "Fair" if total_jobs >= 10 else "Limited"
        
        # Get salary insights
        salary_data = job_market_data.get("salaries", {})
        salary_insights = {
            "average": salary_data.get("overall_average", 0),
            "range": {
                "min": salary_data.get("average_min", 0),
                "max": salary_data.get("average_max", 0)
            },
            "outlook": "Competitive" if salary_data.get("overall_average", 0) >= 80000 else "Good" if salary_data.get("overall_average", 0) >= 60000 else "Moderate"
        }
        
        # Identify emerging vs established skills
        emerging_skills = []
        established_skills = []
        
        for skill_info in hot_skills:
            skill = skill_info["skill"]
            # Simple heuristic: AI/ML, Cloud, DevOps related are "emerging"
            if any(term in skill.lower() for term in ["ai", "ml", "machine learning", "cloud", "docker", "kubernetes", "react", "blockchain", "devops"]):
                emerging_skills.append(skill)
            else:
                established_skills.append(skill)
        
        # Generate market summary
        market_summary = self._generate_market_summary(
            career_goal,
            total_jobs,
            len(hot_skills),
            market_health,
            salary_insights
        )
        
        return {
            "hot_skills": hot_skills,
            "job_trends": job_trends,
            "market_health": market_health,
            "total_opportunities": total_jobs,
            "salary_insights": salary_insights,
            "emerging_skills": emerging_skills[:5],  # Top 5 emerging
            "established_skills": established_skills[:5],  # Top 5 established
            "market_summary": market_summary,
            "recommendation": self._generate_market_recommendation(market_health, skill_gap_analysis)
        }
    
    def _get_career_specific_trends(self, career_goal: str) -> List[str]:
        """
        Get career-specific job market trends
        
        Args:
            career_goal (str): User's career goal
            
        Returns:
            List[str]: List of relevant job market trends
        """
        goal_lower = career_goal.lower()
        
        # Trend mappings for different career paths
        if any(term in goal_lower for term in ["data scientist", "data analyst", "machine learning"]):
            return [
                "Growing demand for AI/ML expertise",
                "Increasing need for data visualization skills",
                "Cloud-based data platforms gaining traction",
                "Real-time data processing becoming standard",
                "AutoML and MLOps emerging as key skills"
            ]
        elif any(term in goal_lower for term in ["software engineer", "developer", "programmer"]):
            return [
                "Remote-first development positions increasing",
                "Cloud-native application development trending",
                "DevOps and CI/CD skills highly valued",
                "Full-stack developers in high demand",
                "Microservices architecture becoming standard"
            ]
        elif any(term in goal_lower for term in ["financial analyst", "finance", "investment"]):
            return [
                "FinTech integration accelerating",
                "Data-driven financial analysis expected",
                "Regulatory technology (RegTech) growing",
                "Cryptocurrency and blockchain knowledge valued",
                "ESG (Environmental, Social, Governance) focus increasing"
            ]
        elif any(term in goal_lower for term in ["neuroscience", "neuroscientist", "cognitive"]):
            return [
                "Computational neuroscience expanding rapidly",
                "Brain-computer interfaces gaining interest",
                "Neuroimaging technology advancing",
                "AI applications in neuroscience growing",
                "Interdisciplinary research opportunities increasing"
            ]
        elif any(term in goal_lower for term in ["marketing", "digital marketing"]):
            return [
                "Data-driven marketing strategies essential",
                "Social media expertise highly valued",
                "Marketing automation tools standard",
                "Content marketing and SEO critical",
                "Customer analytics becoming key"
            ]
        else:
            # Generic tech trends
            return [
                "Digital transformation accelerating across industries",
                "Remote work opportunities expanding",
                "Data literacy becoming essential",
                "Continuous learning valued by employers",
                "Cross-functional skills in demand"
            ]
    
    def _generate_market_summary(
        self,
        career_goal: str,
        total_jobs: int,
        hot_skills_count: int,
        market_health: str,
        salary_insights: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive market summary
        
        Args:
            career_goal (str): User's career goal
            total_jobs (int): Total job opportunities
            hot_skills_count (int): Number of hot skills identified
            market_health (str): Market health indicator
            salary_insights (Dict[str, Any]): Salary information
            
        Returns:
            str: Market summary text
        """
        avg_salary = salary_insights.get("average", 0)
        salary_range = salary_insights.get("range", {})
        
        summary = f"""
        The job market for {career_goal} is currently {market_health.lower()}, with {total_jobs} opportunities identified.
        
        💼 Market Overview:
        • Current openings: {total_jobs} positions
        • Hot skills in demand: {hot_skills_count} key skills
        • Market health: {market_health}
        • Salary outlook: {salary_insights.get("outlook", "Good")}
        
        💰 Compensation Insights:
        • Average salary: ${avg_salary:,} per year
        • Typical range: ${salary_range.get("min", 0):,} - ${salary_range.get("max", 0):,}
        • Market positioning: {salary_insights.get("outlook", "Competitive")}
        
        📊 Market Dynamics:
        The current market shows {"strong" if market_health in ["Excellent", "Good"] else "moderate"} demand for 
        professionals in this field. Developing the identified hot skills will significantly improve your 
        competitiveness in the job market.
        """
        
        return summary.strip()
    
    def _generate_market_recommendation(
        self,
        market_health: str,
        skill_gap_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate market-based recommendations for the user
        
        Args:
            market_health (str): Market health indicator
            skill_gap_analysis (Dict[str, Any]): Skill gap analysis results
            
        Returns:
            str: Personalized market recommendation
        """
        readiness_level = skill_gap_analysis.get("readiness_level", "Beginner")
        skills_to_develop = skill_gap_analysis.get("skills_to_develop", 0)
        
        if market_health == "Excellent" and readiness_level in ["Excellent", "Good"]:
            return "The market is strong and you're well-positioned. Focus on advanced skills and consider applying for positions while continuing your education."
        elif market_health == "Excellent" and skills_to_develop > 5:
            return "Excellent market opportunities exist! Prioritize developing your critical skills first to become competitive quickly."
        elif market_health == "Good":
            return "The market is healthy with good opportunities. Continue building your skills systematically to maximize your chances."
        elif market_health == "Fair":
            return "The market is competitive. Focus on developing niche skills and building a strong portfolio to stand out."
        else:
            return "The market is limited but opportunities exist. Consider broadening your skill set and exploring related career paths while building expertise."

    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent

        Returns:
            List[str]: List of capability descriptions
        """
        return [
            "Takes user career goals and coordinates with other agents",
            "Analyzes job requirements vs. available coursework",
            "Generates personalized course recommendations with explanations",
            "Creates skill gap analysis based on real job market data",
            "Develops semester-by-semester learning paths",
            "Coordinates with Job Market Agent for real job requirements",
            "Coordinates with Course Catalog Agent for available courses",
            "Provides priority-based course sequencing",
            "Estimates completion time and workload"
        ]
