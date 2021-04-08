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
#   print an error message
###############################################################################

def errMsg(str):
  print('[ERROR] ' + str)

###############################################################################
#   print a debug message
###############################################################################

def debugMsg(str):
  print(Fore.BLUE + "[DEBUG]", end=' ')
  print(str, end = '')
  print(Style.RESET_ALL)

###############################################################################
#   print a normal message
###############################################################################

def msg(str):
  print('[MESSAGE] ' + str)

app = Flask(__name__)

###############################################################################
#   immediately execute a postgresql query
###############################################################################

def fastExe(conn, comm):
  #debugMsg(comm)
  cur = conn.cursor()
  cur.execute(comm)
  try:
    data = cur.fetchall()
  except:
    data = [];
    pass
  conn.commit()
  cur.close()
  return data

###############################################################################
#   fetch initilization data from the PostgreSQL server
###############################################################################

def fetchInit(conn):
  countrylist = fastExe(conn, " ".join([
    "SELECT DISTINCT country,iso3c,region,income FROM nations ORDER BY country ASC"
    ]));
  return {
    "countrylist":countrylist
    }

###############################################################################
#   fetch data from the PostgreSQL server
###############################################################################

def fetchData(conn, country, xattr, yattr):
  data = fastExe(conn, " ".join([
    "SELECT", xattr + "," + yattr + ",year",
    "FROM nations WHERE country =",
    "'" + country + "'",
    "ORDER BY year ASC" 
    ]));
  xmin = fastExe(conn, " ".join([
    "SELECT", "MIN(" + xattr + ")",
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]))[0][0];
  xmax = fastExe(conn, " ".join([
    "SELECT", "MAX(" + xattr + ")",
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]))[0][0];
  ymin = fastExe(conn, " ".join([
    "SELECT", "MIN(" + yattr + ")",
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]))[0][0];
  ymax = fastExe(conn, " ".join([
    "SELECT", "MAX(" + yattr + ")",
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]))[0][0];
  yearmin = fastExe(conn, " ".join([
    "SELECT", "MIN(year)",
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]))[0][0];
  yearmax = fastExe(conn, " ".join([
    "SELECT", "MAX(year)",
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]))[0][0];
  return {
    "xygraph":data,
    "xmin":xmin,
    "xmax":xmax,
    "ymin":ymin,
    "ymax":ymax,
    "yearmin":yearmin,
    "yearmax":yearmax}

###############################################################################
#   fetchDataHistograms(): decompose the request to two single fetchings
#   fetchDataHistogram(): fetch histogram data from the PostgreSQL server
#   >>> fetchDataHistogram() is desolated!         <<<
#   >>> we use fetchDataHistogramFenwick() instead <<<
###############################################################################

def fetchDataHistograms(conn, xattr, yattr, year, bins):
  return {
    #"xdata":fetchDataHistogram(conn, xattr, year, bins),
    "xdata":fetchDataHistogramFenwick(conn, xattr, year, bins),
    #"ydata":fetchDataHistogram(conn, yattr, year, bins)
    "ydata":fetchDataHistogramFenwick(conn, yattr, year, bins)
  }
'''
def fetchDataHistogram(conn, attr, year, totalBins):
  year = str(year)
  mn = fastExe(conn, "SELECT MIN(" + attr + ") FROM nations WHERE year = " + year)[0][0]
  mx = fastExe(conn, "SELECT MAX(" + attr + ") FROM nations WHERE year = " + year)[0][0]
  mn = str(mn)
  mx = str(mx)
  totalBins = str(totalBins)
  #debugMsg(totalBins)
  step = "((" + str(mx) + "-" + str(mn) + ")/" + totalBins + ")"
  sts = "SELECT *, seq*" + step + "+" + str(mn) + " AS rangeMin, " + \
    "seq*" + step + "+" + str(mn) + "+" + step + " AS rangeMax " + \
    "FROM (SELECT CASE WHEN " + attr + "=" + str(mx) + " THEN " + str(int(totalBins) - 1) + " ELSE " + \
    "FLOOR((" + attr + "-" + str(mn) + ")/" + step + ") END AS seq, " + \
    "COUNT(*) FROM nations " + \
    "WHERE (" + attr + ">=" + mn + ") AND (" + attr + "<=" + mx + ") AND (year = " + year + \
    ") GROUP BY seq ORDER BY seq) t1"
  return {"data":fastExe(conn, sts), "mn":mn, "mx":mx, "maxcount":fastExe(conn,
    "SELECT MAX(count) FROM (" + sts + ") t2"
  )[0][0]}
'''
###############################################################################
#   server initialization
###############################################################################

