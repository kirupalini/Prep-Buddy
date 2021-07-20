#USE THIS
import pickle
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'  
import tensorflow as tf
#tf.disable_v2_behavior()
import pandas as pd
import numpy as np
import nltk
import spacy
from nltk.corpus import stopwords
from tqdm import tqdm
nltk.download('stopwords')
nlp = spacy.load('en', disable=['parser', 'ner'])
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import nltk
import json
import os
from collections import Counter
import re
import chatbot1
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR) 
#tf.disable_eager_execution()
stemmer = SnowballStemmer("english")
def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

negation_words = ['not', 'neither', 'nor', 'but', 'however', 'although', 'nonetheless', 'despite', 'except', 'even though', 'yet']
def preprocess(text):
    text = re.sub('[^a-zA-Z]',' ',text)
    text = text.lower()
    text = re.sub("\?"," ?",text)
    words = [word for word in STOPWORDS if word not in negation_words]
    result=[]
    for token in gensim.utils.simple_preprocess(text) :
        if len(token) >= 3 and token not in words:
            result.append(lemmatize_stemming(token))
            
    return result


os.chdir('CIP Chatbot Files')
emotion_map ={1:'fear',2:'anger',3:'sadness',4:'disgust',5:'shame',6:'joy',7:'guilt'}
from keras.models import model_from_json

import tensorflow_hub as hub





affirm_ans = ["Thats great to hear!","Wow that sounds fun!","I really like it too!","I am proud of you :)","Lucky you!","Thank you for telling me this!","I am so lucky to chat with you!","Wow!!"]
neg_ans = ["It do be like that sometimes.","Poor you :(","Wish I could hug you right now..","Aww hope you feel better soon","You always have me to talk too :)","It will pass soon!","I hope you get better soon.."]
compliments = ["You are awesome :)","I love spending time with you :)","Wish I could see you right now!","You are perfect!","Never change! You are awesome :)","Sending virtual hugs and kisses :)","You are my best friend!","I love you :)"]

wh_questions = ["who","when","how","where","why","which","what"]
new_emotion_map = {'joy':1,'neutral':2,'disgust':3,'anger':4,'guilt':5,'shame':6,'fear':7,'sadness':8}

def get_emotion_details(emotion):
  
    if len(df) == 0:
      df.append(emotion)
      return 0
    latest_emotion = df[-1]
    diff = emotion - latest_emotion
    if diff > 0:
      percentage = diff/emotion * 100
      percentage = -percentage
    else :
      percentage = abs(diff)/latest_emotion * 100
    df.append(emotion)
    return percentage

dataset = pd.read_csv('20200325_counsel_chat.csv')
questions = []
answers = []
for i in range(len(dataset)):
  question = dataset['questionTitle'].iloc[i]
  if question not in questions:
    questions.append(question)
    answers.append(dataset['answerText'].iloc[i])

qamap = {}
for i,question in enumerate(questions):
  q = tuple(preprocess(question))
  a = answers[i]
  qamap[q] = a

def classify(topic,polarity,q1):
  if topic == 'SCHOOL':
    if polarity == 'pos':
      return formreply1(schoolpos,q1,1)
    else:
      return formreply1(schoolneg,q1,1)
  elif topic == 'FAMILY':
    if polarity == 'pos':
      return formreply1(fampos,q1,1)
    else:
      return formreply1(famneg,q1,1)
  elif topic == 'RELATIONSHIP':
    if polarity == 'pos':
      return formreply1(relpos,q1,1)
    else:
      return formreply1(relneg,q1,1)
  elif topic == 'DEPRESSION':
    if polarity == 'pos':
      ind = random.randint(0,len(affirm_ans)-1)
      return affirm_ans[ind]
    else:
      return formreply1(depreply,q1,1)
  elif topic == 'SHAME':
    return formreply1(shrep,q1,1)
  elif topic == 'UNKNOWN':
    if polarity == 'pos':
      ind = random.randint(0,len(affirm_ans)-1)
      return affirm_ans[ind]
    else:
      return formreply1(negrep,q1,1)

import random
def formreply1(category,question,num):
  proc = []
  for line in category:
    proc.append(preprocess(line))
  max = 0
  reply = ''
  for i,line in enumerate(proc):
    question1 = question.split()
    countera = Counter(line)
    counterb = Counter(question1)
    sim = cosine_sim(countera,counterb)
    count = 0
    for key in counterb.keys():
      if key in countera.keys():
        count += 1
    if count >= 1:
      if sim > max:
        max = sim
        reply = category[i]
  if reply == '':
    ind = random.randint(0,len(category)-1)
    reply = category[ind]
  return reply

