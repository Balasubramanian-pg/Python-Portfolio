import time
import csv
import json
import re
import pandas as pd
import random
from datetime import datetime
from typing import List, Dict, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

class GoogleMapsApparelScraper:
    def __init__(self, headless: bool = False, user_data_dir: str = None):
        """
        Initialize the scraper with undetected-chromedriver
        
        Args:
            headless: Run in headless mode
            user_data_dir: Chrome user data directory for persistence
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup undetected Chrome driver"""
        print("Setting up undetected Chrome driver...")
        
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        # Add arguments to make the browser look more human-like
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # User agents to rotate (optional)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Add random user agent
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Add additional stealth options
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # Initialize undetected chromedriver
        try:
            self.driver = uc.Chrome(
                options=options,
                version_main=120,  # Specify your Chrome version
                driver_executable_path=None  # Auto-download if not found
            )
        except Exception as e:
            print(f"Error initializing driver: {e}")
            print("Trying without version specification...")
            self.driver = uc.Chrome(options=options)
        
        self.wait = WebDriverWait(self.driver, 15)
        
        # Additional anti-detection measures
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("window.navigator.chrome = {runtime: {}};")
        
        print("Driver setup complete!")
        return True
    
    def human_like_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def search_location(self, location: str, business_type: str = "apparel"):
        """
        Search for apparel businesses in a specific location
        
        Args:
            location: City name (e.g., "Nashik, India")
            business_type: Type of business to search for
        """
        print(f"\nSearching for {business_type} in {location}...")
        
        try:
            # Open Google Maps
            self.driver.get("https://www.google.com/maps")
            self.human_like_delay(3, 5)
            
            # Accept cookies if present
            self.accept_cookies()
            
            # Find search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            self.human_like_delay(1, 2)
            
            # Enter search query
            search_query = f"{business_type} store {location}"
            for char in search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Type like a human
            
            search_box.send_keys(Keys.RETURN)
            self.human_like_delay(4, 6)
            
            print("Search completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return False
    
    def accept_cookies(self):
        """Accept cookies if popup appears"""
        try:
            cookie_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(@aria-label, 'Accept all') or contains(text(), 'Accept all') or contains(text(), 'I agree')]"
            )
            cookie_button.click()
            print("Cookies accepted")
            self.human_like_delay(1, 2)
        except:
            pass  # No cookie popup found
    
    def scroll_results(self, max_scrolls: int = 20):
        """
        Scroll through results to load more businesses
        
        Args:
            max_scrolls: Maximum number of scroll attempts
        """
        print("Scrolling to load more results...")
        
        try:
            # Find the scrollable results panel
            scrollable_panel = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
            )
            
            last_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", scrollable_panel
            )
            
            scrolls = 0
            no_new_results = 0
            
            while scrolls < max_scrolls:
                # Scroll down
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    scrollable_panel
                )
                
                self.human_like_delay(2, 4)
                
                # Check for "Show more results" button
                try:
                    show_more_buttons = self.driver.find_elements(
                        By.XPATH,
                        "//button[contains(@aria-label, 'More results') or contains(text(), 'More results')]"
                    )
                    
                    for button in show_more_buttons:
                        if button.is_displayed():
                            button.click()
                            print("Clicked 'More results' button")
                            self.human_like_delay(2, 3)
                except:
                    pass
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", scrollable_panel
                )
                
                if new_height == last_height:
                    no_new_results += 1
                    if no_new_results >= 3:
                        print("No more results to load")
                        break
                else:
                    last_height = new_height
                    no_new_results = 0
                
                scrolls += 1
                print(f"Scroll {scrolls}/{max_scrolls} - Height: {new_height}")
                
                # Occasionally scroll up a bit to look more natural
                if scrolls % 5 == 0:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollTop - 300",
                        scrollable_panel
                    )
                    self.human_like_delay(1, 2)
            
            print(f"Finished scrolling. Total scrolls: {scrolls}")
            
        except Exception as e:
            print(f"Error during scrolling: {str(e)}")
    
    def get_business_links(self, max_businesses: int = 100) -> List[str]:
        """
        Extract business links from the results page
        
        Args:
            max_businesses: Maximum number of businesses to collect
            
        Returns:
            List of business URLs
        """
        print("Extracting business links...")
        
        business_links = []
        seen_links = set()
        
        try:
            # Find all business cards/links
            business_elements = self.driver.find_elements(
                By.XPATH,
                "//a[contains(@href, '/maps/place/') and .//div[contains(@class, 'fontHeadlineSmall')]]"
            )
            
            print(f"Found {len(business_elements)} business elements")
            
            for element in business_elements[:max_businesses]:
                try:
                    href = element.get_attribute("href")
                    if href and href not in seen_links:
                        business_links.append(href)
                        seen_links.add(href)
                except:
                    continue
            
            # Alternative selector if first one doesn't work
            if not business_links:
                business_elements = self.driver.find_elements(
                    By.XPATH,
                    "//div[@role='feed']//a[contains(@href, '/maps/place/')]"
                )
                
                for element in business_elements[:max_businesses]:
                    try:
                        href = element.get_attribute("href")
                        if href and href not in seen_links:
                            business_links.append(href)
                            seen_links.add(href)
                    except:
                        continue
            
            print(f"Extracted {len(business_links)} unique business links")
            return business_links
            
        except Exception as e:
            print(f"Error extracting business links: {str(e)}")
            return business_links
    
    def extract_business_details(self, url: str) -> Optional[Dict]:
        """
        Extract detailed information from a business page
        
        Args:
            url: Business page URL
            
        Returns:
            Dictionary with business details or None
        """
        print(f"Extracting details from: {url[:80]}...")
        
        business_data = {
            "name": "",
            "address": "",
            "phone": "",
            "website": "",
            "rating": "",
            "reviews": "",
            "category": "",
            "hours": "",
            "email": "",
            "social_media": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Open business page in new tab
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.human_like_delay(3, 5)
            
            # Extract business name
            try:
                name_element = self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//h1[contains(@class, 'fontHeadlineLarge') or contains(@class, 'DUwDvf')]"
                    ))
                )
                business_data["name"] = name_element.text.strip()
            except:
                pass
            
            # Extract address
            try:
                address_button = self.driver.find_element(
                    By.XPATH,
                    "//button[@data-item-id='address']//div[contains(@class, 'fontBodyMedium')]"
                )
                business_data["address"] = address_button.text.strip()
            except:
                try:
                    address_div = self.driver.find_element(
                        By.XPATH,
                        "//div[contains(@data-tooltip, 'Copy address')]//div[contains(@class, 'fontBodyMedium')]"
                    )
                    business_data["address"] = address_div.text.strip()
                except:
                    pass
            
            # Extract phone number
            try:
                phone_button = self.driver.find_element(
                    By.XPATH,
                    "//button[contains(@data-item-id, 'phone') or contains(@data-tooltip, 'phone')]//div[contains(@class, 'fontBodyMedium')]"
                )
                business_data["phone"] = phone_button.text.strip()
            except:
                pass
            
            # Extract website
            try:
                website_button = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(@data-item-id, 'authority') or contains(@href, 'http')]"
                )
                website_url = website_button.get_attribute("href")
                business_data["website"] = website_url
                
                # Try to extract email from website URL pattern
                if website_url:
                    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                    emails = re.findall(email_pattern, website_url)
                    if emails:
                        business_data["email"] = emails[0]
            except:
                pass
            
            # Extract rating and reviews
            try:
                rating_element = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@aria-label, 'stars')]"
                )
                aria_label = rating_element.get_attribute("aria-label")
                if aria_label:
                    # Extract rating from aria-label
                    rating_match = re.search(r'(\d+\.?\d*)', aria_label)
                    if rating_match:
                        business_data["rating"] = rating_match.group(1)
                    
                    # Extract review count
                    reviews_match = re.search(r'(\d+[\d,]*) reviews', aria_label)
                    if reviews_match:
                        business_data["reviews"] = reviews_match.group(1)
            except:
                pass
            
            # Extract category
            try:
                category_button = self.driver.find_element(
                    By.XPATH,
                    "//button[@jsaction='pane.rating.category']"
                )
                business_data["category"] = category_button.text.strip()
            except:
                business_data["category"] = "Apparel"
            
            # Extract hours
            try:
                hours_button = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@aria-label, 'hours') or contains(@data-tooltip, 'hours')]"
                )
                business_data["hours"] = hours_button.get_attribute("aria-label") or \
                                        hours_button.get_attribute("data-tooltip")
            except:
                pass
            
            # Try to find email in the page content
            try:
                page_content = self.driver.page_source
                email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                emails = re.findall(email_pattern, page_content)
                if emails and not business_data["email"]:
                    # Filter out common false positives
                    valid_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'domain'])]
                    if valid_emails:
                        business_data["email"] = valid_emails[0]
            except:
                pass
            
            # Close the tab and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.human_like_delay(1, 2)
            
            # Filter out empty data
            if not any([business_data["name"], business_data["address"], business_data["phone"]]):
                print(f"No useful data extracted from {business_data.get('name', 'unknown')}")
                return None
            
            print(f"Successfully extracted: {business_data['name']}")
            return business_data
            
        except Exception as e:
            print(f"Error extracting business details: {str(e)}")
            
            # Try to close tab and switch back
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            
            return None
    
    def scrape_location_businesses(self, location: str, max_businesses: int = 50) -> List[Dict]:
        """
        Scrape all businesses from a location
        
        Args:
            location: City name
            max_businesses: Maximum businesses to scrape
            
        Returns:
            List of business dictionaries
        """
        print(f"\n{'='*60}")
        print(f"SCRAPING: {location}")
        print(f"{'='*60}")
        
        businesses = []
        
        # Search for businesses
        if not self.search_location(location, "apparel"):
            print(f"Failed to search in {location}")
            return businesses
        
        # Scroll to load more results
        self.scroll_results(max_scrolls=15)
        
        # Get business links
        business_links = self.get_business_links(max_businesses)
        
        if not business_links:
            print("No business links found!")
            return businesses
        
        print(f"\nExtracting details for {len(business_links)} businesses...")
        
        # Extract details for each business
        for i, link in enumerate(business_links):
            print(f"\n[{i+1}/{len(business_links)}] Processing business...")
            
            business_data = self.extract_business_details(link)
            
            if business_data:
                business_data["location"] = location
                business_data["source_url"] = link
                businesses.append(business_data)
            
            # Add random delay between businesses
            if i < len(business_links) - 1:
                delay = random.uniform(3, 8)
                print(f"Waiting {delay:.1f} seconds before next business...")
                time.sleep(delay)
        
        print(f"\nSuccessfully scraped {len(businesses)} businesses from {location}")
        return businesses
    
    def save_results(self, businesses: List[Dict], filename: str = None):
        """
        Save scraped data to CSV and JSON files
        
        Args:
            businesses: List of business dictionaries
            filename: Base filename (without extension)
        """
        if not businesses:
            print("No data to save!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"apparel_businesses_{timestamp}"
        
        # Save to CSV
        csv_filename = f"{filename}.csv"
        df = pd.DataFrame(businesses)
        
        # Reorder columns for better readability
        column_order = ["name", "location", "address", "phone", "email", "website", 
                       "rating", "reviews", "category", "hours", "social_media", 
                       "source_url", "timestamp"]
        
        # Only include columns that exist in the dataframe
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in column_order]
        final_columns = existing_columns + other_columns
        
        df = df[final_columns]
        df.to_csv(csv_filename, index=False, encoding="utf-8")
        
        # Save to JSON
        json_filename = f"{filename}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(businesses, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved successfully!")
        print(f"CSV: {csv_filename}")
        print(f"JSON: {json_filename}")
        print(f"Total records: {len(businesses)}")
        
        # Display summary
        self.display_summary(businesses)
    
    def display_summary(self, businesses: List[Dict]):
        """Display summary of scraped data"""
        if not businesses:
            return
        
        print(f"\n{'='*60}")
        print("SCRAPING SUMMARY")
        print(f"{'='*60}")
        
        # Count by location
        locations = {}
        for business in businesses:
            loc = business.get("location", "Unknown")
            locations[loc] = locations.get(loc, 0) + 1
        
        for loc, count in locations.items():
            print(f"{loc}: {count} businesses")
        
        print(f"\nTotal businesses: {len(businesses)}")
        
        # Data completeness
        fields = ["name", "address", "phone", "email", "website"]
        print("\nData completeness:")
        for field in fields:
            count = sum(1 for b in businesses if b.get(field))
            percentage = (count / len(businesses)) * 100
            print(f"{field}: {count}/{len(businesses)} ({percentage:.1f}%)")
        
        # Sample output
        print(f"\n{'='*60}")
        print("SAMPLE BUSINESSES")
        print(f"{'='*60}")
        
        for i, business in enumerate(businesses[:3]):  # Show first 3
            print(f"\n{i+1}. {business.get('name', 'N/A')}")
            print(f"   Location: {business.get('location', 'N/A')}")
            print(f"   Address: {business.get('address', 'N/A')[:60]}...")
            print(f"   Phone: {business.get('phone', 'N/A')}")
            print(f"   Email: {business.get('email', 'N/A')}")
    
    def run_scraper(self, locations: List[str] = None, max_per_location: int = 50):
        """
        Main function to run the scraper
        
        Args:
            locations: List of locations to scrape
            max_per_location: Maximum businesses per location
        """
        if locations is None:
            locations = ["Nashik, Maharashtra, India", "Pune, Maharashtra, India"]
        
        print("="*60)
        print("GOOGLE MAPS APPAREL BUSINESS SCRAPER")
        print("="*60)
        print("Using undetected-chromedriver for anti-detection")
        print(f"Target locations: {locations}")
        print("="*60)
        
        all_businesses = []
        
        try:
            # Setup driver
            if not self.setup_driver():
                print("Failed to setup driver!")
                return
            
            # Scrape each location
            for location in locations:
                try:
                    businesses = self.scrape_location_businesses(
                        location, 
                        max_per_location
                    )
                    all_businesses.extend(businesses)
                    
                    # Save intermediate results
                    if businesses:
                        temp_filename = f"apparel_{location.split(',')[0].lower()}_{datetime.now().strftime('%H%M%S')}"
                        self.save_results(businesses, temp_filename)
                    
                    # Longer delay between locations
                    if location != locations[-1]:
                        delay = random.uniform(10, 20)
                        print(f"\nWaiting {delay:.1f} seconds before next location...")
                        time.sleep(delay)
                        
                except Exception as e:
                    print(f"Error scraping {location}: {str(e)}")
                    continue
            
            # Save final combined results
            if all_businesses:
                self.save_results(all_businesses, "apparel_businesses_nashik_pune_final")
            else:
                print("\nNo businesses were scraped!")
            
        except KeyboardInterrupt:
            print("\n\nScraping interrupted by user!")
            
            # Save partial results
            if all_businesses:
                print("Saving partial results...")
                self.save_results(all_businesses, "apparel_businesses_partial")
        
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            
        finally:
            # Close driver
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()
            
            print("\nScraping completed!")

def main():
    """
    Main execution function
    """
    # Configuration
    HEADLESS = False  # Set to True for headless mode (less detectable but may have issues)
    USER_DATA_DIR = None  # Set to a path like "/path/to/chrome/profile" for persistence
    
    # Create scraper instance
    scraper = GoogleMapsApparelScraper(
        headless=HEADLESS,
        user_data_dir=USER_DATA_DIR
    )
    
    # Define locations (you can add more)
    locations = [
        "Nashik, Maharashtra, India",
        "Pune, Maharashtra, India"
    ]
    
    # Alternative search terms (optional)
    # You can modify the search_location method to use these
    apparel_keywords = [
        "clothing store",
        "fashion store", 
        "boutique",
        "garment shop",
        "textile shop"
    ]
    
    # Run the scraper
    scraper.run_scraper(
        locations=locations,
        max_per_location=30  # Start with 30 per location to avoid detection
    )

if __name__ == "__main__":
    # Install required packages first:
    # pip install undetected-chromedriver selenium pandas
    
    print("Google Maps Apparel Business Scraper")
    print("="*50)
    print("Note: This is for educational purposes only.")
    print("Respect Google's Terms of Service and robots.txt.")
    print("="*50)
    
    main()