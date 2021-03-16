import csv
import sys
import os

###############################################################################
#   absolute/relative path -> absolute path
###############################################################################

def genAbsPath(path):
  if os.path.isabs(path):
    return path
  else:
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.getcwd()
    return os.path.join(dir_path, path)

if __name__ == "__main__":
  srcName = sys.argv[1]
  size = int(sys.argv[2])
  print(genAbsPath(srcName))
  print(size)