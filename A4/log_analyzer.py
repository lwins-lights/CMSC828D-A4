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
#   generate graphs
###############################################################################

def genLearningCurveData(data, outFile):
  n = len(data)
  res = []
  for i in range(1, 4):
    s = 0
    for person in data:
      s += person["data"][i]["time_elapsed_ms"]
    res.append({"x": i, "y": float(s) / n / 1000})
  with open(outFile, 'w') as f:
    json.dump(res, f)

def genAverageAdvantageData(data, outFile):
  n = len(data)
  res = []
  b = 0
  nb = 0
  for person in data:
    for i in range(3, 9):
      if person["data"][i]["blockXy"]:
        b += person["data"][i]["time_elapsed_ms"]
      else:
        nb += person["data"][i]["time_elapsed_ms"]
  res = [{"x": "Normal", "y": float(nb) / n / 3 / 1000}, {"x": "Blocked", "y": float(b) / n / 3 / 1000}]
  with open(outFile, 'w') as f:
    json.dump(res, f)

def genScatterPlotData(data, outFile):
  n = len(data)
  res = []
  for person in data:
    delta = 0
    for i in range(3, 9):
      if person["data"][i]["blockXy"]:
        delta += person["data"][i]["time_elapsed_ms"]
      else:
        delta -= person["data"][i]["time_elapsed_ms"]
    res.append({"x": person["data"][9]["user_input"], "y": float(delta) / 3 / 1000})
  with open(outFile, 'w') as f:
    json.dump(res, f)

def genAverageDelayEffectData(data, outFile):
  n = len(data)
  res = []
  for i in range(11, 16):
    d = 0
    for person in data:
      d += person["data"][i]["time_elapsed_ms"]
    res.append({"x": data[0]["data"][i]["hisDelay"], "y": float(d) / n / 1000})
  with open(outFile, 'w') as f:
    json.dump(res, f)

###############################################################################
#   main
###############################################################################

if __name__ == "__main__":
  srcName = sys.argv[1]
  srcName = genAbsPath(srcName)
  dstFolder = sys.argv[2]
  dstFolder = genAbsPath(dstFolder)
  with open(srcName, 'r') as f:
    data = json.load(f)
  genLearningCurveData(data, os.path.join(dstFolder, 'learning_curve.json'))
  genAverageAdvantageData(data, os.path.join(dstFolder, 'average_advantage.json'))
  genScatterPlotData(data, os.path.join(dstFolder, 'scatter_plot.json'))
  genAverageDelayEffectData(data, os.path.join(dstFolder, 'average_delay_effect.json'))
  '''
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
