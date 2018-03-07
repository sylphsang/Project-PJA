
# coding: utf-8

# In[83]:

import pandas as pd
from bs4 import BeautifulSoup
from collections import OrderedDict
import time

import requests

import re
from Dynamic_Scrape import Scrape_html
import math


# In[84]:

#import urllib2
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


# In[85]:

labels = ['Salary', 'Industry', 'Functional Area', 'Job Title', 'Role','Employment Type']
edu_labels = ['UG', 'PG', 'Doctorate']


# In[103]:

class CreateDataFrameFromSource(object):
    
    #parse the job data 
    
    def __init__(self,url,name,keyword,source):
        self.name = name
        self.source = source
        self.keyword= keyword
        self.url = url
        self.ndf = pd.DataFrame()
        self.tdf = pd.DataFrame()
        self.mdf = pd.DataFrame()
        
        if self.source=='naukri':
            
            html = self.dynamic_scrape(url,name,keyword)
            #print html
            soup= BeautifulSoup(html,'lxml') 
            self.ndf =self.getNaukriDF(soup)
        elif self.source =='times':
            html = self.dynamic_scrape(url,name,keyword)
            soup= BeautifulSoup(html,'lxml') 
            #print(soup.prettify())
            self.tdf =self.getTimesDF(soup)
        elif self.source =='monster':
            html = self.dynamic_scrape(url,name,keyword)
            soup= BeautifulSoup(html,'lxml') 
            print(soup.prettify())
            self.tdf =self.getMonsterDF(soup)  
        else:
            print('Source not reachable')
            
    def dynamic_scrape(self,url,name,keyword):
        dynamic_scrape = Scrape_html()
        html = dynamic_scrape.get_html(url,name,keyword)
        return(html)
    def parseJobData(self,jd_soup):
        try:
            #url 
            url = jd_soup.find("a",{"itemprop":"url"}).getText().strip()
            
            #job descripttion
            jd_text = jd_soup.find("ul",{"itemprop":"description"}).getText().strip()

            #job location
            location = jd_soup.find("div",{"class":"loc"}).getText().strip()

            # Experience
            experience = jd_soup.find("span",{"itemprop":"experienceRequirements"}).getText().strip()

            role_info = [content.getText().split(':')[-1].strip() for content in jd_soup.find("div",{"class":"jDisc mt20"}).contents if len(str(content).replace(' ',''))!=0]
            role_info_dict = {label: role_info for label, role_info in zip(labels, role_info)}

            #key Skills
            key_skills = '|'.join(jd_soup.find("div",{"class":"ksTags"}).getText().split('  '))[1:]

            #edu_info
            edu_info = [content.getText().split(':') for content in jd_soup.find("div",{"itemprop":"educationRequirements"}).contents if len(str(content).replace(' ',''))!=0]


            #print (edu_info)

            edu_info_dict = {label.strip(): edu_info.strip() for label, edu_info in edu_info}
            for l in edu_labels:
                if l not in edu_info_dict.keys():
                    edu_info_dict[l] = ''

            company_name = jd_soup.find("div",{"itemprop":"hiringOrganization"}).contents[1].p.getText().strip()
        except AttributeError:
            return -1
        df_dict = OrderedDict({'Location':location, 'Link':url,'Job Description':jd_text,'Experience':experience,'Skills':key_skills,'Company Name':company_name})
        df_dict.update(role_info_dict)
        df_dict.update(edu_info_dict)  
        #time.sleep(1)
        return df_dict
    
    def getNaukriDF(self, soup):
        #https://www.naukri.com/c-jobs retrieve page wise data
        
        base_url = soup.link["href"]
        
        print base_url
            
        num_jobs = int(soup.find("div", { "class" : "count" }).h1.contents[1].getText().split(' ')[-1])
        print ('Total Number of jobs  :{}'.format(num_jobs))
        
        #extract number of pages as 50 job per page 
       
        #number of pages
        num_pages = int(math.ceil(num_jobs/50.0))
        #print total number of page
        if num_pages > 70:
            num_pages=70
        
        
        for page in range(1,num_pages+1): #replace  ith numpages+1 
            page_url = base_url+str(page)
            req = urllib2.Request(page_url, headers={'User-Agent' : "Magic Browser"}) 
            source = urllib2.urlopen( req ).read()
            soup = BeautifulSoup(source,"html.parser")
        
            all_links = [link.get('href') for link in soup.findAll('a') if 'job-listings' in  str(link.get('href'))]

            #print (all_links)

            #for all the link retrieve the data 
            naukri_df = pd.DataFrame()
        
            for url in all_links:

                req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})

                #job descrption data open the link in the browser
                jd_source = urllib2.urlopen(req).read()

                jd_soup = BeautifulSoup(jd_source,"html.parser")

                #parse job data
        
            
                if(self.parseJobData(jd_soup)==-1):
                    continue
                else:
                    naukri_df = naukri_df.append(self.parseJobData(jd_soup),ignore_index=True) 
                    
            print(page)
                
        return naukri_df
    
    def getTimesDF(self, soup):
        times_df=pd.DataFrame()
        #r=requests.get(times_url)
        #soup=BeautifulSoup(r.content,"lxml")
        all_links=[]
        for link in soup.select('h2 a[href]'):
            if "http" in link.get("href"):
                all_links.append(link['href'])
        links=list(set(all_links))

        for line in links:
            r = requests.get(line)
            soup=BeautifulSoup(r.content,"lxml")
            dict_object={}
            dict_object["Link"] = line
            desc=soup.find_all("section",{"id":"applyFlowHideDetails_2"})
            for item in desc:
                dict_object["Job Description"]= item.text.replace("\n", "").replace("Job Description","")
            desc=soup.find_all("div",{"class":"jd-comp-name"})
            for item in desc:
                #dict_object["Company_name"]= item.text.replace("\n", "")
                fields=item.text.replace("\n", " ").replace("  ","|").split('|')
                #print(fields[1])
                dict_object["Company Name"]=fields[1]
            desc=soup.find_all("ul",{"class":"job-more-dtl clearfix"})
            for item in desc:
                fields=item.text.replace("\n"," ").replace("  ","|").split('|')
                dict_object["Experience"]=fields[2]
                dict_object["Salary"]=fields[3]
                dict_object["Location"]=fields[4]
            df=pd.DataFrame([dict_object])
            times_df=times_df.append(df,ignore_index=True)
        return times_df
    
    def parseMonsterJobDetails(self,jd_soup):
        dict_object = {}

        i = str(jd_soup.find_all("h1", { "class" : "job_title_seo" })); #print(i)
        dict_object["Job Title"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", "")

        i = str(jd_soup.find_all("a", { "class" : "keylink lft" })); #print(i)
        dict_object["Skills"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", " ").replace("/^[ -~]+$/", " ")

        #i = str(jd_soup.find_all("h2", { "class" : "keyskill skillseotag" })[0]); #print(i)
        #print(re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", ""))

        i = str(jd_soup.find_all("h3")); #print(i)
        dict_object["Company Name"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", "")

        i = str(jd_soup.find_all("div", { "class" : "joblnk" })[0]); #print(i)
        dict_object["Location"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", "")

        i = str(jd_soup.find_all("div", { "class" : "joblnk" })[1]); #print(i)
        dict_object["Experience"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", "")

        #i = str(jd_soup.find_all("div", { "class" : "posted" })[0]); #print(i)
        #dict_object["Posted_On"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", "")

        #i = str(jd_soup.find_all("div", { "class" : "col-md-3 col-xs-12 pull-right jd_rol_section" })[0]); #print(i)
        #dict_object["short_desc"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("/^[ -~]+$/", "")

        i = str(jd_soup.find_all("div", { "class":"desc"})[0]); #print(i)
        dict_object["Job Description"] = re.sub(re.compile('<.*?>'), '', i).replace("\n", "").replace("\t", "").replace("/^[ -~]+$/", "")

        return pd.DataFrame([dict_object])
     #CREATE MONSTER DATAFRAME
    def getMonsterDF(self, soup):
        
        monster_df = pd.DataFrame()
        base_url = soup.link["href"]
        
        print base_url
            
       # num_jobs = int(soup.find("div", { "class" : "count" }).h1.contents[1].getText().split(' ')[-1])
       # print ('Total Number of jobs  :{}'.format(num_jobs))
        all_links=[]
        
        for link in soup.select('link[href]'):
            if "http" in link.get("href"):
                all_links.append(link['href'])
        links=list(set(all_links))        
        
        for line in links:
            r = requests.get(line)
            soup=BeautifulSoup(r.content,"lxml")
            
            elements = re.findall(r"sharebutton\(\'(.*?)\?from", str(soup)) 
            
            for item in elements:
                r = requests.get(item)
                soup=BeautifulSoup(r.content,"lxml")
                
                monster_df = monster_df.append(self.parseMonsterJobDetails(soup), ignore_index=True)
        return monster_df 



# In[104]:

#import CreateDFFromMultipleJobPortal
#from CreateDFFromMultipleJobPortal import CreateDataFrameFromSource
#import sys
#del sys.modules['CreateDFFromMultipleJobPortal'] 
#from CreateDFFromMultipleJobPortal import CreateDataFrameFromSource


# In[111]:

#naukri_url = 'https://www.naukri.com/browse-jobs'
#name = 'qp'
#keyword = 'machine learning'

#keyword = 'java'
#name = 'fts'
#monster_url = "http://www.monsterindia.com/"


# In[112]:

#ReadDF=CreateDataFrameFromSource(monster_url,name,keyword,'monster')


# In[ ]:

#ReadDF.mdf


# In[ ]:



