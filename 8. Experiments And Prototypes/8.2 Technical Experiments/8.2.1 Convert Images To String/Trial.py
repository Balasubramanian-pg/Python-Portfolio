import pandas as pd
import time
import random
import re
import os
import logging
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('executive_scraper.log'),
        logging.StreamHandler()
    ]
)

class ExecutiveScraper:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.driver = None
        self.df = pd.DataFrame()
        
        # Target configuration
        self.target_titles = [
            'ceo', 'chief executive officer', 
            'managing director', 'md'
        ]
        self.exclude_titles = [
            'sales', 'account manager', 
            'business development', 'bdm'
        ]
        
        # Search templates with exclusion terms
        self.search_templates = [
            'intitle:"{company}" ("CEO" OR "Managing Director") -"Sales" site:linkedin.com/in/',
            '"{company}" ("Chief Executive Officer" OR "MD") -"VP" -"Director of Sales" site:linkedin.com/in/',
            '"{company}" ("CEO & Managing Director" OR "CEO and MD") -"Sales" site:linkedin.com/in/'
        ]

    def init_driver(self):
        """Initialize stealth browser instance"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
            
            self.driver = uc.Chrome(
                options=options,
                headless=False,
                use_subprocess=True
            )
            ActionChains(self.driver).move_by_offset(10, 10).perform()
            return True
        except Exception as e:
            logging.error(f"Driver init failed: {str(e)}")
            return False

    def humanized_delay(self, min_sec=2, max_sec=5):
        """Randomized human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def execute_search(self, company):
        """Perform targeted Google search"""
        template = random.choice(self.search_templates)
        query = template.format(company=company)
        encoded_query = quote_plus(query)
        
        search_url = f"https://www.google.com/search?q={encoded_query}&num=10"
        try:
            self.driver.get(search_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
            self.humanized_delay(3, 6)
            return True
        except Exception as e:
            logging.error(f"Search failed for {company}: {str(e)}")
            return False

    def clean_linkedin_url(self, url):
        """Extract clean LinkedIn profile URL from Google redirect URL"""
        try:
            # Handle Google redirect URLs
            if 'google.com' in url and '/url?' in url:
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                if 'url' in query_params:
                    actual_url = query_params['url'][0]
                else:
                    actual_url = url
            else:
                actual_url = url
            
            # Remove fragments and query parameters from LinkedIn URLs
            if 'linkedin.com/in/' in actual_url:
                # Extract the base LinkedIn profile URL
                match = re.search(r'(https?://[^/]*linkedin\.com/in/[^/?#&]+)', actual_url)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logging.error(f"Error cleaning URL {url}: {str(e)}")
            return None

    def validate_executive(self, title_text, snippet_text):
        """Validate if result matches target executive criteria"""
        title_text = title_text.lower()
        snippet_text = snippet_text.lower()
        
        # Check for required titles
        title_match = any(re.search(r'\b' + title + r'\b', title_text) 
                         for title in self.target_titles)
        
        # Check for exclusion terms
        exclude_match = any(re.search(r'\b' + term + r'\b', f"{title_text} {snippet_text}")
                          for term in self.exclude_titles)
        
        return title_match and not exclude_match

    def extract_executive_profiles(self, company):
        """Extract and validate executive profiles - gets ALL LinkedIn URLs"""
        company_lower = company.lower()
        profiles = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Find all search result containers
        for result in soup.select('div.g'):
            # Look for any link that contains linkedin.com/in/
            links = result.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                
                # Check if this is a LinkedIn profile URL (any country domain)
                if 'linkedin.com/in/' in href:
                    # Clean the URL to get the actual LinkedIn profile
                    clean_url = self.clean_linkedin_url(href)
                    
                    if clean_url:
                        # Get title and snippet for validation
                        title_elem = result.select_one('h3')
                        snippet_elem = result.select_one('div.VwiC3b, div.s, .st')
                        
                        title_text = title_elem.get_text() if title_elem else ""
                        snippet_text = snippet_elem.get_text() if snippet_elem else ""
                        
                        # Check if company name appears in the result
                        full_text = f"{title_text} {snippet_text}".lower()
                        
                        if company_lower in full_text:
                            profiles.append({
                                'url': clean_url,
                                'title': title_text,
                                'snippet': snippet_text
                            })
                            logging.info(f"LinkedIn profile found: {title_text} - {clean_url}")
        
        # Remove duplicates based on URL
        unique_profiles = []
        seen_urls = set()
        
        for profile in profiles:
            if profile['url'] not in seen_urls:
                unique_profiles.append(profile)
                seen_urls.add(profile['url'])
        
        # Return just the URLs, or you can return the full profile info
        return [profile['url'] for profile in unique_profiles]

    def process_companies(self):
        """Main processing flow"""
        try:
            self.df = pd.read_excel(self.excel_path)
            if 'Company' not in self.df.columns:
                raise ValueError("Missing required 'Company' column")
            
            self.df['Executive Profiles'] = ''
            
            if not self.init_driver():
                return False

            for idx, row in self.df.iterrows():
                company = str(row['Company']).strip()
                if not company or pd.isna(company):
                    continue
                
                logging.info(f"Processing: {company}")
                
                if self.execute_search(company):
                    profiles = self.extract_executive_profiles(company)
                    if profiles:
                        self.df.at[idx, 'Executive Profiles'] = ' | '.join(profiles)
                        logging.info(f"Found {len(profiles)} LinkedIn profiles for {company}")
                        self.save_progress()
                
                # Randomized delay between searches
                self.humanized_delay(7, 15)

            return True
            
        except Exception as e:
            logging.error(f"Processing error: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
            self.save_progress()

    def save_progress(self):
        """Save results to Excel"""
        output_path = os.path.splitext(self.excel_path)[0] + '_EXECUTIVES.xlsx'
        self.df.to_excel(output_path, index=False)
        logging.info(f"Progress saved to: {output_path}")

if __name__ == "__main__":
    scraper = ExecutiveScraper(r"F:\Flipcarbon\2025\5.May\24-05-2025\Logistics Directors.xlsx")
    scraper.process_companies()