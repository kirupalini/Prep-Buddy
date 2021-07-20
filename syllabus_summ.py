from bs4 import BeautifulSoup
import urllib.request
def summarize(a):
  b = ""
  f = open("summarise.txt","w")
  for ch in a:
    #print("Hey!!")
    if(ch!='-'):
      if(ch==' '):
        b=b+"_"
      else:
        b = b+ch
    else:
      URL = "https://en.wikipedia.org/wiki/"+b 
      try:
        page = urllib.request.urlopen(URL)
        #print(page)
        if(page==None):
          continue
        soup = BeautifulSoup(page,"html.parser")

        f = open("summarise.txt","a")
        #for data in soup.findAll('p',limit = 5):
        for data in soup.findAll("p",limit = 2):  
          sum = data.get_text()
          f.writelines(sum)
        f.write('\n')
        b = ""
      except:
        b = ""
    #f.write('\n')

    
  if(b!=""):
    URL = "https://en.wikipedia.org/wiki/"+b
    try:
      page = urllib.request.urlopen(URL)
      #print(page)
      if(page!=None):  
        soup = BeautifulSoup(page,"html.parser")
        f = open("summarise.txt","a")
        #for data in soup.findAll('p',limit = 5):
        for data in soup.findAll("p",limit = 2):  
          sum = data.get_text()
          f.writelines(sum)
    except:
      b = ""
  f.close()
  file = open("summarise.txt","r")
  contents = file.read()
  return contents