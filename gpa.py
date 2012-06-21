import cgi
import datetime
import webapp2
import bs4
import os

from datetime import datetime
import urllib
from bs4 import BeautifulSoup

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template



class MainPage(webapp2.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    template_values = {}
    self.response.out.write(template.render(path, template_values))

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
    
    try:
      con = urllib.urlopen(link)
      html = con.read()
      flag = 1
    except:
	  resultmsg="Server error: Could not be reached"
	  flag = 0
	
    
    if (flag==1):
      soup = BeautifulSoup(html)
      table = soup.find('table', height="315")
      name = table.findAll('th')[1].text
      regno = table.findAll('th')[0].text
      rows = table.findAll('tr')
    
      dic={}
      lis=[]
	
      for i in range(2,len(rows)):
        dic={}
        cols = rows[i].findAll('td')
        dic["subject"]=cols[0].text
        dic["credit"]=int(cols[1].text)
        dic["grade"]=cols[2].text
        dic["result"]=cols[3].text
        lis.append(dic)
      def resolve(x):
		return { 
			'S':10,
			'A':9,
			'B':8,
			'C':7,
			'D':6,
			'E':5
			}[x]	
      sumCredit=0
      sumGPA=0
      for i in range(len(lis)):
		  if lis[i]["result"].strip()=="PASS":
			  tempGPA = lis[i]["credit"]*resolve(lis[i]["grade"].strip())    
			  sumGPA = float(sumGPA+tempGPA)
			  sumCredit = float(sumCredit+lis[i]["credit"])
		  else:
			  continue
    

		  
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
      else:
       template_values = {}
       path = os.path.join(os.path.dirname(__file__), 'templates/regerror.html')
       self.response.out.write(template.render(path, template_values))    
    
    else:
	   template_values = {}
	   path = os.path.join(os.path.dirname(__file__), 'templates/servererror.html')
	   self.response.out.write(template.render(path, template_values))   
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/sign', RenderMarksheet)
], debug=True)
