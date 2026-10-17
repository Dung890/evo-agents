"""
LinkedIn Job Scraper using Selenium
Based on the provided LinkedIn scraping logic
"""

import asyncio
import json
import os
import time
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config.config import AWSConfig


class LinkedInSeleniumScraper:
    """
    LinkedIn job scraper using Selenium
    Based on the provided scraping logic
    """
    
    def __init__(self, manual_login_timeout=120):
        """Initialize the LinkedIn scraper"""
        self.config = AWSConfig()
        self.driver = None
        self.wait = None
        self.manual_login_timeout = manual_login_timeout  # Default 2 minutes
        
        # LinkedIn credentials (should be set in environment variables)
        self.linkedin_email = os.getenv("LINKEDIN_EMAIL", "")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD", "")
        
        # Scraping configuration
        self.max_jobs = 50  # Reasonable limit for demo
        self.delay_between_requests = 2
        self.page_load_timeout = 10
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
    
    def _setup_driver(self):
        """Setup Chrome driver with anti-detection options"""
        try:
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            
            # Run in visible mode for manual login
            # options.add_argument("--headless")  # Commented out to show browser window
            print("🌐 Opening browser window for manual login...")
            
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
                self.driver = webdriver.Chrome(driver_path, options=options)
            else:
                # Try system chromedriver
                self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.wait = WebDriverWait(self.driver, 10)
            
            print("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            print("Chrome/chromedriver not available - will provide mock data instead")
            return False
    
    def _linkedin_login(self) -> bool:
        """Login to LinkedIn with extended session for manual entry"""
        print("🔐 Opening LinkedIn login page...")
        print("📝 You can now manually enter your credentials in the browser window")
        print("⏰ Browser will stay open for 2 minutes to allow manual login")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # If credentials are provided, try automatic login
            if self.linkedin_email and self.linkedin_password:
                print("🔐 Attempting automatic login with provided credentials...")
                try:
                    email_field = self.driver.find_element(By.ID, "username")
                    password_field = self.driver.find_element(By.ID, "password")
                    
                    email_field.send_keys(self.linkedin_email)
                    password_field.send_keys(self.linkedin_password)
                    
                    # Click login button
                    login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
                    login_button.click()
                    time.sleep(5)
                    
                    # Check if login was successful
                    if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                        print("✅ LinkedIn automatic login successful")
                        return True
                    else:
                        print("⚠️ Automatic login failed, please login manually")
                except Exception as e:
                    print(f"⚠️ Automatic login failed: {e}")
                    print("📝 Please login manually in the browser window")
            else:
                print("📝 No credentials provided, please login manually")
            
            # Wait for manual login with configurable timeout
            timeout_minutes = self.manual_login_timeout // 60
            print(f"⏰ Waiting for manual login ({timeout_minutes} minutes)...")
            print("💡 Please complete the login process in the browser window")
            
            # Wait for manual login with configurable timeout
            for i in range(self.manual_login_timeout):
                time.sleep(1)
                current_url = self.driver.current_url
                
                # Check if user has successfully logged in
                if "feed" in current_url or "mynetwork" in current_url or "jobs" in current_url:
                    print("✅ Manual login detected!")
                    return True
                
                # Show progress every 30 seconds
                if i % 30 == 0 and i > 0:
                    remaining_minutes = (self.manual_login_timeout - i) // 60
                    remaining_seconds = (self.manual_login_timeout - i) % 60
                    print(f"⏰ Still waiting... {remaining_minutes}m {remaining_seconds}s remaining")
            
            print("⏰ Timeout reached. Continuing with current session...")
            return True  # Continue even if login status is unclear
            
        except Exception as e:
            print(f"❌ Error during LinkedIn login process: {e}")
            print("📝 Please ensure the browser window is accessible")
            return False
    
    def _go_to_jobs_page(self) -> bool:
        """Navigate to LinkedIn Jobs page"""
        try:
            print("🔍 Navigating to LinkedIn Jobs...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Try to find and click the Jobs icon
            try:
                job_icon = self.driver.find_element(By.XPATH, '//li-icon[@type="job"]/ancestor::a')
                job_icon.click()
                time.sleep(3)
                print("✅ Successfully navigated to Jobs page")
                return True
            except NoSuchElementException:
                # Alternative: go directly to jobs URL
                self.driver.get("https://www.linkedin.com/jobs/")
                time.sleep(3)
                print("✅ Navigated to Jobs page via direct URL")
                return True
                
        except Exception as e:
            print(f"❌ Error navigating to Jobs page: {e}")
            return False
    
    def _search_jobs(self, keyword: str) -> bool:
        """Search for jobs with the given keyword"""
        try:
            print(f"🔍 Searching for jobs: '{keyword}'")
            
            # Find search input
            search_input = self.driver.find_element(By.XPATH, '//input[@aria-label="Search by title, skill, or company"]')
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            time.sleep(4)
            
            print("✅ Job search completed")
            return True
            
        except Exception as e:
            print(f"❌ Error searching for jobs: {e}")
            return False
    
    def _extract_job_data(self, job_element) -> Optional[Dict[str, Any]]:
        """Extract comprehensive job data including salary and requirements"""
        try:
            # Click on the job to get details - optimized for speed
            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
            job_element.click()
            time.sleep(1.5)  # Reduced wait time for faster processing
            
            job_data = {}
            
            # Extract job title
            try:
                title_element = self.driver.find_element(By.XPATH, '//h1[contains(@class, "job-title")]')
                job_data['title'] = title_element.text.strip()
            except NoSuchElementException:
                try:
                    title_element = self.driver.find_element(By.XPATH, '//h1')
                    job_data['title'] = title_element.text.strip()
                except:
                    job_data['title'] = "N/A"
            
            # Extract company name
            try:
                company_element = self.driver.find_element(By.XPATH, '//a[contains(@class, "job-details-jobs-unified-top-card__company-name")]')
                job_data['company'] = company_element.text.strip()
            except NoSuchElementException:
                try:
                    company_element = self.driver.find_element(By.XPATH, '//span[contains(@class, "job-details-jobs-unified-top-card__company-name")]')
                    job_data['company'] = company_element.text.strip()
                except:
                    job_data['company'] = "N/A"
            
            # Extract location
            try:
                location_element = self.driver.find_element(By.XPATH, '//span[contains(@class, "job-details-jobs-unified-top-card__bullet")]')
                job_data['location'] = location_element.text.strip()
            except NoSuchElementException:
                job_data['location'] = "N/A"
            
            # Extract salary information
            try:
                salary_elements = self.driver.find_elements(By.XPATH, '//span[contains(@class, "job-details-jobs-unified-top-card__salary")]')
                if salary_elements:
                    job_data['salary'] = salary_elements[0].text.strip()
                else:
                    # Try alternative salary selectors
                    salary_elements = self.driver.find_elements(By.XPATH, '//span[contains(text(), "$")]')
                    if salary_elements:
                        job_data['salary'] = salary_elements[0].text.strip()
                    else:
                        job_data['salary'] = "Not specified"
            except:
                job_data['salary'] = "Not specified"
            
            # Extract job type and experience level
            try:
                job_type_elements = self.driver.find_elements(By.XPATH, '//span[contains(@class, "job-details-jobs-unified-top-card__job-insight")]')
                job_types = [elem.text.strip() for elem in job_type_elements if elem.text.strip()]
                job_data['job_types'] = job_types
                
                # Extract specific job type
                for job_type in job_types:
                    if any(keyword in job_type.lower() for keyword in ['full-time', 'part-time', 'contract', 'internship']):
                        job_data['job_type'] = job_type
                        break
                else:
                    job_data['job_type'] = "Full-time"  # Default
                
                # Extract experience level
                for job_type in job_types:
                    if any(keyword in job_type.lower() for keyword in ['entry', 'junior', 'mid', 'senior', 'lead', 'principal']):
                        job_data['experience_level'] = job_type
                        break
                else:
                    job_data['experience_level'] = "Mid-level"  # Default
                    
            except:
                job_data['job_types'] = []
                job_data['job_type'] = "Full-time"
                job_data['experience_level'] = "Mid-level"
            
            # Extract job description
            try:
                desc_element = self.driver.find_element(By.XPATH, '//div[contains(@class, "job-details-jobs-unified-top-card__job-description")]')
                job_data['description'] = desc_element.text.strip()
            except NoSuchElementException:
                try:
                    desc_element = self.driver.find_element(By.XPATH, '//div[contains(@class, "jobs-description")]')
                    job_data['description'] = desc_element.text.strip()
                except:
                    job_data['description'] = "N/A"
            
            # Extract requirements from description
            job_data['requirements'] = self._extract_requirements_from_description(job_data.get('description', ''))
            
            # Extract job URL
            try:
                job_link_element = self.driver.find_element(By.XPATH, '//a[contains(@href, "/jobs/view/")]')
                job_data['url'] = job_link_element.get_attribute("href")
            except NoSuchElementException:
                current_url = self.driver.current_url
                if "/jobs/view/" in current_url:
                    job_data['url'] = current_url
                else:
                    job_data['url'] = "N/A"
            
            # Extract posting date
            try:
                date_element = self.driver.find_element(By.XPATH, '//span[contains(@class, "job-details-jobs-unified-top-card__posted-date")]')
                job_data['posted_date'] = date_element.text.strip()
            except:
                job_data['posted_date'] = "N/A"
            
            # Extract additional details
            job_data['source'] = 'LinkedIn'
            job_data['scraped_at'] = datetime.now().isoformat()
            
            # Extract skills from description
            job_data['skills'] = self._extract_skills_from_description(job_data.get('description', ''))
            
            return job_data
            
        except Exception as e:
            print(f"❌ Error extracting job data: {e}")
            return None
    
    def _extract_requirements_from_description(self, description: str) -> List[str]:
        """Extract job requirements from description"""
        if not description or description == "N/A":
            return []
        
        requirements = []
        description_lower = description.lower()
        
        # Common requirement patterns
        requirement_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'degree\s*in\s*([^,\.]+)',
            r'certification\s*in\s*([^,\.]+)',
            r'proficiency\s*in\s*([^,\.]+)',
            r'experience\s*with\s*([^,\.]+)',
            r'knowledge\s*of\s*([^,\.]+)',
            r'familiarity\s*with\s*([^,\.]+)',
            r'strong\s*([^,\.]+)\s*skills',
            r'expertise\s*in\s*([^,\.]+)'
        ]
        
        import re
        for pattern in requirement_patterns:
            matches = re.findall(pattern, description_lower, re.IGNORECASE)
            requirements.extend(matches)
        
        return requirements[:8]  # Limit to 8 requirements
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        if not description or description == "N/A":
            return []
        
        # Common technical skills to look for
        skills_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'machine learning', 'ai', 'data science', 'pandas', 'numpy',
            'tensorflow', 'pytorch', 'scikit-learn', 'spark', 'hadoop',
            'devops', 'ci/cd', 'terraform', 'ansible', 'linux', 'bash',
            'agile', 'scrum', 'jira', 'confluence'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in skills_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return found_skills[:10]  # Limit to 10 skills
    
    def _collect_jobs_with_pagination(self, keyword: str, max_jobs: int = 50) -> List[Dict[str, Any]]:
        """Collect job data - optimized for small numbers"""
        all_jobs = []
        
        print(f"📋 Starting optimized job collection (max: {max_jobs} jobs)...")
        
        try:
            # Find job elements on current page only (no pagination for efficiency)
            jobs = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
            print(f"Found {len(jobs)} job cards on current page")
            
            if not jobs:
                print("No job cards found.")
                return all_jobs
            
            # Process only the number of jobs we need
            jobs_to_process = min(len(jobs), max_jobs)
            
            for i in range(jobs_to_process):
                job = jobs[i]
                try:
                    job_data = self._extract_job_data(job)
                    if job_data and job_data.get('title') != "N/A":
                        all_jobs.append(job_data)
                        print(f"  ✅ Collected {len(all_jobs)}/{max_jobs}: {job_data['title']} at {job_data['company']}")
                        
                        # Stop early if we have enough jobs
                        if len(all_jobs) >= max_jobs:
                            print(f"  🎯 Reached target of {max_jobs} jobs - stopping collection")
                            break
                    else:
                        print(f"  ⚠️ Skipped job {i+1} (no valid data)")
                
                except (NoSuchElementException, ElementClickInterceptedException) as e:
                    print(f"  ❌ Error processing job {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error during job collection: {e}")
        
        print(f"\n✅ Optimized collection completed. Total jobs: {len(all_jobs)}")
        return all_jobs
    
    def _get_mock_linkedin_jobs(self, job_title: str, location: str, max_jobs: int) -> List[Dict[str, Any]]:
        """Get mock LinkedIn job data when Chrome is not available"""
        print("📋 Providing mock LinkedIn job data...")
        
        mock_jobs = [
            {
                "title": f"Senior {job_title.title()}",
                "company": "TechCorp Inc",
                "location": location,
                "description": f"Join our team as a Senior {job_title.title()} and work on cutting-edge projects using modern technologies. We're looking for someone with strong technical skills and leadership experience.",
                "url": "https://linkedin.com/jobs/view/123456",
                "skills": ["Python", "Machine Learning", "SQL", "AWS", "Docker", "Leadership"],
                "job_type": "Full-time",
                "experience_level": "Senior",
                "source": "LinkedIn (Mock)",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "title": f"{job_title.title()} Engineer",
                "company": "DataFlow Solutions",
                "location": location,
                "description": f"We're looking for a {job_title.title()} Engineer to help build our next-generation platform. Experience with cloud technologies and modern development practices required.",
                "url": "https://linkedin.com/jobs/view/123457",
                "skills": ["Python", "JavaScript", "React", "PostgreSQL", "Kubernetes", "Cloud"],
                "job_type": "Full-time",
                "experience_level": "Mid-level",
                "source": "LinkedIn (Mock)",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "title": f"Lead {job_title.title()}",
                "company": "Innovation Labs",
                "location": location,
                "description": f"Lead our {job_title.title()} team and drive technical excellence across the organization. Strong technical background and team leadership experience required.",
                "url": "https://linkedin.com/jobs/view/123458",
                "skills": ["Python", "Leadership", "Architecture", "Cloud", "Agile", "Team Management"],
                "job_type": "Full-time",
                "experience_level": "Senior",
                "source": "LinkedIn (Mock)",
                "scraped_at": datetime.now().isoformat()
            }
        ]
        
        return mock_jobs[:max_jobs]

    async def scrape_jobs(self, job_title: str, location: str = "", max_jobs: int = 50) -> List[Dict[str, Any]]:
        """Main method to scrape LinkedIn jobs"""
        print(f"🚀 LinkedIn Job Scraper - Starting")
        print(f"Job Title: {job_title}")
        print(f"Location: {location or 'Any'}")
        print(f"Max Jobs: {max_jobs}")
        print("=" * 50)
        
        # Setup driver
        if not self._setup_driver():
            print("❌ Failed to setup driver - cannot scrape real data")
            return []
        
        try:
            # Login to LinkedIn
            self._linkedin_login()
            
            # Navigate to jobs page
            if not self._go_to_jobs_page():
                print("❌ Failed to navigate to jobs page")
                return []
            
            # Search for jobs
            search_term = f"{job_title} {location}".strip()
            if not self._search_jobs(search_term):
                print("❌ Failed to search for jobs")
                return []
            
            # Collect job data
            jobs = self._collect_jobs_with_pagination(search_term, max_jobs)
            
            # Save to cache
            if jobs:
                self._save_jobs_to_cache(jobs, job_title, location)
            
            return jobs
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                print("Chrome driver closed.")
    
    def _save_jobs_to_cache(self, jobs: List[Dict[str, Any]], job_title: str, location: str) -> None:
        """Save jobs to cache file"""
        cache_data = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "total_jobs": len(jobs),
                "job_title": job_title,
                "location": location,
                "source": "LinkedIn Selenium Scraper",
                "version": "1.0"
            },
            "jobs": jobs
        }
        
        cache_file = f"data/linkedin_jobs_{job_title.replace(' ', '_').lower()}_{location.replace(' ', '_').lower() if location else 'any'}.json"
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Job data saved to {cache_file}")
        print(f"   Total jobs: {len(jobs)}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get scraper capabilities"""
        return {
            "name": "LinkedIn Selenium Scraper",
            "description": "Scrapes job postings from LinkedIn using Selenium",
            "features": [
                "Real-time job scraping",
                "Pagination support",
                "Job details extraction",
                "Skill extraction",
                "Anti-detection measures"
            ],
            "requirements": [
                "Chrome browser",
                "ChromeDriver",
                "LinkedIn credentials (optional)"
            ],
            "max_jobs_per_request": 50,
            "supported_fields": [
                "title", "company", "location", "description", 
                "url", "skills", "job_type", "experience_level"
            ]
        }


async def main():
    """Main function to run the scraper"""
    scraper = LinkedInSeleniumScraper()
    
    # Example usage
    jobs = await scraper.scrape_jobs(
        job_title="DevOps Engineer",
        location="Dallas, TX",
        max_jobs=20
    )
    
    print(f"\n✅ Scraping completed! Found {len(jobs)} jobs")
    
    # Print sample results
    for i, job in enumerate(jobs[:3]):
        print(f"\nJob {i+1}:")
        print(f"  Title: {job.get('title', 'N/A')}")
        print(f"  Company: {job.get('company', 'N/A')}")
        print(f"  Location: {job.get('location', 'N/A')}")
        print(f"  Skills: {', '.join(job.get('skills', []))}")


if __name__ == "__main__":
    asyncio.run(main())