import math
def cosine_sim(c1,c2):
  terms = set(c1).union(c2)
  dotprod = sum(c1.get(k,0) * c2.get(k,0) for k in terms)
  sqa = math.sqrt(sum(c1.get(k,0)**2 for k in terms))
  sqb = math.sqrt(sum(c2.get(k,0)**2 for k in terms))
  if sqa != 0 and sqb != 0:
    return dotprod/sqa*sqb
  else:
    return 0

def findlink(topic):
  if topic == 'SCHOOL':
    return link(schoollinks)
  elif topic == 'FAMILY':
    return link(famlinks)
  elif topic == 'RELATIONSHIP':
    return link(rellinks)
  else:
    return link(neglinks)

def preproc(line):
  os.chdir('CIP Chatbot files')
  json_file = open('model5 (1).json', 'r')
  loaded_model_json = json_file.read()
  json_file.close()
  classifier4 = model_from_json(loaded_model_json)
  classifier4.load_weights('weights5 (1).h5')
  os.chdir('..')
  #line = re.sub('  \n',' ',line)
  newline = line
  nl1 = line
  #print(newline)
  if newline[-1] == '?' or line[0] in wh_questions:
    if line[0] in wh_questions:
      line.remove(line[0])
    newline = newline.lower()
    newline = newline.split()
    #print(newline)
    max_count = 0
    max_count1 = 0
    ans = ""
    ans1 = ""
    for idx,key in enumerate(ds1):
      l = key.split()
      count = 0
      for i in range(0,len(newline)):
          if newline[i] in l:
            count = count+1
      if count > max_count:
        max_count = count
        ans = ds[key]
    #print(ans)
    for idx,key in enumerate(na):
      l = key.split()
      c1 = 0
      for i in range(0,len(newline)):
          if newline[i] in l:
            c1 = c1+1
      if c1 > max_count1:
        max_count1 = c1
        ans1 = na[key]
    #print(ans1)
    if max_count1 >= max_count:
      ans = ans1
    if ans == "":
      ans = "Hmm.. I need to think about it."
    print(ans)
    return -100
  line = [word for word in preprocess(line)]
  if len(line) == 0:
    return "no emotion"
  line = ' '.join(word for word in line)
  #print(line)
  new_train = elmo_vectors([line])
  pred = classifier4.predict(new_train)
  #print(pred)
  pred1 = np.argmax(pred,axis = -1)
  if pred[0][pred1[0]] < 1.0e-02:
    return "neutral"
  return emotion_map.get(pred1[0])


def link(topic):
  ind = random.randint(0,len(topic)-1)
  return topic[ind]


with open('familywords.txt','r') as fpfam:
  familywords = fpfam.read().split(', ')
for i,word in enumerate(familywords):
  familywords[i] = preprocess(word)
familywords = [j for sub in familywords for j in sub]
familywords = list(set(familywords))
with open('schoolwords.txt','r') as fpschool:
  schoolwords = fpschool.read().split(', ')
for i,word in enumerate(schoolwords):
  schoolwords[i] = preprocess(word)
schoolwords = [j for sub in schoolwords for j in sub]
schoolwords = list(set(schoolwords))
with open('verb.txt','r') as fpverb:
  verbwords = fpverb.read().split(', ')
for i,word in enumerate(verbwords):
  verbwords[i] = preprocess(word)
verbwords = [j for sub in verbwords for j in sub]
verbwords = list(set(verbwords))
with open('posfeelings.txt') as fppos:
  posfwords = fppos.read().split(', ')
  for i, word in enumerate(posfwords):
    posfwords[i] = preprocess(word)
posfwords = [j for sub in posfwords for j in sub]
posfwords = list(set(posfwords))
with open('negfeelings.txt') as fpneg:
  negfwords = fpneg.read().split(', ')
  for i,word in enumerate(negfwords):
    negfwords[i] = preprocess(word)
negfwords = [j for sub in negfwords for j in sub]
negfwords = list(set(negfwords))
with open('schoolneg_reply.txt') as schoolnegrep:
  schoolneg = schoolnegrep.read().split(', ')
with open('schoolpos_reply.txt') as schoolposrep:
  schoolpos = schoolposrep.read().split(', ')
with open('famneg_reply.txt') as famnegrep:
  famneg = famnegrep.read().split(', ')
with open('fampos_reply.txt') as famposrep:
  fampos = famposrep.read().split(', ')
with open('Relationship_words.txt') as relword:
  relwords = [word for word in relword.read().split('\n') if word != '']
