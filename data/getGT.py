#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 21:30:37 2017

@author: ngocbui
"""

import numpy as np
import xml.etree.ElementTree as r
import torch
import os
import re
import collections

def readSymbolfile(path):
    assert(os.path.exists(path))
    with open(path, 'r') as f:
        return f.read().replace("\n", " ").split()
    
def buildVocab(path):
    
    data = readSymbolfile(path)
    counter = collections.Counter(data)
#    print(counter)
    count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
#    print(count_pairs)
    words, _ = list(zip(*count_pairs))
    word_to_id = dict(zip(words, range(len(words))))
    id_to_word = dict((v, k) for k, v in word_to_id.items())
#    print(word_to_id)
#    print(id_to_word)
#    train = _file_to_word_ids(truth, word_to_id)
#    print(train)
    return word_to_id, id_to_word

def replaceW2ID(data, word_to_id):
    print('data', data)
#    data = readSymbolfile(path)
    return [word_to_id[word] for word in data if word in word_to_id]


def touchGT(path):
    assert(os.path.exists(path))
    root = r.parse(path).getroot()
    print(root.tag)
    #print(root.getchildren())
    tag_header_len = len(root.tag)-3
    
    for child in root:
        tag = child.tag[tag_header_len:]
        if tag == 'annotation' and child.attrib['type'] == 'truth':
            text = child.text
            print(text)
            text = text.replace('$','')
            print(text)
#            print(text.split())
#            text = text.split()
    return text

  
def makeOneshotGT(path_to_ink, path_to_symbol):
    word_to_id, id_to_word = buildVocab(path_to_symbol)
    textGT = touchGT(path_to_ink)
#    chuan hoa text de tach ra duoc tung symbol va luu thanh mang trong data
#    TODO
    data = ['\\forall', 'g', '\\in', 'G'] 
    vector = replaceW2ID(data, word_to_id)
    print('vector',vector)
    return vector

#   tach symbol             
def oneshotGT(path_to_ink, path_to_symbol):
    symbols = readSymbolfile(path_to_symbol)
    print(symbols)
    #print(symbols.split())
    text = touchGT(path_to_ink).split()
    print(text)
    truth = []
#    keyword = '[^\\\\]+(\\\\[a-zA-Z]+)+ | [^\\\\]*(\\\\[a-zA-Z]+)(\\\\[a-zA-Z]+)+'
    keyword1 = '[^\\\\]*(\\\\[a-zA-Z]+)(\\\\[a-zA-Z]+)'
    keyword2 = '[^\\\\]+(\\\\[a-zA-Z]+)+'
#    keyword = '[^i]+'
#    print(keyword)
    for word in text:
        
        if re.match(keyword1, word, re.I) or re.match(keyword2, word, re.I):
            print('tttrue')
#            print(re.match(keyword, word, re.I).group())
#            print(word)
            word = word.split('\\')
            truth.extend(word)
            wordtoid = buildVocab(path_to_symbol)
            truth = ['\\forall', 'g', '\\in', 'G']
            print(wordtoid)
            xyz = _file_to_word_ids(truth, wordtoid)
            print(xyz)
        else: 
            truth.append(word)
#            print(truth)
        
    
    
   
#touchGT('./65_alfonso.inkml')
makeOneshotGT('./7_em_59.inkml', './mathsymbolclass.txt')
#buildVocab('./mathsymbolclass.txt')