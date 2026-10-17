"""
Scrapers module for the UTD Career Guidance AI System.

This module contains scrapers for:
- UTD Course Catalog (using Selenium)
- LinkedIn Jobs (using Selenium)
"""

from .utd_course_selenium import UTDCourseSeleniumScraper
from .linkedin_selenium_scraper import LinkedInSeleniumScraper

__all__ = [
    'UTDCourseSeleniumScraper',
    'LinkedInSeleniumScraper'
]
