from os.path import exists
from nltk.stem.porter import *

def tokenize(doc_path):
  words = []
  with open(doc_path, 'r') as f:
    for line in f:
      for word_tag in line.split():
        words.append(word_tag)
  return words


def add_adjacent_word(dictionary, words, idx):
  POS_TAGS = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']

  key = words[idx]
  adjacent_key = words[idx + 1]
  word, tag = key.split('_')
  word = word.lower()
  adj_word, adj_tag = adjacent_key.split('_')
  adj_word = adj_word.lower()

  if tag in POS_TAGS and adj_tag in POS_TAGS:
    if word not in dictionary:
      dictionary[word] = []
    if adj_word not in dictionary[word]:
      dictionary[word].append(adj_word)

    if adj_word not in dictionary:
      dictionary[adj_word] = []
    if word not in dictionary[adj_word]:
      dictionary[adj_word].append(word)
  return


def create_word_graph(doc_path):
  if not exists(doc_path):
    return None
  original_words = tokenize(doc_path)
  adj_words = {}
  for idx, word_tag in enumerate(original_words):
    if idx < len(original_words) - 1:
      add_adjacent_word(adj_words, original_words, idx)
  return adj_words


def stem_graph(adjacent_graph):
  stemmer = PorterStemmer()
  stemmed_graph = {}
  for key in adjacent_graph:
    stem_key = stemmer.stem(key)
    if stem_key not in stemmed_graph:
      stemmed_graph[stem_key] = []
    for adj in adjacent_graph[key]:
      stem_adj = stemmer.stem(adj)
      if stem_adj not in stemmed_graph[stem_key]:
        stemmed_graph[stem_key].append(stem_adj)
  return stemmed_graph

path = "D:\\_dev\\cs582-ir\\hw4\\www\\abstracts\\183"
adjacent_words = create_word_graph(path)
stemmed_graph = stem_graph(adjacent_words)
print('end')