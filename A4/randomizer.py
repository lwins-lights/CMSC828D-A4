import csv
import sys
import os
import numpy
import random

attrList = ['iso2c','iso3c','country','year','gdp_percap','life_expect',
  'population','birth_rate','neonat_mortal_rate','region','income']

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
#   regData():
#   1. filter out illegal countries
#   2. cluster data by countries
###############################################################################

regThr = 10 # minimal number of rows for a country being legal

def legalRow(row):
  for i in attrList:
    if row[i] == '':
      return False
  return True

def regData(data):
  myList = [[]]
  n = 0
  curCountry = data[0]['country']
  for i, row in enumerate(data):
    if legalRow(row):
      if row['country'] == curCountry:
        myList[n].append(row)
      else:
        n += 1
        myList.append([row])
        curCountry = row['country']
  ret = []
  for i in myList:
    if len(i) >= regThr:
      ret.append(i)
  return ret

###############################################################################
#   genCov(): generate covariance matrices for each real country
#   genData(): generate rows by mimicking data of real countries
#   >>> FOR THE ALGORITHM, REFER TO THE WRITEUP <<<
###############################################################################

varAttr = ['gdp_percap','life_expect', 'population','birth_rate',
  'neonat_mortal_rate']
fixedAttr = ['iso2c','iso3c','country','year','region','income']
zeroes = [0, 0, 0, 0, 0]
noiseMultiplier = 0

def genCov(data):
  ret = []
  for country in data:
    obsList = []
    for row in country:
      obs = []
      for attr in varAttr:
        obs.append(float(row[attr]))
      obsList.append(obs)
    ret.append(numpy.cov(obsList, rowvar=False))
    #print(country[0]['country'])
    #print(numpy.cov(obsList, rowvar=False), end='\n\n')
  return ret

def genData(data, size):
  # init
  for i, country in enumerate(data):
    for j, row in enumerate(country):
      for attr in varAttr:
        data[i][j][attr] = float(data[i][j][attr])
  # main
  ret = []
  cov = genCov(data)
  for i in range(size):
    # calculation
    gened = []
    country = random.randrange(len(data))
    for row in data[country]:
      genedRow = {}
      #print(cov[country])
      rv = numpy.random.multivariate_normal(zeroes, cov[country])
      for j, attr in enumerate(varAttr):
        genedRow[attr] = row[attr] + rv[j] * noiseMultiplier / len(data[country])
        if genedRow[attr] < 0:
          genedRow[attr] = row[attr]
      for attr in fixedAttr:
        genedRow[attr] = row[attr]
      genedRow['country'] = genedRow['country'] + '#' + str(i)
      gened.append(genedRow)
    ret.append(gened)
    # showing bar
    if int((i+1)*100/size) != int(i*100/size):
      sys.stdout.write('\r')
      sys.stdout.write("[%-20s] %d%%" % ('='*int((i+1)*20/size), int((i+1)*100/size)))
      sys.stdout.flush()
  sys.stdout.write('\nWriting into the CSV file ...\n')
  return ret

###############################################################################
#   write to a csv
###############################################################################

def writeCsv(data, csvName):
  with open(csvName, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=attrList)
    for country in data:
      for row in country:
        writer.writerow(row)

###############################################################################
#   main
###############################################################################

srcData = []

if __name__ == "__main__":
  srcName = sys.argv[1]
  dstName = sys.argv[2]
  size = int(sys.argv[3])
  noiseMultiplier = float(sys.argv[4])
  srcName = genAbsPath(srcName)
  #print(genAbsPath(srcName))
  #print(size)
  with open(srcName, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      srcData.append(row)
    #print(srcData[0])
  srcData = regData(srcData)
  #writeCsv(srcData, dstName)
  writeCsv(genData(srcData, size), dstName)
