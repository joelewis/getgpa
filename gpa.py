#import necessary base modules
import cgi
import datetime
import webapp2
import os

#import necessary secondary modules
from datetime import datetime
import urllib
from bs4 import BeautifulSoup

#import GAE essentials
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template


#Main Page with does nothing but, render the index.html with a form to input register no.
class MainPage(webapp2.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    template_values = {}
    self.response.out.write(template.render(path, template_values))

#Marksheet Page rendered with render.html
class RenderMarksheet(webapp2.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    template_values = {}
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    reg = self.request.get('content')  
    regstr = str(reg)
    rawlink="http://result.annauniv.edu/cgi-bin/result/result11gr.pl?regno="  
    link =rawlink+regstr
    flag = 0
   
   # Check if the connection is available    
    try:
      con = urllib.urlopen(link)
      html = con.read()
      flag = 1
    except:
	  resultmsg="Server error: Could not be reached"
	  flag = 0
	
    #Parse data from connection, if available
    if (flag==1):
      soup = BeautifulSoup(html)
      table = soup.find('table', height="315")
      name = table.findAll('th')[1].text
      regno = table.findAll('th')[0].text
      rows = table.findAll('tr')
    
      dic={}
      lis=[]
	  
	  # Build a list of dictionaries in python to hold the data, which removes need for a database! 
      for i in range(2,len(rows)):
        dic={}
        cols = rows[i].findAll('td')
        dic["subject"]=cols[0].text
        dic["credit"]=int(cols[1].text)
        dic["grade"]=cols[2].text
        dic["result"]=cols[3].text
        lis.append(dic)
      
      # Function to resolve grade into their numeric equivalent
      def resolve(x):
		return { 
			'S':10,
			'A':9,
			'B':8,
			'C':7,
			'D':6,
			'E':5
			}[x]	
      
      # Calculate sumGPA and sumCredit
      sumCredit=0
      sumGPA=0
      for i in range(len(lis)):
		  if lis[i]["result"].strip()=="PASS":
			  tempGPA = lis[i]["credit"]*resolve(lis[i]["grade"].strip())    
			  sumGPA = float(sumGPA+tempGPA)
			  sumCredit = float(sumCredit+lis[i]["credit"])
		  else:
			  continue
    

      # Check for exceptions, if not calculate the GPA		  
      flag1 = 0
      try:
        GPA = sumGPA/sumCredit
        flag1 = 1 
      except ZeroDivisionError:
		  flag = 0
      
      if (flag==1):
        GPA = round(GPA,3)
        template_values = {
            'regno': regno,
            'name' : name,
            'lis' : lis,        
			'GPA' : GPA,
         }
     
        path = os.path.join(os.path.dirname(__file__), 'templates/render.html')
        self.response.out.write(template.render(path, template_values))
      # Redirect to index.html if register no. was not found
      else:
       template_values = {}
       path = os.path.join(os.path.dirname(__file__), 'templates/regerror.html')
       self.response.out.write(template.render(path, template_values))    
    
    # Redirect if server error
    else:
	   template_values = {}
	   path = os.path.join(os.path.dirname(__file__), 'templates/servererror.html')
	   self.response.out.write(template.render(path, template_values))   

#Main Handler
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/sign', RenderMarksheet)
], debug=True)
