import numpy as np
from TextRank import TextRank
from os.path import exists
from nltk.stem.porter import *
from hw4_utils import tokenize, tokenize_sentences
from Graph import WordGraph

POS_TAGS = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']


class TextProcessor:
  def __init__(self, full_doc_path, full_doc_path_gold, ignore_new_lines=True):
    if not exists(full_doc_path):
      raise IOError("There is no document %s" % full_doc_path)
    if not exists(full_doc_path_gold):
      raise IOError("There is not gold standard for %s" % full_doc_path)

    self.original_words = tokenize(full_doc_path)
    self.sentences = tokenize_sentences(full_doc_path)
    self.gold_path = full_doc_path_gold
    self.create_original_tuples()
    self.create_tuples_sentences()
    self.stemmer = PorterStemmer()
    self.get_graph(ignore_new_lines)

  def create_original_tuples(self):
    self.original_tuples = []
    for word_tag in self.original_words:
      word, tag = word_tag.split('_')
      word = word.lower()
      self.original_tuples.append((word, tag))

  def create_tuples_sentences(self):
    self.tuples_sentences = []
    for sentence in self.sentences:
      tuples = []
      for word_tag in sentence:
        word, tag = word_tag.split('_')
        word = word.lower()
        tuples.append((word, tag))
      self.tuples_sentences.append(tuples)

  def get_graph(self, ignore_new_lines=True):
    unigrams = list(self.get_n_grams(1, ignore_new_lines))
    sentences = [self.original_tuples] if ignore_new_lines else self.tuples_sentences
    m_header = {}
    for idx, unigram in enumerate(unigrams):
      m_header[unigram] = idx

    n = len(unigrams)
    M = np.zeros((n, n))
    for ts in sentences:
      for idx, tup in enumerate(ts):
        if idx < len(ts) - 1:
          self.add_to_matrix(M, m_header, ts, idx)

    self.word_graph = WordGraph(n)
    self.word_graph.M = M
    self.word_graph.m_header = m_header

    return self.word_graph

  def add_to_matrix(self, M, m_headers, tuples, idx):
    pivot_tuple = tuples[idx]
    next_tuple = tuples[idx + 1]

    if pivot_tuple[1] in POS_TAGS and next_tuple[1] in POS_TAGS:
      m_idx_pivot = m_headers[self.stemmer.stem(pivot_tuple[0])]
      m_idx_next = m_headers[self.stemmer.stem(next_tuple[0])]
      M[m_idx_pivot][m_idx_next] += 1
      M[m_idx_next][m_idx_pivot] += 1
    return

  def get_n_grams(self, n, ignore_new_lines=True):
    n_grams = set()
    sentences = [self.original_tuples] if ignore_new_lines else self.tuples_sentences

    for ts in sentences:
      for idx, tup in enumerate(ts):
        if idx < len(ts) - (n - 1):
          n_gram = [self.stemmer.stem(ts[idx + i][0]) for i in range(n) if ts[idx + i][1] in POS_TAGS]
          if len(n_gram) == n:
            n_grams.add(' '.join(n_gram))
    return n_grams

  def rank_n_grams(self, ignore_new_lines=True):
    tr = TextRank(self.word_graph, tolerance=1e-6)
    tr.compute()

    n_grams = list(self.get_n_grams(1, ignore_new_lines)) + \
              list(self.get_n_grams(2, ignore_new_lines)) + \
              list(self.get_n_grams(3, ignore_new_lines))
    scores = [0 for i in range(len(n_grams))]

    for idx, score in enumerate(scores):
      words = n_grams[idx].split(" ")
      for word in words:
        score += tr.S[0][self.word_graph.m_header[word]]
      scores[idx] = score
    sorted_idx = (-np.array(scores)).argsort()
    return n_grams, scores, sorted_idx

  def process_gold_tokens(self):
    keyphrases = []
    with open(self.gold_path, 'r') as f:
      for line in f:
        token = []
        for word in line.split():
          token.append(self.stemmer.stem(word))
        keyphrases.append(' '.join(token))
    return keyphrases

  def MRR(self, k):
    n_grams, scores, sorted_idx = self.rank_n_grams()
    gold_keyphrases = self.process_gold_tokens()
    mrr_scores = np.zeros((1, k))

    k_ = min(k, len(n_grams))
    for i in range(k_):
      n_gram = n_grams[sorted_idx[i]]
      if i > 0 and mrr_scores[0][i-1] > 0:
        mrr_scores[0][i] = mrr_scores[0][i-1]
      else:
        for keyphrase in gold_keyphrases:
          if n_gram == keyphrase:
            mrr_scores[0][i] = 1/(i + 1)
            break
    # if len(n_grams) < k, fill with previous values
    for i in range(k_ + 1, k):
      mrr_scores[0][i] = mrr_scores[0][i-1]

    return mrr_scores
