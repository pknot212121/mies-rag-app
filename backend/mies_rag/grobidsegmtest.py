import requests
import os
from lxml import etree

GROBID_URL = "http://localhost:8070"
FULLTEXT_ENDPOINT = "/api/processFulltextDocument"


def segment_with_grobid(filepath):
    '''
    Uses GROBID to segmentate text into acapits, abstracts, and section heads
    To use this you NEED to launch grobid in a docker container on localhost:8070.
    '''
    if os.path.exists(filepath):
        with open(filepath, 'rb') as pdf_file:
            files = {'input': pdf_file}
            response = requests.post(f"{GROBID_URL}{FULLTEXT_ENDPOINT}", files=files)
        tei_xml_string = response.text
    
    root = etree.fromstring(tei_xml_string.encode('utf-8'))
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    texts = []
    
    paragraphs = root.xpath('//tei:body//tei:p', namespaces=ns)
    for i, p in enumerate(paragraphs):
        if p.text:
            print(f"AKAPIT {i+1}: {p.text}")
            texts.append(p.text)
            
    abstract_paragraphs = root.xpath('//tei:front//tei:div[@type="abstract"]//tei:p', namespaces=ns)
    for p in abstract_paragraphs:
        if p.text:
            print(f"ABSTRAKT: {p.text.strip()}")
            texts.append(p.text)
    
    section_heads = root.xpath('//tei:body//tei:head', namespaces=ns)
    for head in section_heads:
        if head.text:
            print(f"SEKCJA: {head.text.strip()}")
            texts.append(p.text)
    
    return texts
            