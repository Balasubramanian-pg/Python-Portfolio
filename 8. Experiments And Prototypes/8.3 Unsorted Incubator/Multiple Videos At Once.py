"""
YouTube Transcript Downloader - Batch Version with File Input
Supports both interactive input and reading URLs from a text file
"""
import time
import re
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def skip_ads(driver, timeout=30):
    """Check for ads and skip them if possible."""
    print("Checking for ads...")
    time.sleep(2)
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            skip_btn = driver.find_element(
                By.CSS_SELECTOR,
                ".ytp-ad-skip-button, .ytp-skip-ad-button"
            )
            if skip_btn.is_displayed():
                skip_btn.click()
                print("Skipped ad")
                time.sleep(1)
                return
        except:
            pass
        
        try:
            ad_showing = driver.find_elements(By.CLASS_NAME, "ytp-ad-player-overlay")
            if not ad_showing:
                print("No ads detected")
                return
        except:
            return
        
        time.sleep(1)


def create_driver(headless=False):
    """Create undetected Chrome driver."""
    options = uc.ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = uc.Chrome(
        options=options, 
        use_subprocess=True,
        version_main=144
    )
    driver.set_page_load_timeout(60)
    return driver


def get_video_title(driver, video_url):
    """Extract video title using multiple fallback methods."""
    video_title = None
    
    try:
        meta_elem = driver.find_element(By.CSS_SELECTOR, "meta[property='og:title']")
        video_title = meta_elem.get_attribute("content")
        print(f"Title found via meta tag")
    except NoSuchElementException:
        pass
    
    if not video_title:
        try:
            video_title = driver.execute_script("return document.title")
            video_title = re.sub(r'\s*-\s*YouTube$', '', video_title)
            print(f"Title found via document.title")
        except:
            pass
    
    if not video_title:
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, "h1.style-scope.ytd-watch-metadata")
            video_title = title_elem.text.strip()
            print(f"Title found via h1.ytd-watch-metadata")
        except:
            pass
    
    if not video_title:
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer")
            video_title = title_elem.text.strip()
            print(f"Title found via legacy selector")
        except:
            pass
    
    if not video_title or not video_title.strip():
        try:
            video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url).group(1)
            video_title = f"Transcript_{video_id}"
            print(f"Using video ID as filename")
        except:
            video_title = f"Transcript_{int(time.time())}"
            print(f"Using timestamp as filename")
    
    video_title = video_title.strip()
    print(f"Raw title: '{video_title}'")
    
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", video_title)
    safe_filename = safe_filename.replace(" ", "_")
    safe_filename = re.sub(r'_+', '_', safe_filename)
    safe_filename = safe_filename.strip('_.-')
    
    if not safe_filename or len(safe_filename) < 2:
        try:
            video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url).group(1)
            safe_filename = f"Transcript_{video_id}"
        except:
            safe_filename = f"Transcript_{int(time.time())}"
    
    print(f"Safe filename: '{safe_filename}'")
    return safe_filename, video_title


