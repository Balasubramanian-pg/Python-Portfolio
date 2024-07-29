import pandas as pandas
from parsel import selector
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverwait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import options
from selenium.webdriver.common.keys import keys
opts = Options()


driver = webdriver.chrome(options=opts, executable_path ='chromedriver')

#function to ensure all key data fields have a value
def validate_field(field):
    #if field is present pass if field
    if field:
        pass
    #if field is not present print text else:
    eles:
        field = 'No results'
    return field

    #driver.get method() will navigate to a page given by the address
driver.get('https://www.linkedIn.com')
# Locate email form by_class_name
username = driver.find_element (By.ID, 'session_key')

#send_keys() to simulate key strokes
username.send_keys('YOUR EMAIL')

#sleep for 0.5 seconds
sleep(o.5)

#Locate password form by_class_name
password = driver.find_elements(By.ID,'session_password')

# send_keys to simulate key strokes
password.send_keys("YOUR PASSWORD")
sleep(0.5)

#locate submit button by_xpath
sign_in_button = driver.find_elements(By.X0ATH,'//*[@type="submit"]')

#.click() to mimic button click
sign_in_button.click()
sleep(15)






Jobdata = []
links = []
for x in range(0,20,10):
    driver.get(f'hyperlink goes here')
    time.sleep(random.unifrom(2.5,4.9))
    linkedIn_urls = [my.elem.get_attribute["href"] for my_elem is WebdriverWait(driver,20).until(EC.visibility_of_all_elements)]
    lnks.append(linkedin_url)

for x in lnks:
    for i in x:
        #get the profile URL
        driver.get(i)
        time.sleep(random.uniform(2.5,4.9))

        #assigning the source code for the web page to variable set
        set = selector(text=driver.page_source)

        #xpath to extract the text from the class containing the name
        name = sel.xpath('//"[starts-with(@class, "text-heading-xlarge inline t-24 v-align-middle break-words')]/text()).exit