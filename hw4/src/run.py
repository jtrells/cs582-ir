import sys
from hw4 import HW4

def main(argv):
  num_params = len(argv)
  if num_params < 2:
    print('Required parameters:\n1) Path to WWW collection root folder\n2) Ignore new lines [0: False, 1: True]')
    return
  ROOT = str(argv[0])
  print(ROOT)
  IGNORE = True if int(argv[1]) == 1 else False
  hw4 = HW4(ROOT, IGNORE)
  MRR = hw4.calculate_mrrs(10)

  print("")
  print("MRR for k=1 to k=10")
  for k in range(0, 10):
    print("%d  %f" % (k+1, MRR[k]))

if __name__ == "__main__":
  main(sys.argv[1:])