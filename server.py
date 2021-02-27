import csv
import configparser
try:
    import simplejson as json
except ImportError:
    import json
from flask import Flask,request,Response,render_template,send_from_directory
import psycopg2
import os

'''
  errMsg(): Print an error message
'''
def errMsg(str):
  print('[ERROR] ' + str)

'''
  debugMsg(): Print a debug message
'''
def debugMsg(str):
  print('[DEBUG]', end=' ')
  print(str)

'''
  msg(): Print a normal message
'''
def msg(str):
  print('[MESSAGE] ' + str)

app = Flask(__name__)

'''
  fastExe(): Immediately execute an PostgreSQL query
'''
def fastExe(conn, comm):
  cur = conn.cursor()
  cur.execute(comm)
  data = cur.fetchall()
  conn.commit()
  cur.close()
  return data

'''
  fetchData(): Fetch data from the PostgreSQL server
'''
def fetchData(conn, country, xattr, yattr):
  data = fastExe(conn, " ".join([
    "SELECT", xattr + "," + yattr,
    "FROM nations WHERE country =",
    "'" + country + "'"
    ]));
  return {"xygraph":data}

'''
  init(): Initialization of the server
'''
def init(app):
  try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = psycopg2.connect( \
      database=config['DEFAULT']['database'], \
      user=config['DEFAULT']['user'], \
      password=config['DEFAULT']['password'], \
      host=config['DEFAULT']['host'], \
      port=config['DEFAULT']['port'])
  except Exception as err:
    errMsg('Failed to connect to the PostgreSQL server.')
    raise err
  return conn

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
  ---------- OUTPUT ----------
  .qtype == data:
    .xygraph := data of the line graph for attribute 1 & 2
'''
@app.route('/get-data')
def getData():
  qtype = request.args.get('qtype')
  if qtype == 'data':
    country = request.args.get('country')
    xattr = request.args.get('xattr')
    yattr = request.args.get('yattr')
    data = fetchData(conn, country, xattr, yattr)
  resp = Response(response=json.dumps(data),status=200, mimetype='application/json')
  h = resp.headers
  h['Access-Control-Allow-Origin'] = "*"
  return resp

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
      'favicon.ico',mimetype='image/vnd.microsoft.icon')

'''
  Main part
'''

if __name__ == "__main__":
  conn = init(app)
  msg('Initialization done.')
  app.run(debug=True,port=10007)