def init(app, csvName):
  try:
    config = configparser.ConfigParser()
    config.read(os.path.join(app.root_path, 'config.ini'))
    conn = psycopg2.connect( \
      database=config['DEFAULT']['database'], \
      user=config['DEFAULT']['user'], \
      password=config['DEFAULT']['password'], \
      host=config['DEFAULT']['host'], \
      port=config['DEFAULT']['port'])
  except Exception as err:
    errMsg('Failed to connect to the PostgreSQL server.')
    raise err
  fastExe(conn, "DROP TABLE IF EXISTS nations;")
  fastExe(conn,
    '''
      CREATE TABLE nations (
      iso2c VARCHAR ( 15 ),
      iso3c VARCHAR ( 15 ),
      country VARCHAR ( 255 ),
      year FLOAT,
      gdp_percap FLOAT,
      life_expect FLOAT,
      population FLOAT,
      birth_rate FLOAT,
      neonat_mortal_rate FLOAT,
      region VARCHAR ( 255 ),
      income VARCHAR ( 255 ) 
    );
    ''')
  fastExe(conn,
    "COPY nations FROM '" +
    genAbsPath(csvName) +
    "' DELIMITER ',' CSV HEADER" 
  )
  return conn

###############################################################################
#   finerInit():
#   1. create indexes
#   2. build fenwick tree
#   >>> FOR THE ALGORITHM, REFER TO THE WRITEUP <<<
###############################################################################

varAttr = ['gdp_percap','life_expect', 'population','birth_rate',
  'neonat_mortal_rate']
treeSize = 5040
fenwick = {}
mnList = {}
mxList = {}

def finerInit(conn):

  msg("Pre-fetching the country list ...")
  ret = fetchInit(conn)

  # create index
  msg("Creating Indexes ...")
  size = 6
  fastExe(conn, "CREATE INDEX ON nations (country);")
  sys.stdout.write('\r')
  sys.stdout.write("[%-20s] %d%%" % ('='*int((1)*20/size), int((1)*100/size)))
  sys.stdout.flush()
  for i, attr in enumerate(varAttr):
    fastExe(conn, "CREATE INDEX ON nations (year," + attr + ");")
    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %d%%" % ('='*int((i+2)*20/size), int((i+2)*100/size)))
    sys.stdout.flush()
  sys.stdout.write('\n')

  # get statistics
  msg("Fetching statistics ...")
  temp = fastExe(conn, " ".join([
    "SELECT DISTINCT year FROM nations ORDER BY year ASC"
    ]));
  yearList = []
  for row in temp:
    yearList.append(str(int(row[0])))
  size = 5 * len(yearList)
  #debugMsg(yearList)
  for i, year in enumerate(yearList):
    for j, attr in enumerate(varAttr):
      mnList[year + attr] = str(fastExe(conn, "SELECT MIN(" + attr + ") FROM nations WHERE year = " + year)[0][0])
      mxList[year + attr] = str(fastExe(conn, "SELECT MAX(" + attr + ") FROM nations WHERE year = " + year)[0][0])
      sys.stdout.write('\r')
      sys.stdout.write("[%-20s] %d%%" % ('='*int((i*5+j+1)*20/size), int((i*5+j+1)*100/size)))
      sys.stdout.flush()
  sys.stdout.write('\n')

  # fenwick tree init
  msg("Initializing Fenwick trees ...")
  for i, year in enumerate(yearList):
    for j, attr in enumerate(varAttr):
      mn = mnList[year + attr]
      mx = mxList[year + attr]
      step = "((" + mx + "-" + mn + ")/" + str(treeSize) + ")"
      temp = fastExe(conn, " ".join([
        "SELECT CASE WHEN",
        attr + "=" + mx,
        "THEN", str(treeSize - 1), "ELSE",
        "FLOOR((" + attr + "-" + mn + ")/" + step + ") END AS seq,",
        "COUNT(*) FROM nations WHERE year =", year,
        "GROUP BY seq ORDER BY seq;"
        ]));
      vec = [0] * treeSize
      for row in temp:
        vec[min(int(row[0]), treeSize - 1)] += row[1]
      fenwick[year + attr] = FenwickTree(treeSize)
      fenwick[year + attr].init(vec)
      sys.stdout.write('\r')
      sys.stdout.write("[%-20s] %d%%" % ('='*int((i*5+j+1)*20/size), int((i*5+j+1)*100/size)))
      sys.stdout.flush()
  sys.stdout.write('\n')
  return ret

