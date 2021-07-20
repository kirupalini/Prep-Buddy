from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from nltk import word_tokenize
from collections import Counter
import re
import nltk
import pandas as pd
import math
import random

def get_bot_response(userText):
    chatbot = ChatBot('Buddy')
    return chatbot.get_response(userText)

