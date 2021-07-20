import pandas as pd
import json
import nltk
import re
from nltk.corpus import stopwords 
import os
import time
import test
from flask import Flask,redirect,url_for,request,make_response,render_template
def init():
    nltk.download('stopwords')

def preprocess(data):
  other_words = []
  stop_words = set(stopwords.words('english')) 
  for ind,row in enumerate(data):
    row = row.lower()
    row = re.sub('\s+',' ',row)
    row = re.sub(r'[^a-zA-z0-9\s]','',row)
    if len(row.split()) == 1:
      row = row.strip()
    else:
      row = ''
      for f in row.split():
        other_words.append(f)
    data[ind] = row
  data = [f for f in data if f != '' and f not in stop_words]
  for f in other_words:
    data.append(f)
  return list(set(data))

def keyword_search(subject,staffs,term):
    p1 = './Upload Folder/' + subject + '/keyword_indices.json'
    p2 = './Upload Folder/' + subject + '/metadata.json'
    with open(p1,'r') as f:
        map = json.load(f)
    with open(p2,'r') as f:
        df = json.load(f)
        df = pd.DataFrame.from_dict(df,orient = 'columns')
    term = preprocess(term.split())
    indices = []
    for word in term:
        if word in map.keys():
            indices.append(map[word])
    ans = ""
    hyper_link_format = '<a href = "{link}">{text}</a>'
    if len(indices) > 0:
        result = set(indices[0])
        for i in range(1,len(indices)):
            result = result.intersection(set(indices[i]))
        for res in result:
            if df['Author'][res] in staffs:
                ptemp = './Upload Folder/' + subject + '/' + df['Author'][res]
                filename = df['Chapter'][res]
                files = os.listdir(ptemp)
                #print(files)
                ext = ''
                for f in files:
                  if filename in f:
                    ext = f.split('.')[-1]
                cur = test.mysql.connection.cursor()
                cur.execute("Select name from faculty where username = %s",[df['Author'][res]])
                user = cur.fetchone()
                temp12 = user[0]
                ans += "Author : " + temp12 + "<br>"
                ans += "Topic : " + df['Topic'][res] + "<br><br>"
                ans += df['Paragraph'][res] + "<br><br>"
                id = df['Author'][res]
                l = url_for("download",id = id,filename = filename + '.' + ext)
                link = hyper_link_format.format(link = l,text = filename)
                ans += "Extracted from document : " + link + "<br><br>"
    if len(ans) == 0:
            ans = 'No results found'
            return ans
    time.sleep(2)
    return ans
    