###############################################################################
#   fetch histogram data using fenwick trees
###############################################################################

def fetchDataHistogramFenwick(conn, attr, year, totalBins):
  debugMsg("Fenwick: " + str(attr) + " " + str(year) + " #Bins=" + str(totalBins))
  year = str(year)
  try:
    mn = float(mnList[year + attr])
    mx = float(mxList[year + attr])
  except:
    return {}
    pass
  totalBins = int(totalBins)
  step = (mx - mn) / totalBins
  treeStep = (mx - mn) / treeSize
  table = []
  maxcount = 0
  command = ''
  '''
  for i in range(totalBins):
    pseudoLB = mn + math.ceil(i * treeSize / totalBins) * treeStep
    pseudoUB = mn + math.floor((i + 1) * treeSize / totalBins) * treeStep
    trueLB = mn + i * step;
    trueUB = mn + (i + 1) * step;
    command = command + " ".join([
      "SELECT COUNT(*) FROM nations WHERE",
      "(year=" + year + ") AND",
      "((" + attr + ">=" + str(trueLB) + ") AND",
      "(" + attr + "<" + str(pseudoLB) + ")) OR",
      "((" + attr + ">=" + str(pseudoUB) + ") AND",
      "(" + attr + "<" + str(trueUB) + "))"
    ])
    if i + 1 < totalBins:
      command = command + " UNION\n"
  res = fastExe(conn, command)
  debugMsg(res)
  '''
  for i in range(totalBins):
    count = fenwick[year + attr].range_sum(
      int(math.floor(i * treeSize / totalBins)), int(math.ceil((i + 1) * treeSize / totalBins))
    )
    maxcount = max(count, maxcount)
    table.append([i, count, mn + i * step, mn + (i + 1) * step])
  return {"data":table, "mn":mn, "mx":mx, "maxcount":maxcount}

@app.route('/')
def renderPage():
  return render_template("index.html")

'''
  getData(): fetch data from the PostgreSQL server and return it
  ---------- INPUT = request.args.get('qtype') ----------
  .qtype == data:
    .country := country of interest
    .xattr := attribute 1
    .yattr := attribute 2
  .qtype == init:
    NONE
  .qtype == data_his:
    .xattr := attribute 1
    .yattr := attribute 2
    .year := year
    .bins := #bins
  ---------- OUTPUT ----------
  .qtype == data:
    .xygraph := data of the line graph: array of tuple [x, y, year]
  .qtype == init:
    .countrylist := array of tuple like ["China", "CHN", "Asia", "Middle Income"]
  .qtype == data_his:
    .xdata = data of the histogram
    .ydata 
'''

initData = {}

@app.route('/get-data')
def getData():
  qtype = request.args.get('qtype')
  if qtype == 'data':
    country = request.args.get('country')
    xattr = request.args.get('xattr')
    yattr = request.args.get('yattr')
    data = fetchData(conn, country, xattr, yattr)
  if qtype == 'init':
    data = initData
  if qtype == 'data_his':
    xattr = request.args.get('xattr')
    yattr = request.args.get('yattr')
    year = request.args.get('year')
    bins = request.args.get('bins')
    data = fetchDataHistograms(conn, xattr, yattr, year, bins)
  resp = Response(response=json.dumps(data),status=200, mimetype='application/json')
  h = resp.headers
  h['Access-Control-Allow-Origin'] = "*"
  return resp

@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
    'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/d3.v6.min.js')
def getD3js():
  return send_from_directory(os.path.join(app.root_path, 'static'),
    'd3.v6.min.js',mimetype='text/javascript')

@app.route('/d3-simple-slider.min.js')
def getD3Sliderjs():
  return send_from_directory(os.path.join(app.root_path, 'static'),
    'd3-simple-slider.min.js',mimetype='text/javascript')

###############################################################################
#   main
###############################################################################

if __name__ == "__main__":
  csvName = sys.argv[1]
  conn = init(app, csvName)
  msg('Initialization done.')
  initData = finerInit(conn)
  msg('Optimization initialized.')
  app.run(debug=True,use_reloader=False,port=10008)
