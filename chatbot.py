# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 14:54:52 2019

@author: slacki
"""

#Using Python 3.5 which allows tensorflow work

#Building a Chatbot with deep NLP
import numpy as np
import tensorflow as tf
import re
import time 

### Part 1 - Data Preprocessing

#importing dataset
lines = open('movie_lines.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')
conversations = open('movie_conversations.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')

#Creating a dicitonary that maps each line and its id
id2line = {}
for line in lines:
    _line = line.split(' +++$+++ ') #_line means that this is a local variable
    id2line[_line[0]] = _line[len(_line)-1] #Take first and last string from the lines array and map to eachother
    
 #I'm not sure why he used this logic rather than the one I did above
 #   if len(_line) == 5: 
 #   id2line[_line[0]] = _line[4]
 
 #Creating a list of all of the conversations
conversations_ids = []
for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'","").replace(" ", "") #This is a weird way of just choosing the first and last element from the list 
    conversations_ids.append(_conversation.split(','))
    
# Getting the questions and answers separately
questions = []
answers = []
for conversation in conversations_ids:
    for i in range(len(conversation) - 1):
        questions.append(id2line[conversation[i]])
        answers.append(id2line[conversation[i + 1]])

#Doing a first cleaning of the texts. Consider not including . ? , 
def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"[-()\"#/@;<>{}+=~|.?,)]", "", text)
    return text

#Cleaning the questions, did differently than in the video
clean_questions = []
for question in questions:
    _cleaned1 = clean_text(question)
    clean_questions.append(_cleaned1)

#Cleaning the answers
clean_answers = []
for answer in answers:
    _cleaned2 = clean_text(answer)
    clean_answers.append(_cleaned2)
    
#Creating a dictionary that maps each word to its number of occurences
#Mind that the numbers are different than in the video. If the bot doesn't work in the end, it will be worth reviewing my code 
word2count = {}
for question in clean_questions:
    for word in question.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1
for answer in clean_answers:
    for word in answer.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1

#Creating two dictionaries that map the questions words and the answers words to a unique integer. Genius. Every word has a number
treshold = 20
questionswords2int = {}
word_number = 0
for word, count in word2count.items():  #.items() is used to do things with dictionaries innit
    if count >= treshold:
        questionswords2int[word] = word_number
        word_number += 1
answerswords2int = {}
word_number = 0
for word, count in word2count.items():  #.items() is used to do things with dictionaries innit
    if count >= treshold:
        answerswords2int[word] = word_number
        word_number += 1

#Adding the last tokens to these two dictionaries
tokens = ['<PAD>','<EOS>', '<OUT>', '<SOS>']
for token in tokens: 
    questionswords2int[token] = len(questionswords2int) + 1
for token in tokens: 
    answerswords2int[token] = len(answerswords2int) + 1

#Creating the inverse dictionary of the answers2wordsint dictionary
answerints2word = {w_i: w for w, w_i in answerswords2int.items()}

#Adding the End of String (EOS) token to the end of every answer
for i in range(len(clean_answers)):
    clean_answers[i] += ' <EOS>'

#Translating all the questions and the answers into integers
# and replacing all words that were filtered out by <OUT>
questions_to_int = []
for question in clean_questions:
    ints = []
    for word in question.split():
        if word not in questionswords2int:
            ints.append(questionswords2int['<OUT>']) #takes from the inverse dictionary
        else:
            ints.append(questionswords2int[word])
    questions_to_int.append(ints)
        
answers_to_int = []
for answer in clean_answers:
    ints = []
    for word in answer.split():
        if word not in answerswords2int:
            ints.append(answerswords2int['<OUT>']) #takes from the inverse dictionary
        else:
            ints.append(answerswords2int[word])
    answers_to_int.append(ints)

#Sorting questions and answers by the length of questions because that reduces loss or something. And makes things more efficient
sorted_cleaned_questions = []
sorted_cleaned_answers = []
for length in range(1, 25 + 1):
    for i in enumerate(questions_to_int):
        if len(i[1]) == length:
            sorted_cleaned_questions.append(questions_to_int[i[0]])
            sorted_cleaned_answers.append(answers_to_int[i[0]])

        