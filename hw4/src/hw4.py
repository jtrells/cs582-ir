import numpy as np
from os.path import join, isfile
from os import listdir
from AbstractProcessor import TextProcessor

class HW4:
  def __init__(self, folder_root_path, ignore_new_lines=True):
    self.root = folder_root_path
    self.abstracts_path = join(self.root, 'abstracts')
    self.gold_path = join(self.root, 'gold')
    self.ignore_new_lines=ignore_new_lines

  def calculate_mrrs(self, k):
    abstracts = listdir(self.abstracts_path)
    mrrs = np.zeros((0, k))
    for abstract in abstracts:
      if isfile(join(self.abstracts_path, abstract)) and abstract[0] != '.':
        try:
          tp = TextProcessor(join(self.abstracts_path, abstract), join(self.gold_path, abstract), self.ignore_new_lines)
          mrr = tp.MRR(k)
          mrrs = np.vstack((mrrs, mrr))
        except IOError as e:
          print(e)
    D = mrrs.shape[0]
    self.MRR = np.sum(mrrs, 0) / D
    print("")
    print("# abstracts: %d" % len(abstracts))
    print("# processed docs: %d" % D)
    return self.MRR