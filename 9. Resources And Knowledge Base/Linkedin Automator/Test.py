import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration (Consider using a .env file or environment variables for credentials) ---
LINKEDIN_USERNAME = "balasubramanian.ganeshan@flipcarbon.in" # Replace with your email
LINKEDIN_PASSWORD = "Burner23!"         # Replace with your password
EXCEL_FILE_PATH = "linkedin_profiles.xlsx"        # Replace with your Excel file name
URL_COLUMN_NAME = "LinkedIn_URL"                    # Column name in Excel for profile URLs
NAME_COLUMN_NAME = "Name"                           # Column name for the person's first name (for personalization)
ROLE_COLUMN_NAME = "Role"                           # Column name for the role they are in or you're interested in

MESSAGE_TEMPLATE = """Hey [Dude],

Hope you're doing well! This is a bit out of the blue, but I recently checked out the [Role] and was wondering if you’d be open to referring me.

No pressure at all - just thought I’d reach out and ask. Would really appreciate any help!"""

# --- Helper Functions ---

def setup_driver():
    """Sets up the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (no browser window) - LinkedIn might detect this more easily
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=en-US") # Ensure consistent language for selectors
    # The following line attempts to use a user data directory to potentially preserve login sessions
    # Be very careful with this, as it stores your browsing data.
    # options.add_argument("user-data-dir=./chrome_profile") # Creates a chrome_profile folder

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        return None

def login_to_linkedin(driver, username, password):
    """Logs into LinkedIn."""
    print("Attempting to log in to LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print("Login form submitted.")

        # Wait for a bit to see if login was successful (e.g., feed page loads)
        # A more robust check would be to look for a specific element on the home page
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "global-nav-search")) # Example element on home page
        )
        print("Login likely successful.")
        return True
    except TimeoutException:
        print("Timeout during login. CAPTCHA or incorrect credentials or changed page structure?")
        # You might need to manually solve a CAPTCHA here.
        input("Please solve any CAPTCHA if present and press Enter to continue...")
        # Check again if login was successful
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
            print("Login successful after manual intervention.")
            return True
        except TimeoutException:
            print("Still not logged in after manual intervention. Exiting.")
            return False
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return False

def send_connection_request(driver, profile_url, first_name, role):
    """Navigates to profile, sends connection request with a note."""
    print(f"\nProcessing profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(5) # Allow page to load

    try:
        # --- Step 1: Find the "Connect" button ---
        # LinkedIn's connect button can be tricky and its structure changes.
        # Common patterns:
        # 1. Direct "Connect" button on the profile.
        # 2. "More" button, then "Connect" in a dropdown.

        connect_button = None
        try:
            # Try to find a direct "Connect" button
            # This XPath looks for a button within the main profile actions area
            # that has a span containing the text "Connect".
            # This is highly likely to change.
            connect_button_xpath = "//div[contains(@class, 'pvs-profile-actions')]//button[.//span[text()='Connect']]"
            connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, connect_button_xpath))
            )
            print("Found direct 'Connect' button.")
        except TimeoutException:
            print("Direct 'Connect' button not found. Trying 'More...' then 'Connect'.")
            # If direct "Connect" not found, try the "More..." button
            # This XPath looks for a button that might be labeled "More"
            more_button_xpath = "//div[contains(@class, 'pvs-profile-actions')]//button[contains(@aria-label, 'More actions') or .//span[text()='More']]"
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, more_button_xpath))
            )
            more_button.click()
            time.sleep(1) # Wait for dropdown

            # Now find "Connect" in the dropdown
            # This XPath looks for an element within a dropdown that has the text "Connect"
            # The structure of this dropdown is also very volatile.
            connect_in_dropdown_xpath = "//div[@role='menuitem' and contains(., 'Connect')]" # Simpler, might work
            # A more specific one might be needed depending on LinkedIn's current HTML:
            # connect_in_dropdown_xpath = "//div[contains(@class, 'artdeco-dropdown__item')]//span[text()='Connect']/ancestor::div[@role='menuitem']"

            connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, connect_in_dropdown_xpath))
            )
            print("Found 'Connect' button in 'More...' dropdown.")

        if not connect_button:
            print(f"Could not find a 'Connect' button for {profile_url}. Skipping.")
            return False

        connect_button.click()
        print("Clicked 'Connect' button.")
        time.sleep(2) # Wait for modal to appear

        # --- Step 2: Click "Add a note" ---
        try:
            # This XPath looks for a button with aria-label "Add a note" or text "Add a note"
            add_note_button_xpath = "//button[@aria-label='Add a note'] | //button[span[text()='Add a note']]"
            add_note_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, add_note_button_xpath))
            )
            add_note_button.click()
            print("Clicked 'Add a note'.")
            time.sleep(1) # Wait for textarea to be ready
        except TimeoutException:
            print(f"Could not find 'Add a note' button for {profile_url}. Modal might have appeared differently or already allows note.")
            # Sometimes, the modal directly shows the text area. We'll try to find the text area anyway.
            # If "Add a note" is not found, it's possible the connection request was sent without a note, or an error occurred.
            # For now, we'll try to proceed to sending the note, assuming the text area might be visible.


        # --- Step 3: Paste the customized message ---
        try:
            message_area_xpath = "//textarea[@name='message' or @id='custom-message']" # Common identifiers
            message_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, message_area_xpath))
            )

            custom_message = MESSAGE_TEMPLATE.replace("[Dude]", first_name).replace("[Role]", role)
            message_area.send_keys(custom_message)
            print(f"Pasted message: {custom_message[:30]}...") # Log first few chars
            time.sleep(1)
        except TimeoutException:
            print(f"Could not find message text area for {profile_url}. Skipping message.")
            # If we can't find the message area, we might have to just send the request or cancel.
            # For now, let's try to find the send button anyway, in case the note was somehow pre-filled or not needed.
            # It's better to cancel if we can't add the note as intended.
            # print("Attempting to close the modal...")
            # try:
            #     close_button = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
            #     close_button.click()
            # except:
            #     driver.send_keys(Keys.ESCAPE) # Try escape key
            # return False # Indicate failure to send with note.

        # --- Step 4: Click "Send" (or "Send invitation") ---
        # The send button text might vary.
        try:
            send_button_xpath = "//button[@aria-label='Send now'] | //button[span[text()='Send']]" # Common options
            send_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, send_button_xpath))
            )
            send_button.click()
            print(f"Connection request sent to {first_name} for role {role} at {profile_url}.")
            return True
        except TimeoutException:
            print(f"Could not find 'Send' button for {profile_url} after trying to add note. Request might not have been sent or sent without note.")
            # Try to close the modal if send failed
            try:
                # Look for a dismiss or close button in the modal
                dismiss_button_xpath = "//button[@aria-label='Dismiss'] | //button[contains(@class, 'artdeco-modal__dismiss')]"
                dismiss_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, dismiss_button_xpath)))
                dismiss_button.click()
                print("Closed modal after failing to send.")
            except:
                print("Could not find dismiss button, trying ESCAPE key.")
                # Try sending ESCAPE key to close any modal
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            return False

    except NoSuchElementException as e:
        print(f"A specific element was not found on {profile_url}: {e}")
        # Check if already connected or pending
        if "message" in driver.page_source.lower() or "pending" in driver.page_source.lower():
            print(f"Already connected or request pending for {profile_url}. Skipping.")
        return False
    except TimeoutException as e:
        print(f"Timeout waiting for an element on {profile_url}: {e}")
        # Check if already connected or pending
        if "message" in driver.page_source.lower() or "pending" in driver.page_source.lower():
            print(f"Already connected or request pending for {profile_url}. Skipping.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred for {profile_url}: {e}")
        return False


# --- Main Script ---
if __name__ == "__main__":
    if LINKEDIN_USERNAME == "your_linkedin_email@example.com" or LINKEDIN_PASSWORD == "your_linkedin_password":
        print("ERROR: Please update LINKEDIN_USERNAME and LINKEDIN_PASSWORD in the script.")
        exit()

    driver = setup_driver()
    if not driver:
        print("Failed to initialize WebDriver. Exiting.")
        exit()

    if not login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD):
        print("LinkedIn login failed. Exiting.")
        driver.quit()
        exit()

    print("Login successful. Reading Excel file...")
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        if URL_COLUMN_NAME not in df.columns or NAME_COLUMN_NAME not in df.columns or ROLE_COLUMN_NAME not in df.columns:
            print(f"Excel file must contain columns: '{URL_COLUMN_NAME}', '{NAME_COLUMN_NAME}', and '{ROLE_COLUMN_NAME}'")
            driver.quit()
            exit()

    except FileNotFoundError:
        print(f"Error: Excel file not found at {EXCEL_FILE_PATH}")
        driver.quit()
        exit()
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        driver.quit()
        exit()

    successful_requests = 0
    failed_profiles = []

    for index, row in df.iterrows():
        profile_url = row[URL_COLUMN_NAME]
        first_name = str(row[NAME_COLUMN_NAME]) # Ensure it's a string
        target_role = str(row[ROLE_COLUMN_NAME])  # Ensure it's a string

        if pd.isna(profile_url) or not str(profile_url).startswith("http"):
            print(f"Skipping invalid URL at row {index+2}: {profile_url}")
            continue
        if pd.isna(first_name) or not first_name.strip():
            print(f"Skipping row {index+2} due to missing name for URL: {profile_url}")
            continue
        if pd.isna(target_role) or not target_role.strip():
            print(f"Skipping row {index+2} due to missing role for URL: {profile_url}")
            continue


        if send_connection_request(driver, profile_url, first_name, target_role):
            successful_requests += 1
            print(f"Successfully processed: {profile_url}")
        else:
            print(f"Failed to process: {profile_url}")
            failed_profiles.append(profile_url)

        # IMPORTANT: Add a significant delay to mimic human behavior and avoid detection
        # Randomize delay slightly
        import random
        delay_time = random.uniform(30, 90) # Delay between 30 and 90 seconds
        print(f"Waiting for {delay_time:.2f} seconds before next profile...")
        time.sleep(delay_time)

        # Optional: Limit the number of requests per run
        # if successful_requests >= 5: # Example limit
        #     print("Reached processing limit for this run.")
        #     break

    print("\n--- Script Finished ---")
    print(f"Total successful requests sent: {successful_requests}")
    if failed_profiles:
        print("Profiles that could not be processed or failed:")
        for url in failed_profiles:
            print(f"- {url}")

    input("Press Enter to close the browser and exit...")
    driver.quit()