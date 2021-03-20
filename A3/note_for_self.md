## Create Index
```
CREATE INDEX ON nations (country);
```

## Create database
```
CREATE DATABASE a2database
```

## Connect to database
```
psql -U postgres
psql -U cmsc828d -w a2database
```

## Give superuser privilege
```
ALTER USER cmsc828d WITH SUPERUSER;
```

## Initialize
```
DROP TABLE IF EXISTS nations;

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

COPY nations
FROM '/home/yuwan/Documents/Courses/2021 Spring/CMSC828D/CMSC828D-A2/data/nations.csv' 
DELIMITER ',' 
CSV HEADER;
```

## Old code: server.py
```
'''
fetchAttributes(): Obtain the list of attributes
'''
def fetchAttributes(conn):
  data = fastExe(conn, "SELECT column_name FROM information_schema.columns WHERE table_name = 'movies'")
  attr = []
  for x in data:
    attr.append(x[0])
  num = fastExe(conn, "SELECT COUNT(*) FROM movies")[0][0]
  return {"attr":attr,"num":num}

'''
fetchData(): Obtain aggregated data for a set of visualization parameters from the client
'''
def fetchData(conn, attr, totalBins, rangeLo, rangeHi):
  mn = fastExe(conn, "SELECT MIN(" + attr + ") FROM movies")[0][0]
  mx = fastExe(conn, "SELECT MAX(" + attr + ") FROM movies")[0][0]
  rangeLo = str(rangeLo)
  rangeHi = str(rangeHi)
  if rangeLo == 'default':
    rangeLo = str(mn)
    rangeHi = str(mx)
  totalBins = str(totalBins)
  step = "((" + str(mx) + "-" + str(mn) + ")/" + totalBins + ")"
  return [fastExe(conn, "SELECT *, seq*" + step + "+" + str(mn) + " AS rangeMin, " + \
    "seq*" + step + "+" + str(mn) + "+" + step + " AS rangeMax " + \
    "FROM (SELECT CASE WHEN " + attr + "=" + str(mx) + " THEN " + str(int(totalBins) - 1) + " ELSE " + \
    "FLOOR((" + attr + "-" + str(mn) + ")/" + step + ") END AS seq, " + \
    "COUNT(*) FROM movies " + \
    "WHERE (" + attr + ">=" + rangeLo + ") AND (" + attr + "<=" + rangeHi + ") GROUP BY seq ORDER BY seq) t1;"), mn, mx]

@app.route('/get-data')
def getData():
  qType = request.args.get('qtype')
  if qType == 'init':
    data = fetchAttributes(conn)
  elif qType == 'data':
    attr = request.args.get('attr')
    totalBins = request.args.get('totalbins')
    rangeLo = request.args.get('rangelo')
    rangeHi = request.args.get('rangehi')
    data = fetchData(conn, attr, totalBins, rangeLo, rangeHi)
  else:
    debugMsg("I am directly accessing the raw file.")
    data = []
    filename = request.args.get('filename')
    with open(filename, 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        data.append(row)
  resp = Response(response=json.dumps(data),status=200, mimetype='application/json')
  h = resp.headers
  h['Access-Control-Allow-Origin'] = "*"
  return resp
```