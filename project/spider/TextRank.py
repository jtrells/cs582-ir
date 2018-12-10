import numpy as np


class TextRank:
  '''
  Calculates TextRank, the variation of PageRank using a matrix with the number of
  times two adjacent words appear in the text rather that just a binary entry.
  '''
  def __init__(self, G, it=20, damping=0.85, tolerance=None):
    self.n = G.V
    self.M = G.M
    self.it = it
    self.tolerance = tolerance
    self.alpha = damping
    self.S = np.ones((1, self.n))
    self.p = np.ones((1, self.n))
    self.p = self.p / self.n

  def initialize(self):
    # Initializes the state vector S for the ranks and normalizes graph matrix representation
    self.S = self.S / self.n
    M_row_sum = np.sum(self.M, 1).reshape(self.n, 1)
    # divide by zero safety check
    mask_zero_rows = (M_row_sum == 0).astype(int)
    M_row_sum += mask_zero_rows

    self.M_norm = self.M / M_row_sum

  def update(self):
    # Calculate new state vector and return convergence
    S = self.alpha * np.matmul(self.S, self.M_norm) + (1 - self.alpha) * self.p
    diff = np.sum(np.abs(S - self.S))
    self.S = S
    return diff

  def compute(self):
    # Compute TextRank scores, return number of iterations
    self.initialize()
    if self.tolerance is None:
      for i in range(self.it):
        self.update()
      return self.it
    else:
      num_iterations = 0
      diff = float("inf")
      while diff > self.tolerance:
        diff = self.update()
        num_iterations += 1
      return num_iterations