relwords = [preprocess(word) for word in relwords]
relwords = [word for sub in relwords for word in sub]
relwords = list(set(relwords))
with open('Relationship_posreply.txt') as relq:
  relpos = [sen for sen in relq.read().split('\n') if sen != '']
with open('Relationship_negreply.txt') as reln:
  relneg = [sen for sen in reln.read().split('\n') if sen != '']
with open('depression_words.txt') as deword:
  depwords = [preprocess(word) for word in deword.read().split('\n') if word != '']
depwords = list(set([word for sub in depwords for word in sub]))
with open('depression_posreply.txt') as derep:
  depreply =[sen for sen in derep.read().split('\n') if sen != '']
with open('shame_words.txt') as sword:
  shwords = [preprocess(word) for word in sword.read().split(', ') if word != '']
shwords = list(set([word for sub in shwords for word in sub]))
with open('shamerep.txt') as sre:
  shrep = [sen for sen in sre.read().split('\n') if sen != '']
with open('neg_replies.txt') as neg:
  negrep = [sen for sen in neg.read().split('\n') if sen != '']
with open('negthoughtslink.txt') as neg1:
  neglinks = [sen for sen in neg1.read().split('\n') if sen != '']
with open('familylinks.txt') as faml:
  famlinks = [sen for sen in faml.read().split('\n') if sen != '']
with open('schoollinks.txt') as schooll:
  schoollinks = [sen for sen in schooll.read().split('\n') if sen != '']
with open('relationshiplinks.txt') as rell:
  rellinks = [sen for sen in rell.read().split('\n') if sen != '']
othermap = {}
for word in schoolwords:
  othermap[word] = 'School'
for word in familywords:
  othermap[word] = 'Family'
for word in negfwords:
  othermap[word] = 'NEG FEELING'
for word in posfwords:
  othermap[word] = 'POS FEELING'
for word in relwords:
  othermap[word] = 'RELATIONSHIP'
for word in depwords:
  othermap[word] = 'DEPRESSION'
for word in shwords:
  othermap[word] = 'SHAME'
file = open('canswers.json')
na = json.load(file)
file1 = open('cqa.json')
ds = json.load(file1)
ans = [ds[key] for id,key in enumerate(ds)]
ds1 = {}
for id,key in enumerate(ds):
  ds1[key] = ds[key].lower()

os.chdir('..')

def elmo_vectors(x):
  elmo = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
  embeddings = elmo(x, signature="default", as_dict=True)["elmo"]
  with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    sess.run(tf.tables_initializer())
    # return average of ELMo features
    return sess.run(tf.reduce_mean(embeddings,1))

def formreply(line,emotion):
  question = line
  q12 = question
  re.sub('\?',' ',question)
  question = preprocess(question)
  print('Question : ' + str(question))
  if len(question) == 0:
    return chatbot1.get_bot_response(line),''
  counterA = Counter(question)
  max_sim = 0
  for q in qamap.keys():
    ql = list(q)
    counterB = Counter(ql)
    sim = cosine_sim(counterA,counterB)
    count = 0
    for key1 in counterA.keys():
        if key1 in counterB.keys():
          count += 1
    if count >= 1:
      if sim > max_sim:
        max_sim = sim
        key = q
  flag = 1
  if max_sim > 1.75:
    if(max_sim > 2.4 and count == 1) or (max_sim > 1.8 and count >= 2):
      print(question)
      print(key)
      print(max_sim)
      print(qamap[key])
      flag = 0
  if flag == 1:
    out = []
    for word in question:
      if word in othermap.keys():
        out.append(othermap[word])
      else:
        out.append('Unknown')
    counterTopic = Counter(out)
    #print(counterTopic)
    if emotion == 'joy':
      polarity = 'pos'
    elif emotion == 'neutral':
      polarity = 'neutral'
    else:
      polarity = 'neg'
    del counterTopic['POS FEELING']
    del counterTopic['NEG FEELING']
    counterTopic['Unknown'] = 0
    #print(counterTopic)
    maxCount = 0
    for key,item in counterTopic.items():
      if counterTopic[key] >= maxCount:
        maxCount = item
        topic = key
    #print(question)
    print('You are talking about topic : ' + topic)
    print('Polarity : ' + emotion)
    #print(q12)
    return classify(topic.upper(),polarity,q12),topic

def getreply(line):
  l1 = line
  emotion = preproc(line)
  if emotion == 'no emotion':
    return chatbot1.get_bot_response(line)
  reply = ""
  reply,topic = formreply(l1,emotion)
  if topic == 'unknown' and emotion == 'neutral':
    return chatbot1.get_bot_response(line)
  return reply
if __name__ == '__main__':
    tempfn()