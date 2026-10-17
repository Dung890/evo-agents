"""
Career LLM Service - Lightweight AWS Bedrock integration for relevant career guidance
Uses the cheapest available model for cost-effective career matching
"""

import json
import boto3
from typing import Dict, List, Any, Optional
from src.config.config import AWSConfig

class CareerLLMService:
    def __init__(self):
        self.config = AWSConfig()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client"""
        try:
            self.client = self.config.get_bedrock_client()
            print("✅ Career LLM Service initialized with AWS Bedrock")
        except Exception as e:
            print(f"⚠️ Failed to initialize Bedrock client: {e}")
            self.client = None
    
    def analyze_career_skills_match(self, career_goal: str, available_courses: List[Dict], job_requirements: Dict) -> Dict[str, Any]:
        """
        Use LLM to analyze career goal and recommend relevant courses
        
        Args:
            career_goal: Target career (e.g., "Financial Analyst")
            available_courses: List of UTD courses
            job_requirements: Job market requirements and skills
            
        Returns:
            Dict with relevant course recommendations and explanations
        """
        # For now, use improved fallback system for consistent results
        # This ensures we get relevant course recommendations while LLM credentials are being configured
        print("🤖 Using improved intelligent fallback system for career matching")
        return self._fallback_career_analysis(career_goal, available_courses, job_requirements)
        
        # Original LLM code (commented out for testing)
        # if not self.client:
        #     return self._fallback_career_analysis(career_goal, available_courses, job_requirements)
        # 
        # try:
        #     # Create a focused prompt for career matching
        #     prompt = self._create_career_matching_prompt(career_goal, available_courses, job_requirements)
        #     
        #     # Use Claude 3 Haiku (cheapest model) for cost efficiency
        #     response = self.client.invoke_model(
        #         modelId="anthropic.claude-3-haiku-20240307-v1:0",  # Cheapest Claude model
        #         body=json.dumps({
        #             "anthropic_version": "bedrock-2023-05-31",
        #             "max_tokens": 1000,  # Keep tokens low for cost
        #             "temperature": 0.3,   # Lower temperature for more focused responses
        #             "messages": [
        #                 {
        #                     "role": "user",
        #                     "content": prompt
        #                 }
        #             ]
        #         })
        #     )
        #     
        #     response_body = json.loads(response['body'].read())
        #     llm_output = response_body['content'][0]['text']
        #     
        #     # Parse LLM response into structured format
        #     return self._parse_llm_response(llm_output, career_goal)
        #     
        # except Exception as e:
        #     print(f"❌ LLM analysis failed: {e}")
        #     return self._fallback_career_analysis(career_goal, available_courses, job_requirements)
    
    def _create_career_matching_prompt(self, career_goal: str, courses: List[Dict], job_requirements: Dict) -> str:
        """Create a focused prompt for career matching"""
        
        # Extract relevant course info (limit to reduce token cost)
        course_info = []
        for course in courses[:20]:  # Limit to 20 courses to reduce tokens
            course_info.append(f"- {course.get('course_code', 'N/A')}: {course.get('title', 'N/A')} (Skills: {', '.join(course.get('skills', [])[:3])})")
        
        # Extract job skills (limit to top skills)
        job_skills = list(job_requirements.get('skills', {}).keys())[:10]
        
        prompt = f"""You are a career counselor helping students choose relevant courses for their career goal.

CAREER GOAL: {career_goal}

TOP JOB MARKET SKILLS NEEDED:
{', '.join(job_skills) if job_skills else 'General business and analytical skills'}

AVAILABLE UTD COURSES:
{chr(10).join(course_info[:15])}  

TASK: Recommend the TOP 3-5 most relevant courses for becoming a {career_goal}. 

REQUIREMENTS:
1. Only recommend courses that are DIRECTLY relevant to {career_goal}
2. Focus on courses that teach skills needed for {career_goal}
3. Prioritize business, finance, economics, statistics, and data analysis courses for financial roles
4. Avoid irrelevant technical courses (like machine learning for finance unless specifically relevant)

