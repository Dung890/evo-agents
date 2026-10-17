"""
LinkedIn Authentication Module
Handles LinkedIn login and session management
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class LinkedInAuthenticator:
    """
    LinkedIn authentication handler
    Manages LinkedIn login and session validation
    """
    
    def __init__(self):
        self.driver = None
        self.session_file = "data/linkedin_session.json"
        self.session_timeout = 24 * 60 * 60  # 24 hours in seconds
        self.auth_timeout = 300  # 5 minutes for manual login
        
    def _setup_driver(self) -> bool:
        """Setup Chrome driver for LinkedIn authentication"""
        try:
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            
            # Run in visible mode for authentication
            print("🌐 Opening browser for LinkedIn authentication...")
            
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
            self.driver.set_page_load_timeout(30)
            
            print("✅ Chrome driver initialized for LinkedIn authentication")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            return False
    
    def _check_existing_session(self) -> bool:
        """Check if there's a valid existing LinkedIn session"""
        if not os.path.exists(self.session_file):
            return False
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Check if session is still valid
            session_time = datetime.fromisoformat(session_data.get('authenticated_at', ''))
            if datetime.now() - session_time > timedelta(seconds=self.session_timeout):
                print("📅 LinkedIn session expired")
                return False
            
            print("✅ Valid LinkedIn session found")
            return True
            
        except Exception as e:
            print(f"❌ Error checking session: {e}")
            return False
    
    def _save_session(self, success: bool = True) -> None:
        """Save LinkedIn session status"""
        os.makedirs("data", exist_ok=True)
        
        session_data = {
            "authenticated": success,
            "authenticated_at": datetime.now().isoformat(),
            "session_timeout": self.session_timeout
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        if success:
            print("💾 LinkedIn session saved successfully")
        else:
            print("💾 LinkedIn authentication failed - session not saved")
    
    async def authenticate_linkedin(self) -> bool:
        """
        Authenticate with LinkedIn
        Returns True if authentication successful, False otherwise
        """
        print("🔐 LinkedIn Authentication Required")
        print("=" * 50)
        print("📝 To access real job market data, you need to authenticate with LinkedIn")
        print("⏰ You will have 5 minutes to complete the login process")
        print("=" * 50)
        
        # Check for existing valid session
        if self._check_existing_session():
            return True
        
        # Setup driver
        if not self._setup_driver():
            print("❌ Cannot setup browser for LinkedIn authentication")
            self._save_session(False)
            return False
        
        try:
            # Navigate to LinkedIn login
            print("🔐 Opening LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Try automatic login if credentials are provided
            linkedin_email = os.getenv("LINKEDIN_EMAIL", "")
            linkedin_password = os.getenv("LINKEDIN_PASSWORD", "")
            
            if linkedin_email and linkedin_password:
                print("🔐 Attempting automatic login...")
                try:
                    email_field = self.driver.find_element(By.ID, "username")
                    password_field = self.driver.find_element(By.ID, "password")
                    
                    email_field.send_keys(linkedin_email)
                    password_field.send_keys(linkedin_password)
                    
                    # Click login button
                    login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
                    login_button.click()
                    time.sleep(5)
                    
                    # Check if login was successful
                    if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                        print("✅ LinkedIn automatic login successful")
                        self._save_session(True)
                        return True
                    else:
                        print("⚠️ Automatic login failed, please login manually")
                except Exception as e:
                    print(f"⚠️ Automatic login failed: {e}")
                    print("📝 Please login manually in the browser window")
            else:
                print("📝 No credentials provided, please login manually")
            
            # Wait for manual login
            print("⏰ Waiting for manual LinkedIn login (5 minutes)...")
            print("💡 Please complete the login process in the browser window")
            
            for i in range(self.auth_timeout):
                time.sleep(1)
                current_url = self.driver.current_url
                
                # Check if user has successfully logged in
                if "feed" in current_url or "mynetwork" in current_url or "jobs" in current_url:
                    print("✅ Manual LinkedIn login detected!")
                    self._save_session(True)
                    return True
                
                # Show progress every 30 seconds
                if i % 30 == 0 and i > 0:
                    remaining_minutes = (self.auth_timeout - i) // 60
                    remaining_seconds = (self.auth_timeout - i) % 60
                    print(f"⏰ Still waiting... {remaining_minutes}m {remaining_seconds}s remaining")
            
            print("⏰ Authentication timeout reached")
            self._save_session(False)
            return False
            
        except Exception as e:
            print(f"❌ Error during LinkedIn authentication: {e}")
            self._save_session(False)
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("🌐 Browser closed")
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated with LinkedIn"""
        return self._check_existing_session()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get current authentication status"""
        if self.is_authenticated():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                return {
                    "authenticated": True,
                    "authenticated_at": session_data.get('authenticated_at'),
                    "status": "LinkedIn session active"
                }
            except:
                return {
                    "authenticated": False,
                    "status": "Session file error"
                }
        else:
            return {
                "authenticated": False,
                "status": "Not authenticated with LinkedIn"
            }
    
    def logout(self) -> bool:
        """Logout and clear session"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            print("✅ LinkedIn session cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing session: {e}")
            return False


# Global authenticator instance
linkedin_auth = LinkedInAuthenticator()


async def require_linkedin_auth() -> bool:
    """
    Require LinkedIn authentication before proceeding
    This function should be called at the start of the application
    """
    print("🚀 UTD Career Guidance AI System")
    print("=" * 50)
    print("🔐 LinkedIn Authentication Required")
    print("📊 To provide real job market data, we need to authenticate with LinkedIn")
    print("=" * 50)
    
    if linkedin_auth.is_authenticated():
        print("✅ LinkedIn authentication verified")
        return True
    
    print("❌ LinkedIn authentication required")
    print("🔐 Please authenticate with LinkedIn to continue...")
    
    # Attempt authentication
    success = await linkedin_auth.authenticate_linkedin()
    
    if success:
        print("✅ LinkedIn authentication successful!")
        print("🎉 You can now access real job market data")
        return True
    else:
        print("❌ LinkedIn authentication failed")
        print("⚠️ You can still use the system with limited data")
        return False


if __name__ == "__main__":
    # Test the authentication
    async def test_auth():
        success = await require_linkedin_auth()
        if success:
            print("✅ Authentication test passed")
        else:
            print("❌ Authentication test failed")
    
    asyncio.run(test_auth())
