import time
import os
from typing import List, Dict, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from sqlalchemy.orm import Session
from app import models
from app.config import get_settings

settings = get_settings()


class WebCrawler:
    def __init__(self, db: Session, headless: bool = True):
        self.db = db
        self.headless = headless
        self.driver = None
        self.wait_timeout = 10
    
    def init_driver(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(5)
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def login(self, login_url: str, username: str, password: str, 
              username_selector: str = None, password_selector: str = None,
              submit_selector: str = None):
        try:
            self.driver.get(login_url)
            time.sleep(2)
            
            if username_selector:
                username_input = self.driver.find_element(By.CSS_SELECTOR, username_selector)
                username_input.send_keys(username)
            
            if password_selector:
                password_input = self.driver.find_element(By.CSS_SELECTOR, password_selector)
                password_input.send_keys(password)
            
            if submit_selector:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_selector)
                submit_button.click()
            
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def crawl_interface(self, interface_id: int, url: str, task_id: int = None) -> Tuple[List[Dict], str | None]:
        try:
            self.driver.get(url)
            time.sleep(2)
            
            screenshot_path = self.take_interface_screenshot(interface_id, task_id)
            
            texts = self.extract_texts_from_page()
            
            text_elements = []
            for text_data in texts:
                text_element = models.TextElement(
                    interface_id=interface_id,
                    element_path=text_data['path'],
                    text_content=text_data['text'],
                    element_type=text_data['type'],
                    collect_status=1
                )
                text_elements.append(text_element)
            
            return text_elements, screenshot_path
        except Exception as e:
            print(f"Crawl interface {url} failed: {str(e)}")
            return [], None
    
    def take_interface_screenshot(self, interface_id: int, task_id: int = None) -> str | None:
        if not self.driver:
            return None
        
        try:
            screenshot_dir = os.path.join(settings.REPORT_OUTPUT_DIR, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_prefix = f"task{task_id}_" if task_id else ""
            filename = f"{task_prefix}interface_{interface_id}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            self.driver.save_screenshot(filepath)
            print(f"Screenshot saved: {filepath}")
            
            return filepath
        except Exception as e:
            print(f"Take screenshot failed: {str(e)}")
            return None
    
    def extract_texts_from_page(self) -> List[Dict]:
        texts = []
        
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for btn in buttons:
                text = btn.text.strip()
                if text:
                    texts.append({
                        'text': text,
                        'path': self.get_element_path(btn),
                        'type': 'button'
                    })
        except Exception as e:
            print(f"Extract buttons failed: {str(e)}")
        
        try:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                text = link.text.strip()
                if text:
                    texts.append({
                        'text': text,
                        'path': self.get_element_path(link),
                        'type': 'link'
                    })
        except Exception as e:
            print(f"Extract links failed: {str(e)}")
        
        try:
            labels = self.driver.find_elements(By.TAG_NAME, 'label')
            for label in labels:
                text = label.text.strip()
                if text:
                    texts.append({
                        'text': text,
                        'path': self.get_element_path(label),
                        'type': 'label'
                    })
        except Exception as e:
            print(f"Extract labels failed: {str(e)}")
        
        try:
            spans = self.driver.find_elements(By.TAG_NAME, 'span')
            for span in spans:
                text = span.text.strip()
                if text and len(text) > 1:
                    texts.append({
                        'text': text,
                        'path': self.get_element_path(span),
                        'type': 'text'
                    })
        except Exception as e:
            print(f"Extract spans failed: {str(e)}")
        
        try:
            divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="title"], h1, h2, h3, h4, h5, h6')
            for div in divs:
                text = div.text.strip()
                if text and len(text) > 1:
                    texts.append({
                        'text': text,
                        'path': self.get_element_path(div),
                        'type': 'title'
                    })
        except Exception as e:
            print(f"Extract titles failed: {str(e)}")
        
        unique_texts = []
        seen = set()
        for text_data in texts:
            if text_data['text'] not in seen:
                seen.add(text_data['text'])
                unique_texts.append(text_data)
        
        return unique_texts
    
    def get_element_path(self, element) -> str:
        try:
            if element.get_attribute('id'):
                return f"#{element.get_attribute('id')}"
            
            path = []
            current = element
            while current.tag_name.lower() != 'html':
                tag = current.tag_name.lower()
                classes = current.get_attribute('class')
                if classes:
                    class_list = classes.split()
                    if class_list:
                        tag += f".{class_list[0]}"
                path.insert(0, tag)
                current = current.find_element(By.XPATH, '..')
            
            return ' > '.join(path)
        except Exception:
            return "unknown"
    
    def take_screenshot(self, filepath: str):
        if self.driver:
            self.driver.save_screenshot(filepath)
