# From: Eric Paiz
#from chatbot import PilotBot
from bs4 import BeautifulSoup
import time 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import requests

class Scraper: 
    
    
    def __init__(self):
        self.chat_messages = []
        
        

    def set_up(self): 
        
        options = Options()
        # options.add_argument('--headless')
        chromeDriverPath = '/usr/bin/chromedriver'
        options.add_experimental_option("detach", True)
        options.add_argument("--log-level=3 --silent") # Using this to supress the errors so only fatal ones show, to clean up the output.
        chromeService = ChromeService()
        self.driver = webdriver.Chrome(service=chromeService, options=options)
        return self.driver
    
    def targetChat(self, chat_choice, duration):
        try:
            time.sleep(1)
            url = f'https://kick.com/{chat_choice}/chatroom'
            print(f'Connecting to {chat_choice}...')
            time.sleep(1)
            print('Please wait...')
            self.driver.get(url)
            start_time = time.time()
            while time.time() - start_time < duration:

            
                SCROLL_PAUSE_TIME = 0.3
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                print('Parsing to begin.')
                    
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span[class="chat-entry-username"]'))
                    )
                while True:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    time.sleep(SCROLL_PAUSE_TIME)
                    
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                htmlContent = self.driver.page_source
                last_height = self.driver.execute_script("return document.body.scrollHeight")

                soup = BeautifulSoup(htmlContent, 'html.parser')
                
                user_names_target = soup.select('span[class="chat-entry-username"]')
                user_names = []
                for user_name in user_names_target:
                    user_name = user_name.get_text().strip().lower()
                    user_names.append(user_name)
    
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {type(e).__name__}: {e}")

        except Exception as e:
            print(f"An error occurred: {type(e).__name__}: {e}")


        finally:
            print("Closing Connection...")
            
            self.driver.quit()
            print("Connection closed.")

    def get_messages(self, duration, chat_choice):
        try:
            time.sleep(1)
            url = f'https://kick.com/{chat_choice}/chatroom'
            print(f'Connecting to {chat_choice}...')
            time.sleep(1)
            print('Please wait...')
            print('Parsing to begin.')
            self.driver.get(url)
            start_time = time.time()
            while time.time() - start_time < duration:

            
                SCROLL_PAUSE_TIME = 0.3
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                
                    
                WebDriverWait(self.driver, int(duration)).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span[class="chat-entry-content"]'))
                    )
                while True:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    time.sleep(SCROLL_PAUSE_TIME)
                    
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                htmlContent = self.driver.page_source
                last_height = self.driver.execute_script("return document.body.scrollHeight")

                soup = BeautifulSoup(htmlContent, 'html.parser')
                
                message_selectors = soup.select('span[class="chat-entry-content"]')
                
                for chat_message in message_selectors:
                    chat_message = chat_message.get_text().strip().lower()
                    self.chat_messages.append(chat_message)
                last_message = self.chat_messages[-1]
                

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {type(e).__name__}: {e}")

        except Exception as e:
            print(f"An error occurred: {type(e).__name__}: {e}")

    def printMessages(self):
        print(self.chat_messages)
