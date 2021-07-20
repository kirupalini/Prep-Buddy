from tika import parser
import pandas as pd
import numpy as np
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
import json
import re
from bs4 import BeautifulSoup
import urllib.request


def get_course_page(course_name):
  with open('PAGE_MAP.json') as f:
    df = json.load(f)
    #df

  sub_map = dict()
  count = 0
  for i in df['subject']:
    sub_map[i.lower()] = i

  course_name_lower = course_name.lower()
  count = 0
  if course_name_lower not in sub_map:
    return -1
  for i in df['subject']:
    if i==sub_map[course_name_lower]:
      break
    count+=1

  page_no = df['page'][count]

  page_from_pdf = ((int)(page_no)-1)

  return page_from_pdf

def create_paragraphs(content_final):
    paragraph = []
    for line in content_final:
        if line.isspace():
            if paragraph:
                yield ''.join(paragraph)
                paragraph = []
        else:
            paragraph.append(line)
    if paragraph:
        yield ''.join(paragraph)

def get_course_content(course_page,course_name):

  #parse content of the file and put only the 2 pages into output.pdf
  reader = PdfFileReader('18.IT final.pdf')
  writer = PdfFileWriter()
  
  my_page = reader.getPage(course_page)
  my_page_1 = reader.getPage(course_page+1)

  writer.addPage(my_page)
  writer.addPage(my_page_1)
  output_file = 'output.pdf'
  with open(output_file,'wb') as output:
    writer.write(output)

  file_data = (parser.from_file('output.pdf'))
  file_data_content = file_data['content']

  #Get only the course' content from the total file content
  #regex = '([A-Z][A-Z][0-9]*+\W*('+course_name.upper()+')[\s\w]*)'
  #regex = course_name.upper()
  #regex = regex+'[\s\w]*'
  #p = re.compile(regex)
 ##print(n1.string)
  #sub_str = course_name.upper()
  #if(bool(re.search(r'([A-Z][A-Z]([0-9])+\W*[A-Z]+[\W\w]+)',file_data_content))):
  #  c_name = [re.search(r'([A-Z][A-Z]([0-9])+\W*[A-Z]+\s[A-Z]+)',file_data_content)]
  #  for i in c_name:
  #    if(check(c_name,sub_str)):

  subjects = []
  n = re.search('([A-Z][A-Z]([0-9])+\W*[A-Z]+[\W\w]+)',file_data_content).group(1)
  #print(n)

  count = 0
  lines = n.splitlines(True)
  for line in lines:
    if (bool(re.search(r'\s*((TOTAL)\W+[0-9]+( PERIODS))\s+',line))):
      break
    count+=1

  #print(count)

  content_final = []
  c = 0
  for i in lines:
    if(c<=count):
      #print(i)
      content_final.append(i)
    c+=1

  #Seperate into paragraphs!
  l1 = list(create_paragraphs(content_final))
  
  return l1


def filter_unit(l1,unit_number):
  units = ['I','II','III','IV','V']
  if unit_number.split()[-1] not in units :
    return 'Not Found'
  count_para = 0
  for i in l1:
    count_para+=1

  searchwords = []
  searchwords.append(unit_number)

  df = pd.DataFrame({'id':count_para,'text':l1})
  df_2 = df[df['text'].str.startswith(tuple(searchwords))]
  if len(df_2) == 0:
    unit_number = '  '.join(unit_number.split())
    searchwords = [unit_number]
    df = pd.DataFrame({'id':count_para,'text':l1})
    df_2 = df[df['text'].str.startswith(tuple(searchwords))]
  numpy_array = df_2.to_numpy()
  np.savetxt("test_file.txt", numpy_array[0], fmt = "%s")

  file = open("test_file.txt","r")
  contents = file.read()
  return contents


def get_info(course_name, unit_number):
  course_page = get_course_page(course_name)
  if course_page == -1:
    return 'Not found'
  l1 = get_course_content(course_page,course_name)
 
  if(unit_number==""):
    h = 1
    return '\n'.join(f for f in l1)
  else:
    contents = filter_unit(l1,unit_number)
    return contents

