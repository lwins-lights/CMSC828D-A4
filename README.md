## Manual

### Cautions
You will __not__ find any explanation of the A3 in this document. This is normal because we want to know your learning curve.

### Prerequisite
We assume that you have installed `pip3` and `postgresql` and you have ___all___ privileges to modify everything about databases. Furthermore, you have created one user (`cmsc828d` by default) and a database (`a3database` by default) for that user. 

### PostgreSQL
Give the user (`cmsc828d` by default) the ___superuser___ privilege, otherwise the server cannot automatically load the table from the CSV file when accessing the PostgreSQL server when initializing.
```
# After logging into your PostgreSQL server as admin (postgres)
ALTER USER cmsc828d WITH SUPERUSER;
```

### Installing Python packages
You need to install Python packages by the following command:
```
pip3 install flask psycopg2-binary colorama fenwick numpy
```
Note: If you have trouble installing `numpy` because of compatibility issues, refer to [https://docs.scipy.org/doc/scipy/reference/toolchain.html](https://docs.scipy.org/doc/scipy/reference/toolchain.html) to check which version is suitable for your `python3` and then manually install that version using `pip3`. For example:
```
pip3 install 'numpy==1.18'
```

### Configuration
Please double-check that the parameters for connecting to the PostgreSQL server are correct in `A4/config.ini`. The default values are listed as follows:
```
[DEFAULT]
database = a3database
user = cmsc828d
password = 
host = 127.0.0.1
port = 5432
```

### Launch A3
To start the experiment:
```
python3 A4/server.py data/nations.csv
```
Please wait until it is outputted that 
```
 * Running on http://127.0.0.1:10009/ (Press CTRL+C to quit)
```

Now, open the web page [http://127.0.0.1:10009/](http://127.0.0.1:10009/) with any browser to enjoy! You may need to use `ctrl`+`-` to zoom out the dashboard if your screen is not large enough.

### Return the result
Your browser should automatically download a `log.txt` file when you finish. Please send it to `yfzheng@umd.edu`.