RESPONSE FORMAT (JSON):
{{
  "recommended_courses": [
    {{
      "course_code": "COURSE_CODE",
      "relevance_score": 9,
      "explanation": "Why this course is essential for {career_goal}",
      "skills_gained": ["skill1", "skill2"]
    }}
  ],
  "career_path_summary": "Brief summary of how these courses prepare for {career_goal}"
}}

Respond ONLY with valid JSON."""

        return prompt
    
    def _parse_llm_response(self, llm_output: str, career_goal: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from LLM response
            start_idx = llm_output.find('{')
            end_idx = llm_output.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = llm_output[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                return {
                    "success": True,
                    "career_goal": career_goal,
                    "llm_recommendations": parsed_response.get("recommended_courses", []),
                    "career_summary": parsed_response.get("career_path_summary", ""),
                    "source": "aws_bedrock_claude_haiku"
                }
            else:
                raise ValueError("No JSON found in LLM response")
                
        except Exception as e:
            print(f"❌ Failed to parse LLM response: {e}")
            return self._fallback_career_analysis(career_goal, [], {})
    
    def _fallback_career_analysis(self, career_goal: str, courses: List[Dict], job_requirements: Dict) -> Dict[str, Any]:
        """Fallback analysis when LLM is unavailable"""
        print("🔄 Using fallback career analysis (no LLM)")
        
        # Define career-specific course mappings with detailed keywords
        career_course_mappings = {
            "financial analyst": {
                "prefixes": ["FIN", "ACCT", "ECON", "STAT", "BA"],
                "keywords": ["finance", "accounting", "economics", "financial", "investment", "business", "statistics", "portfolio", "valuation"]
            },
            "data scientist": {
                "prefixes": ["CS", "STAT", "MATH", "BA", "DATA"],
                "keywords": ["statistics", "data", "analytics", "machine learning", "programming", "mathematics", "mining", "modeling", "python", "r"]
            },
            "software engineer": {
                "prefixes": ["CS", "SE", "ENGR"],
                "keywords": ["programming", "software", "computer", "algorithms", "data structures", "java", "python", "web", "systems"]
            },
            "business analyst": {
                "prefixes": ["BA", "STAT", "ECON", "ACCT", "MIS"],
                "keywords": ["business", "analytics", "statistics", "economics", "analysis", "intelligence", "data", "reporting"]
            },
            "marketing analyst": {
                "prefixes": ["MKTG", "BA", "STAT", "COMM"],
                "keywords": ["marketing", "business", "analytics", "statistics", "analysis", "consumer", "digital", "social media"]
            },
            "neuroscientist": {
                "prefixes": ["NSC", "BIOL", "PSYC", "CHEM", "PHYS"],
                "keywords": ["neuroscience", "brain", "cognitive", "neural", "biology", "psychology", "neurology", "behavior", "perception"]
            },
            "neuro scientist": {
                "prefixes": ["NSC", "BIOL", "PSYC", "CHEM", "PHYS"],
                "keywords": ["neuroscience", "brain", "cognitive", "neural", "biology", "psychology", "neurology", "behavior", "perception"]
            },
            "data engineer": {
                "prefixes": ["CS", "DATA", "MIS", "ENGR"],
                "keywords": ["data", "database", "engineering", "pipeline", "etl", "sql", "nosql", "cloud", "distributed"]
            },
            "devops engineer": {
                "prefixes": ["CS", "SE", "SYSM", "ENGR"],
                "keywords": ["devops", "cloud", "infrastructure", "automation", "ci/cd", "kubernetes", "docker", "aws", "systems"]
            },
            "operations manager": {
                "prefixes": ["OPRE", "MGMT", "BA", "STAT"],
                "keywords": ["operations", "management", "supply chain", "logistics", "process", "optimization", "quality"]
            },
            "investment analyst": {
                "prefixes": ["FIN", "ECON", "ACCT", "STAT"],
                "keywords": ["investment", "finance", "portfolio", "securities", "valuation", "financial markets", "risk"]
            },
            "management consultant": {
                "prefixes": ["MGMT", "BA", "ECON", "STAT"],
                "keywords": ["management", "consulting", "strategy", "business", "analytics", "organizational", "leadership"]
            }
        }
        
        career_lower = career_goal.lower()
        relevant_config = None
        matched_pattern = None
        
        # Find matching career patterns (prioritize exact matches)
        for career_pattern, config in career_course_mappings.items():
            # First try exact match
            if career_pattern == career_lower:
                relevant_config = config
                matched_pattern = career_pattern
                break
            # Then try substring match (e.g., "financial analyst" in "I want to become a financial analyst")
            elif career_pattern in career_lower:
                relevant_config = config
                matched_pattern = career_pattern
                break
        
        if not relevant_config:
            matched_pattern = "default"
            relevant_config = {
                "prefixes": ["BA", "STAT", "ECON"],
                "keywords": ["business", "statistics", "economics"]
            }
        
        
        # Filter courses by relevance using both prefixes and keywords
        relevant_courses = []
        for course in courses:
            course_code = course.get('course_code', '')
            course_title = course.get('title', '').lower()
            course_description = course.get('description', '').lower()
            
            relevance_score = 0
            match_reason = ""
            
            # Check if course matches career-relevant prefixes (highest priority)
            if any(prefix.lower() in course_code.lower() for prefix in relevant_config["prefixes"]):
                relevance_score = 9
                match_reason = "prefix_match"
            
            # Check if course title/description contains relevant keywords
            elif any(keyword in course_title or keyword in course_description for keyword in relevant_config["keywords"]):
                relevance_score = 8
                match_reason = "keyword_match"
            
            # Check for general business/analytical courses
            elif any(keyword in course_title for keyword in ['business', 'statistics', 'analysis', 'economics']):
                relevance_score = 6
                match_reason = "general_match"
            
            if relevance_score > 0:
                # Create more specific explanations based on career goal
                explanation = self._generate_explanation(career_lower, course_code, course_title, career_goal)

                
                relevant_courses.append({
                    "course_code": course_code,
                    "title": course.get('title', ''),
                    "relevance_score": relevance_score,
                    "explanation": explanation,
                    "skills_gained": course.get('skills', [])[:3]
                })
        
        # Sort by relevance and take top 5
        relevant_courses.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            "success": True,
            "career_goal": career_goal,
            "llm_recommendations": relevant_courses[:5],
            "career_summary": f"These courses provide essential skills and knowledge for pursuing a career as a {career_goal}",
            "source": "fallback_analysis"
        }
    
    def _generate_explanation(self, career_lower: str, course_code: str, course_title: str, career_goal: str) -> str:
        """Generate career-specific explanations for course recommendations"""
        course_code_lower = course_code.lower()
        
        # Financial Analyst explanations
        if "financial analyst" in career_lower or "investment analyst" in career_lower:
            if "fin" in course_code_lower or "finance" in course_title:
                return f"Essential finance course for {career_goal} - covers financial analysis and corporate finance principles."
            elif "acct" in course_code_lower or "accounting" in course_title:
                return f"Critical accounting foundation for {career_goal} - essential for financial statement analysis."
            elif "econ" in course_code_lower or "economics" in course_title:
                return f"Economic principles course for {career_goal} - provides market analysis foundation."
            elif "stat" in course_code_lower or "statistics" in course_title:
                return f"Statistical analysis course for {career_goal} - essential for data-driven financial decisions."
            else:
                return f"Relevant business course for {career_goal} - builds analytical and business skills."
        
        # Neuroscientist/Neuro Scientist explanations
        elif "neuro" in career_lower or "neuroscience" in career_lower:
            if "nsc" in course_code_lower or "neuroscience" in course_title:
                return f"Core neuroscience course for {career_goal} - fundamental for understanding brain function and neural systems."
            elif "biol" in course_code_lower or "biology" in course_title:
                return f"Essential biology foundation for {career_goal} - provides understanding of cellular and molecular mechanisms."
            elif "psyc" in course_code_lower or "psychology" in course_title:
                return f"Psychology course for {career_goal} - bridges understanding between brain and behavior."
            elif "chem" in course_code_lower or "chemistry" in course_title:
                return f"Chemistry foundation for {career_goal} - essential for understanding molecular neuroscience."
            elif "phys" in course_code_lower or "physics" in course_title:
                return f"Physics course for {career_goal} - important for understanding neural signaling and biophysics."
            else:
                return f"Relevant science course for {career_goal} - supports comprehensive understanding of neuroscience."
        
        # Data Scientist/Data Engineer explanations
        elif "data" in career_lower:
            if "stat" in course_code_lower or "statistics" in course_title:
                return f"Critical statistics course for {career_goal} - essential for data analysis and modeling."
            elif "cs" in course_code_lower or "programming" in course_title or "software" in course_title:
                return f"Programming foundation for {career_goal} - key for data manipulation and algorithm implementation."
            elif "machine learning" in course_title or "ml" in course_code_lower:
                return f"Machine learning course for {career_goal} - core competency for advanced data analysis."
            elif "database" in course_title or "data" in course_title:
                return f"Data management course for {career_goal} - essential for working with large datasets."
            else:
                return f"Technical course for {career_goal} - builds analytical and computational skills."
        
        # Software/DevOps Engineer explanations
        elif "software" in career_lower or "devops" in career_lower or "engineer" in career_lower:
            if "cs" in course_code_lower or "programming" in course_title:
                return f"Core programming course for {career_goal} - fundamental software development skills."
            elif "algorithm" in course_title or "data structure" in course_title:
                return f"Essential algorithms course for {career_goal} - critical for efficient software design."
            elif "system" in course_title or "cloud" in course_title:
                return f"Systems course for {career_goal} - important for infrastructure and deployment."
            else:
                return f"Technical course for {career_goal} - enhances software engineering capabilities."
        
        # Marketing Analyst explanations
        elif "marketing" in career_lower:
            if "mktg" in course_code_lower or "marketing" in course_title:
                return f"Marketing course for {career_goal} - core marketing principles and strategies."
            elif "stat" in course_code_lower or "analytics" in course_title:
                return f"Analytics course for {career_goal} - essential for data-driven marketing decisions."
            elif "comm" in course_code_lower or "communication" in course_title:
                return f"Communication course for {career_goal} - important for effective marketing messaging."
            else:
                return f"Business course for {career_goal} - supports marketing strategy and analysis."
        
        # Business/Management roles
        elif any(term in career_lower for term in ["business", "management", "operations", "consultant"]):
            if "mgmt" in course_code_lower or "management" in course_title:
                return f"Management course for {career_goal} - develops leadership and organizational skills."
            elif "opre" in course_code_lower or "operations" in course_title:
                return f"Operations course for {career_goal} - essential for process improvement and efficiency."
            elif "ba" in course_code_lower or "analytics" in course_title:
                return f"Business analytics course for {career_goal} - supports data-driven decision making."
            elif "econ" in course_code_lower or "economics" in course_title:
                return f"Economics course for {career_goal} - provides market and business environment understanding."
            else:
                return f"Business course for {career_goal} - builds professional and analytical capabilities."
        
        # Default explanation
        else:
            return f"This course provides foundational knowledge relevant to {career_goal}"
    
    def generate_learning_path_explanation(self, career_goal: str, recommended_courses: List[Dict]) -> str:
        """Generate a brief explanation of the learning path"""
        if not self.client:
            return f"This learning path is designed to prepare you for a career as a {career_goal} through relevant coursework in business, finance, and analytical skills."
        
        try:
            course_list = [f"- {course.get('course_code', 'N/A')}: {course.get('title', 'N/A')}" for course in recommended_courses[:5]]
            
            prompt = f"""Create a brief 2-3 sentence explanation of why these courses prepare someone for a {career_goal} career:

COURSES:
{chr(10).join(course_list)}

Explain how these courses build relevant skills for {career_goal}. Keep it concise and professional."""

            response = self.client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 200,
                    "temperature": 0.3,
                    "messages": [
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"❌ Failed to generate learning path explanation: {e}")
            return f"This learning path is designed to prepare you for a career as a {career_goal} through relevant coursework."

# Global instance
career_llm_service = CareerLLMService()
