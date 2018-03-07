
# coding: utf-8

# In[1]:

# this file contain two classes 
# 1. Job - Class which takes dataframe path ,take the column and resume text clean  and find the similarity
# 2. File - Class to read the file and return the clean tetx at present Implemented only for docx ,
# to use this class download as .py and keep in the same folder where the main code cleint code is there and then 
# import it e.g import Job,import File also below the main code is written


# In[23]:

#import all the library 

#import Panda
import pandas as pd
# using lemmatization  in place of porter stemmer as gives more meaning base word as compared to stemmer
from nltk.stem import WordNetLemmatizer  

#used for the stop word removal 
from nltk.corpus import stopwords  

#regular expression used for unknown chrarater replacing with blank
import re 
#install Package gensim pip install gensim And import the library

from gensim import corpora, models, similarities


# In[24]:

def  getCleanData(text,tokenize=False):
        stops = set(stopwords.words("english"))
        txt = str(text)
        txt = re.sub(r'[^A-Za-z0-9\s]',r' ',txt)  # if any other than A-z0-9 Replaced with blank
        txt = re.sub(r'\n',r' ',txt)  #relpace the new line with blank
        txt = re.sub(r'\u',r' ',txt)  #relpace the new line with blank
    
       #Convert it into lower form
        txt = " ".join([w.lower() for w in txt.split()])
        
       #remove the stop word
        txt = " ".join([w for w in txt.split() if w not in stops])
    
        #get the base form of word
        st = WordNetLemmatizer()
        txt = " ".join([st.lemmatize(w) for w in txt.split()])

        if tokenize:
            tokens = [token for token in txt.split() ]
            return tokens
    
        return txt


# In[25]:

class Job:
    def __init__(self,dataFrame):
         self.job_df=dataFrame
         #self.job_df=pd.read_csv(jobDescDataPath)
            
               
     # ****Get Basic Info about Data Frame
    def getBasicInfoAboutDataFrame(self):
        print("\n\nData DataTypes:\n{}".format(self.job_df.dtypes))
        print("\nTrain Shape:\n{}".format(self.job_df.shape))
        print ("\n*********\n Missing Value Statistics:\n{}".format(self.job_df.isnull().sum()))
           
    def __getCleanDfColumn(self,colname):
        print colname
        self.job_df[colname+'_Clean'] = self.job_df[colname].map(lambda x: getCleanData(x,True))
        self.job_df.head()
       # return self.job_df
        
         #create Bag of Word like count vectorizer
    def getSimilarity(self,colname,resumeTextClean):
        #get Clean Data column
        self.__getCleanDfColumn(colname)
        colNameClean=colname+'_Clean'
        dictionary = corpora.Dictionary(self.job_df[colNameClean] ) 
        print dictionary.token2id 
        corpus = [dictionary.doc2bow(text) for text in self.job_df[colNameClean]]  #count vectorrizer for job description
        #count vectorizer for resume text
        resume_text_vec=dictionary.doc2bow(resumeTextClean.lower().split()) 
        #create LSI model fro jobdescription corpus
        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=5)
        resume_vec_lsi = lsi[resume_text_vec] # convert the query to LSI space 5 dimension 
        index = similarities.MatrixSimilarity(lsi[corpus])
        simsIndex = index[resume_vec_lsi]  #perform a similarity query against the corpus
        simsIndex = sorted(enumerate(simsIndex), key=lambda item: -item[1])
        
        #verify -print top ten similar document
        for i in range(10):
            print simsIndex[i]
        return simsIndex     
        


# In[26]:

import PyPDF2
import textract
import docx


# In[27]:

ValidExtension=["pdf","docx"]
class File(object):
    def __init__(self,filename):
        self.filename=filename
        self.extension=""
        #self.getFileExtension() private function
    def __getFileExtension(self):
        self.extension=self.filename.split('.')[-1]
        return self.extension
    def __checkExtension(self): ##private function
        self.__getFileExtension()
        if self.extension not in ValidExtension:
            print("Error:Not a valid File")
            return False
        else: 
            return True
    def readpdfFile(self):  
        content=""
        print self.filename
        pdfFileObj = open(self.filename,'rb')
       # read_pdf = PyPDF2.PdfFileReader(pdfFileObj)
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        noofpages = pdfReader.numPages
        print(" Number of Pages {}".format(noofpages))
        #read file 
        page = pdfReader.getPage(0)
        content= page.extractText()
      #  text = textract.process(self.filename)
       
       # print ("type of page_content {}".format(type(page_content)))
      #  print text  #need to finish
        print content.encode('utf-8')
    def readdocxFile(self):
        resumeCleanText=""
        if (self.__checkExtension()):
            doc = docx.Document(self.filename)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)
                ' '.join(fullText)
            #get clean text
            resumeCleanText=getCleanData(fullText)
            #return resumeCleanText
        else:
            print("File Extension in Not valid")          
        return resumeCleanText;
            
           
          
        

        
        


# In[28]:

#rf= File("resume.docx")

#Job_df=pd.read_csv("Naukri_JD.csv")



# In[29]:

#resume_text=rf.readdocxFile()

#Job_df["Final_Job_Req"] = Job_df["Location"]+" "+Job_df["Experience"]+" "+Job_df["Job Description"] 


# In[19]:

#pData=Job(Job_df) 


# In[20]:

#pData.job_df.head(2)


# In[21]:

#getCleanData
#pData.getSimilarity('Final_Job_Req',resume_text)


# In[ ]:

#get Clean


# In[ ]:



