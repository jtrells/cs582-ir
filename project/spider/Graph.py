import numpy as np


class WordGraph:
  def __init__(self, n):
    self.V = n
    self.M = np.zeros((n, n))
    self.m_header = {}