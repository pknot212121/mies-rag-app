import pandas as pd
import os
from jsonpath_ng import jsonpath, parse
import json
import openpyxl
import re
import spacy

def get_docs_from_json(file):
    '''
    A Simple way to segmentate json text into sentences using spacy
    '''
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    text = data[0]["text"]
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return sentences