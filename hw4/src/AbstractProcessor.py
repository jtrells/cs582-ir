import numpy as np
from os.path import exists
from nltk.stem.porter import *
from hw4_utils import tokenize
from Graph import WordGraph

POS_TAGS = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']


class TextProcessor:
  def __init__(self, full_doc_path):
    if not exists(full_doc_path):
      raise IOError("document path do not exist")
    self.original_words = tokenize(full_doc_path)
    self.create_original_tuples()
    self.unigrams = self.get_unigrams()
    self.stemmer = PorterStemmer()
    self.get_graph()

  def create_original_tuples(self):
    self.original_tuples = []
    for word_tag in self.original_words:
      word, tag = word_tag.split('_')
      word = word.lower()
      self.original_tuples.append((word, tag))

  def filter_words(self):
    stemmer = PorterStemmer()
    filtered_words = []
    for tup in self.original_tuples:
      if tup[1] in POS_TAGS:
        filtered_words.append(stemmer.stem(tup[0]))
    return filtered_words

  def get_graph(self):
    unigrams = list(self.get_unigrams())
    m_header = {}
    for idx, unigram in enumerate(unigrams):
      m_header[unigram] = idx
    print(unigrams)

    n = len(unigrams)
    M = np.zeros((n, n))
    for idx, tup in enumerate(self.original_tuples):
      if idx < len(self.original_tuples) - 1:
        self.add_to_matrix(M, m_header, self.original_tuples, idx)

    self.word_graph = WordGraph(n)
    self.word_graph.M = M
    self.word_graph.m_header = m_header

    return self.word_graph

  def get_unigrams(self):
    unigrams = set(self.filter_words())
    # unigrams_dict = dict.fromkeys(unigrams, 0)
    return unigrams

  def add_to_matrix(self, M, m_headers, tuples, idx):
    pivot_tuple = tuples[idx]
    next_tuple = tuples[idx + 1]

    if pivot_tuple[1] in POS_TAGS and next_tuple[1] in POS_TAGS:
      m_idx_pivot = m_headers[self.stemmer.stem(pivot_tuple[0])]
      m_idx_next = m_headers[self.stemmer.stem(next_tuple[0])]
      M[m_idx_pivot][m_idx_next] += 1
      M[m_idx_next][m_idx_pivot] += 1
    return

  def get_bigrams(self):
    bigrams = set()
    for idx, tup in enumerate(self.original_tuples):
      if idx < len(self.original_tuples) - 1:
        pivot_tuple = self.original_tuples[idx]
        next_tuple = self.original_tuples[idx + 1]
        if pivot_tuple[1] in POS_TAGS and next_tuple[1] in POS_TAGS:
          bigrams.add('%s %s' % (self.stemmer.stem(pivot_tuple[0]), self.stemmer.stem(next_tuple[0])))
    return bigrams

  def get_trigrams(self):
    trigrams = set()
    for idx, tup in enumerate(self.original_tuples):
      if idx < len(self.original_tuples) - 2:
        pivot_tuple = self.original_tuples[idx]
        next_tuple = self.original_tuples[idx + 1]
        last_tuple = self.original_tuples[idx + 2]
        if pivot_tuple[1] in POS_TAGS and next_tuple[1] in POS_TAGS and last_tuple[1] in POS_TAGS:
          trigrams.add('%s %s %s' % (self.stemmer.stem(pivot_tuple[0]), self.stemmer.stem(next_tuple[0]),
                                     self.stemmer.stem(last_tuple[0])))
    return trigrams

  def get_n_grams(self, n):
    n_grams = set()
    ot = self.original_tuples
    for idx, tup in enumerate(ot):
      if idx < len(ot) - (n - 1):
        n_gram = [self.stemmer.stem(ot[idx + i][0]) for i in range(n) if ot[idx + i][1] in POS_TAGS]
        if len(n_gram) == n:
          n_grams.add(' '.join(n_gram))
    return n_grams
