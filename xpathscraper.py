import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, TimeoutException,StaleElementReferenceException
from base_logger import logger

IGNORED_EXCEPTION = (NoSuchElementException,TimeoutException,StaleElementReferenceException)
# options.add_argument('log-level=3') 
# 0: Only critical log messages are displayed
# 1: Display only warnings and errors
# 2: Display all messages except debug messages
# 3: Display all messages except debug and informational messages
# 99: Debugging messages are displayed

class XpathScraper:
    def __init__(self, timeout, options=None):
        if not options:
            options = webdriver.ChromeOptions()
            # set log level to suppress INFO messages
            # options.add_argument('--headless')
            options.add_argument('log-level=3')
            options.add_argument('--incognito')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-infobars')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--accept-cookie')
            # Add the following lines to click the "Accept all" button
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=site-per-process')
            options.add_argument('--disable-save-password-bubble')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('prefs', {'profile.default_content_setting_values.cookies': 2})            
            
        #self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.timeout = timeout
        
        
    def set_timeout(self, timeout):
        self.timeout = timeout


    def quit(self):
        self.driver.quit()


    def scrape(self, url:str, xpath:str):
        if url:
            self.driver.get(url)
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text
        except (NoSuchElementException,TimeoutException,StaleElementReferenceException) as e:
            logger.error(e.msg)
        except (NoSuchWindowException) as e:
            logger.error(e.msg)
            sys.exit()    
        

    def get_elements_from_xpath_list(self, url:str, xpath_list:list):
        element_text_list = []
        if url:
            self.driver.get(url)
        try:
            for xpath in xpath_list:
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                element_text_list.append(element.text)
        except (NoSuchElementException,TimeoutException,StaleElementReferenceException) as e:
            logger.error(e.msg)
        except (NoSuchWindowException) as e:
            logger.error(e.msg)
            sys.exit()
        return element_text_list


    def click_switch_page(self, url:str, xpath:str):
        if url:
            self.driver.get(url)
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            return element.parent.current_url
        except (NoSuchElementException,TimeoutException,StaleElementReferenceException) as e:
            logger.error(e.msg)   
        except (NoSuchWindowException) as e:
            logger.error(e.msg)   

    def click(self, url:str, xpath:str):
        if url:
            self.driver.get(url)        
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            return element.parent.current_url
        except (NoSuchElementException,TimeoutException,StaleElementReferenceException) as e:
            logger.error(e.msg)   
        except (NoSuchWindowException) as e:
            logger.error(e.msg)     

    def input_text(self, url:str, xpath:str, text:str):
        if url:
            self.driver.get(url)     
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.send_keys(text)
        except (NoSuchElementException,TimeoutException,StaleElementReferenceException) as e:
            logger.error(e.msg)   
        except (NoSuchWindowException) as e:
            logger.error(e.msg)
