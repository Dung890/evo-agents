from typing import Dict, Any, List
import json
import os
import re
from datetime import datetime
import numpy as np
from src.agents.base_agent import BaseAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMBEDDINGS_FILE = "data/course_embeddings.npy"
EMBEDDING_IDS_FILE = "data/course_embedding_ids.json"


def course_embedding_text(course: Dict[str, Any]) -> str:
    """Text that represents a course in embedding space: clean title + description"""
    title = re.sub(r"^\(\s*[A-Z]+\s+\w+\s*\)\s*", "", course.get("title", ""))
    description = re.sub(r"^\(\d+ semester credit hours?\)\s*", "", course.get("description") or "")
    return f"{title}. {description}".strip()

class CourseCatalogAgent(BaseAgent):
    """
    Agent responsible for gathering UTD course descriptions and prerequisites,
    analyzing course content to extract taught skills, and mapping relationships
    between courses.
    """

    def __init__(self):
        """Initialize the Course Catalog Agent"""
        super().__init__(
            name="Course Catalog Agent",
            description="Analyzes UTD course offerings to extract skills and course relationships"
        )
        
        # Load course data from JSON file
        self.courses_file = "data/utd_courses.json"
        self.courses = self._load_courses_from_json()
        
        # Create skill index for fast searching
        self.skill_index = self._build_skill_index()

        # Load precomputed course embeddings for semantic search (None if not built yet)
        self.course_embeddings = self._load_embeddings()
        self._query_cache: Dict[str, np.ndarray] = {}

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a course catalog request

        Args:
            request (Dict[str, Any]): Request containing search parameters

        Returns:
            Dict[str, Any]: Course catalog data
        """
        search_term = request.get("search_term", "")
        department = request.get("department", "")
        skill = request.get("skill", "")

        # Get course data based on request parameters
        if search_term:
            courses = self.search_courses(search_term)
        elif department:
            courses = self.get_courses_by_department(department)
        elif skill:
            courses = self.get_courses_by_skill(skill)
        else:
            return {"error": "No search criteria provided"}

        # Extract skills from courses
        if courses:
            course_skills = self.extract_course_skills(courses)

            # Map relationships between courses
            course_relationships = self.map_course_relationships(courses)

            return {
                "courses": courses,
                "skills": course_skills,
                "relationships": course_relationships
            }
        else:
            return {"error": "No courses found matching the criteria"}

    def _load_courses_from_json(self) -> List[Dict[str, Any]]:
        """Load courses from JSON file"""
        if not os.path.exists(self.courses_file):
            print(f"Course catalog file not found: {self.courses_file}")
            print("Please run the UTD course scraper first to generate course data.")
            return []
        
        try:
            with open(self.courses_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                courses = data.get('courses', [])
                for course in courses:
                    # Catalog stores prefix/number separately; agents expect "CS 4375"
                    if not course.get('course_code') and course.get('prefix'):
                        course['course_code'] = f"{course['prefix']} {course['number']}"
                print(f"Loaded {len(courses)} courses from {self.courses_file}")
                return courses
        except Exception as e:
            print(f"Error loading courses from JSON: {e}")
            return []
    
    def _build_skill_index(self) -> Dict[str, List[str]]:
        """Build an index of skills to courses for fast searching"""
        skill_index = {}
        
        for course in self.courses:
            course_code = course.get('course_code', '')
            skills = course.get('skills', [])
            
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower not in skill_index:
                    skill_index[skill_lower] = []
                skill_index[skill_lower].append(course_code)
        
        return skill_index
    
    def _load_embeddings(self):
        """Load course embeddings and align their rows with self.courses"""
        if not (os.path.exists(EMBEDDINGS_FILE) and os.path.exists(EMBEDDING_IDS_FILE)):
            print("Course embeddings not found. Run scripts/build_course_embeddings.py to enable semantic search.")
            return None

        try:
            matrix = np.load(EMBEDDINGS_FILE)
            with open(EMBEDDING_IDS_FILE, 'r', encoding='utf-8') as f:
                row_by_code = {code: i for i, code in enumerate(json.load(f))}

            rows = [row_by_code.get(course.get('course_code')) for course in self.courses]
            if not rows or None in rows:
                print("Course embeddings are out of date with the catalog. Rebuild them to enable semantic search.")
                return None

            print(f"Loaded {len(rows)} course embeddings ({matrix.shape[1]} dims)")
            return matrix[rows]
        except Exception as e:
            print(f"Error loading course embeddings: {e}")
            return None

    def has_semantic_search(self) -> bool:
        return self.course_embeddings is not None

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a query with Bedrock, caching repeated queries (e.g. common skills)"""
        key = text.strip().lower()
        if key not in self._query_cache:
            self._query_cache[key] = np.array(self.bedrock_service.embed_text(text), dtype=np.float32)
        return self._query_cache[key]

    def similarity_scores(self, query_vector: np.ndarray) -> np.ndarray:
        """Cosine similarity of a query against every course (vectors are unit length)"""
        return self.course_embeddings @ query_vector

    def semantic_search(self, query: str, top_k: int = 10, exclude_codes: List[str] = None) -> List[Dict[str, Any]]:
        """
        Find the courses whose content is closest in meaning to the query

        Args:
            query (str): Free text, e.g. "Data Scientist. Skills: Python, SQL, statistics"
            top_k (int): Number of courses to return
            exclude_codes (List[str]): Course codes to skip (e.g. already completed)

        Returns:
            List[Dict[str, Any]]: [{"course": ..., "index": int, "similarity": float}] best first
        """
        if not self.has_semantic_search():
            return []

        excluded = {code.lower() for code in (exclude_codes or [])}
        scores = self.similarity_scores(self.embed_query(query))

        results = []
        seen = set()  # Cross-listed courses (e.g. BUAN/ITSS 4354) differ only by "(Same as ...)"
        for i in np.argsort(-scores):
            course = self.courses[i]
            content_key = re.sub(r"\(Same as [^)]*\)", "", course_embedding_text(course))
            if course.get('course_code', '').lower() in excluded or content_key in seen:
                continue
            seen.add(content_key)
            results.append({"course": course, "index": int(i), "similarity": float(scores[i])})
            if len(results) >= top_k:
                break
        return results

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """
        Get all courses from the UTD course catalog

        Returns:
            List[Dict[str, Any]]: List of courses
        """
        return self.courses

    def search_courses(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for courses by term

        Args:
            search_term (str): Term to search for

        Returns:
            List[Dict[str, Any]]: List of matching courses
        """
        all_courses = self.get_all_courses()
        search_term = search_term.lower()

        # Filter courses by search term
        matching_courses = [
            course for course in all_courses
            if search_term in course.get("title", "").lower() or
               search_term in course.get("description", "").lower() or
               search_term in course.get("course_code", "").lower()
        ]

        return matching_courses

    def get_courses_by_department(self, department: str) -> List[Dict[str, Any]]:
        """
        Get courses by department

        Args:
            department (str): Department name

        Returns:
            List[Dict[str, Any]]: List of courses in the department
        """
        all_courses = self.get_all_courses()
        department = department.lower()

        # Filter courses by department
        matching_courses = [
            course for course in all_courses
            if department in course.get("department", "").lower()
        ]

        return matching_courses

    def get_courses_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """
        Get courses that teach a specific skill using skill index

        Args:
            skill (str): Skill name

        Returns:
            List[Dict[str, Any]]: List of courses teaching the skill
        """
        skill_lower = skill.lower()
        matching_course_codes = []
        
        # Direct match
        if skill_lower in self.skill_index:
            matching_course_codes.extend(self.skill_index[skill_lower])
        
        # Partial match
        for indexed_skill, course_codes in self.skill_index.items():
            if skill_lower in indexed_skill or indexed_skill in skill_lower:
                matching_course_codes.extend(course_codes)
        
        # Remove duplicates and get course objects
        unique_codes = list(set(matching_course_codes))
        matching_courses = []
        
        for course in self.courses:
            if course.get('course_code') in unique_codes:
                matching_courses.append(course)
        
        return matching_courses

    def extract_skills_from_course(self, course: Dict[str, Any]) -> List[str]:
        """
        Get skills for a course (already extracted and stored in JSON)

        Args:
            course (Dict[str, Any]): Course information

        Returns:
            List[str]: List of skills taught in the course
        """
        return course.get('skills', [])

    def extract_course_skills(self, courses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract skills from a list of courses

        Args:
            courses (List[Dict[str, Any]]): List of courses

        Returns:
            Dict[str, List[str]]: Dictionary mapping course codes to skills
        """
        course_skills = {}

        for course in courses:
            course_code = course.get("code") or course.get("course_code")
            if course_code:
                skills = course.get('skills', [])
                course_skills[course_code] = skills

        return course_skills

    def map_course_relationships(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map relationships between courses

        Args:
            courses (List[Dict[str, Any]]): List of courses

        Returns:
            List[Dict[str, Any]]: List of course relationships
        """
        relationships = []

        # Extract prerequisites
        for course in courses:
            course_code = course.get("code") or course.get("course_code")
            prerequisites = course.get("prerequisites", [])

            if not prerequisites or not course_code:
                continue

            # Prerequisites are already parsed as list of course codes
            for prereq_code in prerequisites:
                relationships.append({
                    "course": course_code,
                    "prerequisite": prereq_code,
                    "type": "prerequisite"
                })

        # Add skill-based relationships
        course_skills = self.extract_course_skills(courses)

        for i, course1 in enumerate(courses):
            code1 = course1.get("code") or course1.get("course_code")
            if not code1 or code1 not in course_skills:
                continue

            skills1 = set(course_skills[code1])

            for j, course2 in enumerate(courses[i+1:], i+1):
                code2 = course2.get("code") or course2.get("course_code")
                if not code2 or code2 not in course_skills:
                    continue

                skills2 = set(course_skills[code2])

                # Find common skills
                common_skills = skills1.intersection(skills2)

                if len(common_skills) > 2:  # At least 3 skills in common
                    relationships.append({
                        "course1": code1,
                        "course2": code2,
                        "common_skills": list(common_skills),
                        "type": "related"
                    })

        return relationships

    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent

        Returns:
            List[str]: List of capability descriptions
        """
        return [
            "Load UTD course catalog from JSON with pre-extracted skills",
            "Search courses by term, department, or skill using skill index",
            "Map relationships between different courses based on prerequisites and skills",
            "Fast semantic skill matching for course recommendations",
            f"Access to {len(self.courses)} courses across {len(set(c.get('department', '') for c in self.courses))} departments"
        ]
