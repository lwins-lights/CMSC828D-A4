import csv
import configparser
try:
  import simplejson as json
except ImportError:
  import json
from flask import Flask,request,Response,render_template,send_from_directory
import psycopg2
import os, sys
import colorama
from colorama import Fore, Style
from fenwick import FenwickTree
import math

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

###############################################################################
#   visible analysis
###############################################################################

def printAnalysis(data):
  alias = data[0]["user_input"];
  print("Alias = " + alias)
  for i, row in enumerate(data):
    if i > 0:
      print(row["time_elapsed_ms"], end='ms <--| ')
      if not ("load" in row) or row["load"] == False:
        print(row["user_input"])
      else:
        if row["blockXy"]:
          b = "B"
        else:
          b = "N"
        print("[" + b + "]" + "[" + str(row["hisDelay"]) + "]" + row["user_input"])

###############################################################################
#   generate JSON
###############################################################################

def genStat(data):
  ret = {}
  ret["alias"] = data[0]["user_input"];
  #print("Alias = " + alias)
  for i, row in enumerate(data):
    if "text" in row:
      data[i]["text_hash"] = hash(row["text"])
  ret["data"] = data;
  return ret;

###############################################################################
#   main
###############################################################################

if __name__ == "__main__":
  argc = len(sys.argv);
  res = []
  for i in range(2, argc):
    srcName = genAbsPath(sys.argv[i])
    with open(srcName, 'r') as f:
      data = json.load(f)
      res.append(genStat(data))
  dstName = genAbsPath(sys.argv[1])
  with open(dstName, 'w') as f:
    json.dump(res, f)
  '''
  srcName = sys.argv[1]
  srcName = genAbsPath(srcName)
  with open(srcName, 'r') as f:
    data = json.load(f)
    printAnalysis(data)
  '''