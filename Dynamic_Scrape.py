
# coding: utf-8

# In[1]:

from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


# In[3]:

class Scrape_html(object):
    
    def __init__(self):
        try:
            self.driver = webdriver.Firefox()
        except Exception as e:
            print(e)
        
    
    def get_html(self,url,name,keyword):
        driver = self.driver
        try:
            driver.get(url)
            search = driver.find_element_by_name(name)
            WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.NAME, name)))
            search.send_keys(keyword)
            search.submit()
            WebDriverWait(driver, 20).until(
            EC.url_changes(url)) 
            #search.send_keys(Keys.RETURN)
            #driver.forward()
            html_page = driver.page_source
        except Exception as e:
            print(e)
        return (html_page)
    
    def end_session(self):
        self.driver.quit()
    
        


# In[ ]:



