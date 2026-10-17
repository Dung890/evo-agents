"""
UTD Course Catalog Selenium Scraper
Uses Selenium to scrape course information directly from UTD Coursebook
Based on the coursebook-api scraping logic
"""

import asyncio
import json
import os
import time
import re
from datetime import datetime
from typing import Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.core.aws.bedrock_service import BedrockService
from src.config.config import AWSConfig


class UTDCourseSeleniumScraper:
    """
    Selenium-based scraper for UTD Coursebook
    Uses the actual scraping logic from coursebook-api
    """
    
    def __init__(self):
        """Initialize the UTD Course Selenium scraper"""
        self.config = AWSConfig()
        self.bedrock_service = BedrockService()
        self.cache_file = "data/utd_courses.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Target departments for scraping
        self.target_departments = self.config.target_departments
        
        # Common course numbers to scrape for each department
        self.course_numbers = {
            "CS": ["1336", "1337", "2336", "3345", "4347", "4348", "4352", "4353", "4354", "4355", "4356", "4357", "4358", "4359", "4361", "4365", "4366", "4367", "4368", "4369", "4370"],
            "SE": ["4351", "4352", "4353", "4354", "4355", "4356", "4357", "4358", "4359", "4360", "4361", "4362", "4363", "4364", "4365", "4366", "4367", "4368", "4369", "4370"],
            "MATH": ["2413", "2414", "2415", "2416", "2417", "2418", "2419", "2420", "2421", "2422", "2423", "2424", "2425", "2426", "2427", "2428", "2429", "2430", "2431", "2432", "2433", "2434", "2435", "2436", "2437", "2438", "2439", "2440"],
            "STAT": ["4351", "4352", "4353", "4354", "4355", "4356", "4357", "4358", "4359", "4360", "4361", "4362", "4363", "4364", "4365", "4366", "4367", "4368", "4369", "4370"],
            "BA": ["1310", "1311", "1312", "1313", "1314", "1315", "1316", "1317", "1318", "1319", "1320", "1321", "1322", "1323", "1324", "1325", "1326", "1327", "1328", "1329", "1330"],
            "SYSM": ["4351", "4352", "4353", "4354", "4355", "4356", "4357", "4358", "4359", "4360", "4361", "4362", "4363", "4364", "4365", "4366", "4367", "4368", "4369", "4370"]
        }
        
        # Initialize Chrome driver
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try to find chromedriver
            chromedriver_paths = [
                "bin/chromedriver.exe",
                "bin/chromedriver-win.exe", 
                "chromedriver.exe",
                "chromedriver"
            ]
            
            driver_path = None
            for path in chromedriver_paths:
                if os.path.exists(path):
                    driver_path = path
                    break
            
            if driver_path:
                self.driver = webdriver.Chrome(driver_path, options=chrome_options)
            else:
                # Try system chromedriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to coursebook
            self.driver.get("https://coursebook.utdallas.edu")
            print("✅ Chrome driver initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            print("Please ensure Chrome and chromedriver are installed")
            self.driver = None
    
    def _set_inject_vars(self):
        """Extract course data from the page (based on coursebook-api logic)"""
        try:
            course_elements = self.driver.find_elements(By.CLASS_NAME, "courseinfo__overviewtable__td")
            course_head_elements = self.driver.find_elements(By.CLASS_NAME, "courseinfo__overviewtable__th")
            
            return {
                "course": course_elements,
                "course_head": course_head_elements
            }
        except Exception as e:
            print(f"Error extracting course data: {e}")
            return {"course": [], "course_head": []}
    
    def _scrape_course_data(self, course_elements, course_head_elements):
        """Scrape course data from elements (based on coursebook-api logic)"""
        try:
            course_data = {}
            
            # Extract course information
            for i, head in enumerate(course_head_elements):
                if i < len(course_elements):
                    key = head.text.strip().lower().replace(" ", "_")
                    value = course_elements[i].text.strip()
                    course_data[key] = value
            
            return course_data
            
        except Exception as e:
            print(f"Error scraping course data: {e}")
            return {}
    
    def _webscrape_single_section(self, course_tag):
        """Scrape a single course section (based on coursebook-api logic)"""
        try:
            url = f"https://coursebook.utdallas.edu/clips/clip-coursebook.zog?id={course_tag}&action=info"
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Extract course data
            inject_vars = self._set_inject_vars()
            course_data = self._scrape_course_data(inject_vars["course"], inject_vars["course_head"])
            
            return course_data
            
        except Exception as e:
            print(f"Error scraping course {course_tag}: {e}")
            return {}
    
    def _webscrape_all_sections(self, course_tag):
        """Scrape all sections for a course (based on coursebook-api logic)"""
        try:
            url = f"https://coursebook.utdallas.edu/search/{course_tag}"
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Find course sections
            try:
                course_list = self.driver.find_elements(By.CLASS_NAME, "stopbubble")
                current_term_element = self.driver.find_element(By.CLASS_NAME, "directaddress")
                current_term = current_term_element.text[-3:]  # Get last 3 characters
                
                course_sections = []
                for course in course_list:
                    section_text = course.text.replace(' ', '').lower()
                    course_sections.append(f"{section_text}.{current_term}")
                
                # Scrape each section
                all_sections = []
                for section in course_sections:
                    section_data = self._webscrape_single_section(section)
                    if section_data:
                        all_sections.append(section_data)
                    time.sleep(0.2)  # Rate limiting
                
                return all_sections
                
            except NoSuchElementException:
                print(f"No sections found for {course_tag}")
                return []
                
        except Exception as e:
            print(f"Error scraping all sections for {course_tag}: {e}")
            return []
    
    def extract_skills_from_description(self, description: str) -> List[str]:
        """Extract technical skills from course description using AI"""
        if not description or len(description.strip()) < 10:
            return []
        
        try:
            prompt = f"""
            Analyze this course description and extract the main technical skills, programming languages, tools, and technologies mentioned.
            Return only the skills as a comma-separated list, no explanations.
            
            Course Description: {description}
            
            Skills:"""
            
            response = self.bedrock_service.invoke_model(prompt)
            if response and "skills:" in response.lower():
                skills_text = response.split("skills:")[-1].strip()
                skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
                return skills[:10]  # Limit to 10 skills
            return []
            
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return []
    
    def process_course_data(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw course data into our standardized format"""
        if not course_data:
            return {}
        
        # Extract basic information
        course_code = course_data.get("course_number", "")
        course_title = course_data.get("course_title", "")
        description = course_data.get("description", "")
        
        # Extract skills from description
        skills = self.extract_skills_from_description(description)
        
        # Extract prerequisites
        prerequisites = []
        enrollment_reqs = course_data.get("enrollment_reqs", "")
        if enrollment_reqs:
            prereq_match = re.search(r"prerequisite[s]?:?\s*([^.]+)", enrollment_reqs.lower())
            if prereq_match:
                prereq_text = prereq_match.group(1)
                prerequisites = [req.strip() for req in prereq_text.split(",") if req.strip()]
        
        # Extract credit hours
        credit_hours = course_data.get("semester_credit_hours", "3")
        try:
            credits = int(credit_hours)
        except:
            credits = 3
        
        # Extract instructor information
        instructors = course_data.get("instructor", [])
        if isinstance(instructors, str):
            instructors = [instructors] if instructors else []
        
        return {
            "course_code": course_code,
            "title": course_title,
            "description": description,
            "credits": credits,
            "prerequisites": prerequisites,
            "corequisites": [],
            "department": course_code[:2].upper() if len(course_code) > 2 else "CS",
            "skills": skills,
            "instructors": instructors,
            "level": "undergraduate" if int(course_code[2:]) < 5000 else "graduate",
            "schedule": course_data.get("date/time", ""),
            "grading": course_data.get("grading", ""),
            "mode": course_data.get("mode", ""),
            "type": course_data.get("type", "")
        }
    
    async def scrape_courses(self) -> List[Dict[str, Any]]:
        """Scrape all courses using Selenium"""
        if not self.driver:
            print("❌ Chrome driver not initialized")
            return []
        
        print("Starting UTD course scraping with Selenium...")
        print(f"Target departments: {self.target_departments}")
        
        all_courses = []
        total_courses = sum(len(courses) for courses in self.course_numbers.values())
        processed = 0
        
        for dept in self.target_departments:
            if dept not in self.course_numbers:
                continue
                
            print(f"Processing {dept} department...")
            
            for course_num in self.course_numbers[dept]:
                course_code = f"{dept.lower()}{course_num}"
                processed += 1
                
                print(f"  [{processed}/{total_courses}] Processing {course_code}...")
                
                try:
                    # Scrape all sections for this course
                    sections_data = self._webscrape_all_sections(course_code)
                    
                    if sections_data:
                        # Process the first section (they should all be similar)
                        processed_course = self.process_course_data(sections_data[0])
                        
                        if processed_course and processed_course.get('course_code'):
                            all_courses.append(processed_course)
                            print(f"    ✅ {processed_course['course_code']}: {processed_course['title']}")
                        else:
                            print(f"    ⚠️ No valid data for {course_code}")
                    else:
                        print(f"    ❌ No sections found for {course_code}")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ❌ Error processing {course_code}: {e}")
                    continue
        
        print(f"Scraping completed. Found {len(all_courses)} courses.")
        return all_courses
    
    def save_courses_to_json(self, courses: List[Dict[str, Any]]) -> None:
        """Save courses to JSON file"""
        data = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "total_courses": len(courses),
                "departments": self.target_departments,
                "version": "3.0",
                "source": "UTD Coursebook Selenium Scraper"
            },
            "courses": courses
        }
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Course data saved to {self.cache_file}")
        print(f"   Total courses: {len(courses)}")
        print(f"   Departments: {', '.join(self.target_departments)}")
    
    async def run_scraping(self) -> None:
        """Run the complete scraping process"""
        try:
            if not self.driver:
                print("❌ Chrome driver not available. Please install Chrome and chromedriver.")
                return
            
            # Scrape courses
            courses = await self.scrape_courses()
            
            if courses:
                # Save to JSON
                self.save_courses_to_json(courses)
                
                # Print summary
                print("\n" + "="*50)
                print("SCRAPING SUMMARY")
                print("="*50)
                print(f"Total courses scraped: {len(courses)}")
                
                # Count by department
                dept_counts = {}
                for course in courses:
                    dept = course.get('department', 'Unknown')
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
                
                for dept, count in dept_counts.items():
                    print(f"{dept}: {count} courses")
                
                print(f"\nData saved to: {self.cache_file}")
                print("✅ Scraping completed successfully!")
                
            else:
                print("❌ No courses were scraped. Please check the scraper configuration.")
                
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("Chrome driver closed.")


async def main():
    """Main function to run the scraper"""
    scraper = UTDCourseSeleniumScraper()
    await scraper.run_scraping()


if __name__ == "__main__":
    asyncio.run(main())
