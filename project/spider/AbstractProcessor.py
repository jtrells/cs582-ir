import numpy as np
from nltk.corpus import stopwords
from TextRank import TextRank
from os.path import exists
from nltk.stem.porter import *
from Graph import WordGraph
import string

POS_TAGS = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']

def tokenize(doc):
  title = doc['title'].lower()
  captions = doc['captions']
  summary = doc['summary'].lower()
  content = doc['paragraph'].lower()

  words = []
  punctuation = string.punctuation + "\"" + "\“" + "\”"
  translator = str.maketrans('', '', punctuation)
  title = title.translate(translator)
  content = content.translate(translator)
  summary = summary.translate(translator)
  words += title.split() + content.split() + summary.split()

  new_captions = []
  for caption in captions:
    new_caption = caption.lower().translate(translator)
    new_captions.append(new_caption)
    words += new_caption.split()
  return words


def remove_stopwords(l):
  words = []
  for word in l:
    if word not in stopwords.words("spanish"):
      words.append(word)
  return words

class TextProcessor:
  def __init__(self, doc):
    self.original_words = tokenize(doc)
    self.words = remove_stopwords(self.original_words)
    self.get_graph()


  def get_graph(self):
    unigrams = list(self.get_n_grams(1))
    m_header = {}
    for idx, unigram in enumerate(unigrams):
      m_header[unigram] = idx

    n = len(unigrams)
    M = np.zeros((n, n))
    for idx, tup in enumerate(self.words):
      if idx < len(self.words) - 1:
        self.add_to_matrix(M, m_header, self.words, idx)

    self.word_graph = WordGraph(n)
    self.word_graph.M = M
    self.word_graph.m_header = m_header

    return self.word_graph

  def add_to_matrix(self, M, m_headers, tuples, idx):
    pivot_tuple = tuples[idx]
    next_tuple = tuples[idx + 1]

    m_idx_pivot = m_headers[pivot_tuple]
    m_idx_next = m_headers[next_tuple]
    M[m_idx_pivot][m_idx_next] += 1
    M[m_idx_next][m_idx_pivot] += 1
    return

  def get_n_grams(self, n):
    n_grams = set()

    for idx, tup in enumerate(self.words):
      if idx < len(self.words) - (n - 1):
        n_gram = [self.words[idx + i] for i in range(n)]
        if len(n_gram) == n:
          n_grams.add(' '.join(n_gram))
    return n_grams

  def rank_n_grams(self, n):
    tr = TextRank(self.word_graph, tolerance=1e-6)
    tr.compute()

    n_grams = []
    for i in range(n):
      n_grams += list(self.get_n_grams(i + 1))
    #
    # n_grams = list(self.get_n_grams(1)) + \
    #           list(self.get_n_grams(2)) + \
    #           list(self.get_n_grams(3))
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