def download_transcript(video_url, headless=False):
    """Download transcript from single YouTube video."""
    driver = create_driver(headless=headless)
    
    try:
        print(f"Loading: {video_url}")
        driver.get(video_url)
        wait = WebDriverWait(driver, 25)
        
        skip_ads(driver)
        time.sleep(2)
        
        safe_filename, video_title = get_video_title(driver, video_url)
        
        try:
            expand_btn = wait.until(EC.presence_of_element_located((By.ID, "expand")))
            driver.execute_script("arguments[0].click();", expand_btn)
            time.sleep(1)
        except TimeoutException:
            print("Description already expanded or not found")
        
        print("Opening transcript...")
        try:
            transcript_btn = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ytd-video-description-transcript-section-renderer button")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", transcript_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", transcript_btn)
        except TimeoutException:
            try:
                transcript_btn = driver.find_element(By.XPATH, "//button[contains(., 'Show transcript')]")
                driver.execute_script("arguments[0].click();", transcript_btn)
            except:
                print("ERROR: Transcript button not found")
                return None
        
        try:
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "ytd-transcript-renderer")))
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "ytd-transcript-segment-renderer .segment-text")
                )
            )
            time.sleep(1.5)
        except TimeoutException:
            print("ERROR: Transcript didn't load")
            return None
        
        segments = driver.find_elements(By.CSS_SELECTOR, "ytd-transcript-segment-renderer")
        transcript_lines = []
        
        for seg in segments:
            try:
                timestamp = seg.find_element(By.CSS_SELECTOR, ".segment-timestamp").text.strip()
                text = seg.find_element(By.CSS_SELECTOR, ".segment-text").text.strip()
                if text:
                    transcript_lines.append(f"**[{timestamp}]** {text}")
            except:
                continue
        
        print(f"Extracted {len(transcript_lines)} segments")
        
        if not transcript_lines:
            print("WARNING: No transcript segments found")
            return None
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, f"{safe_filename}.md")
        
        counter = 1
        base_filename = safe_filename
        while os.path.exists(output_file):
            output_file = os.path.join(script_dir, f"{base_filename}_{counter}.md")
            counter += 1
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {video_title}\n\n")
            f.write(f"Source: {video_url}\n\n")
            f.write("\n\n".join(transcript_lines))
        
        print(f"✓ Saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            driver.save_screenshot("error.png")
            print("Screenshot saved to error.png")
        except:
            pass
        return None
        
    finally:
        driver.quit()
        print("Browser closed\n")


def process_multiple_videos(video_urls, headless=False):
    """Process multiple YouTube videos sequentially."""
    results = {
        'successful': [],
        'failed': []
    }
    
    total = len(video_urls)
    print(f"Starting batch processing of {total} videos\n")
    print("=" * 60)
    
    for idx, url in enumerate(video_urls, 1):
        print(f"\n[{idx}/{total}] Processing video...")
        print("-" * 60)
        
        try:
            output_file = download_transcript(url, headless=headless)
            
            if output_file:
                results['successful'].append({
                    'url': url,
                    'file': output_file,
                    'index': idx
                })
                print(f"✓ Video {idx} completed successfully")
            else:
                results['failed'].append({
                    'url': url,
                    'error': 'Failed to extract transcript',
                    'index': idx
                })
                print(f"✗ Video {idx} failed")
        
        except Exception as e:
            results['failed'].append({
                'url': url,
                'error': str(e),
                'index': idx
            })
            print(f"✗ Video {idx} crashed: {e}")
        
        if idx < total:
            print("\nWaiting 3 seconds before next video...")
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Successful: {len(results['successful'])}/{total}")
    print(f"Failed: {len(results['failed'])}/{total}")
    
    if results['failed']:
        print("\nFailed videos:")
        for item in results['failed']:
            print(f"  - [{item['index']}] {item['url']}")
            print(f"    Error: {item['error']}")
    
    return results


def read_urls_from_file(filepath):
    """Read YouTube URLs from a text file (one per line)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        return urls
    except FileNotFoundError:
        print(f"ERROR: File '{filepath}' not found")
        return []
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return []


if __name__ == "__main__":
    print("YouTube Transcript Batch Downloader")
    print("=" * 60)
    
    print("\nChoose input method:")
    print("1. Enter URLs manually")
    print("2. Read URLs from file")
    
    choice = input("\nYour choice (1 or 2): ").strip()
    
    urls = []
    
    if choice == '2':
        filepath = input("Enter path to file with URLs: ").strip()
        urls = read_urls_from_file(filepath)
        if urls:
            print(f"\nLoaded {len(urls)} URLs from file")
    else:
        print("\nEnter YouTube URLs (one per line, empty line to finish):")
        while True:
            url = input(f"URL {len(urls)+1} (or press Enter to finish): ").strip()
            if not url:
                break
            urls.append(url)
    
    if urls:
        # Ask if headless mode
        headless_choice = input("\nRun in headless mode? (y/n): ").strip().lower()
        headless = headless_choice == 'y'
        
        print(f"\nProcessing {len(urls)} videos...")
        results = process_multiple_videos(urls, headless=headless)
    else:
        print("No URLs provided")
