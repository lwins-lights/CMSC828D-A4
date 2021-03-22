
## How to launch

### Cautions
Please do ___not___ use the original A2 submitted previously because
* it does not support a user-specified CSV, and
* the new version of A2 outputs useful information in Chrome console (see below).

Instead, please follow this guide to test both A2 and A3.
_We are aware of a performance issue about the lag when switching to a new country by clicking the selection button. However, this problem is irrelevant to us: it is a defect of the browser, which should have been able to handle a list of 10,000 terms._

### Prerequisite
We assume that you have installed `pip3` and `postgresql` and you have ___all___ privileges to modify everything about databases. Furthermore, you have created one user (`cmsc828d` by default) and ___two___ databases (`a2database` and `a3database` by default) for that user. 

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
Please double-check that the parameters for connecting to the PostgreSQL server are correct in `A3/config.ini`. The default values are listed as follows:
```
[DEFAULT]
database = a3database
user = cmsc828d
password = 
host = 127.0.0.1
port = 5432
```
Similarly, check `A2/config.ini`:
```
[DEFAULT]
database = a2database
user = cmsc828d
password = 
host = 127.0.0.1
port = 5432
```

### Launch the Dataset Randomizer
Now, you are ready to launch the dataset randomizer:
```
# usage: python3 A3/randomizer.py [source] [destination] [number_of_countries] [noise_level]
# the generated CSV will have ~ (20 * number_of_countries) rows
# suggested parameters: 
#   10000 <= number_of_countries <= 100000
#   0.25 <= noise_level <= 4
python3 A3/randomizer.py data/nations.csv rand.csv 50000 1
```
Usually it takes a few minutes to generate the dataset.

### Launch A2 and A3
To launch the A2/A3 server, enter the following:
```
# usage: python3 A2/server.py [dataset]
python3 A2/server.py rand.csv
# usage: python3 A3/server.py [dataset]
python3 A3/server.py rand.csv
```
Please wait until it is outputted that 
```
 * Running on http://127.0.0.1:1000X/ (Press CTRL+C to quit)
```
for both A2 and A3.

Now, open the web page [http://127.0.0.1:10007/](http://127.0.0.1:10007/) (for A2) and [http://127.0.0.1:10008/](http://127.0.0.1:10008/) (for A3) with any browser to enjoy! You may need to use `ctrl`+`-` to zoom out the dashboard if your screen is not large enough.

#### Observing system response time. 
For your convenience, both A2 and A3 clients will print the real-time system response time to the browser developer console. If you are using Chrome, press `ctrl`+`shift`+`I` to open the console. ___However___, we do ___not___ recommend you to open the console in the very beginning because it will dramatically reduce the performance. Instead, open the console to read the log ___after___ you have done the interaction.

## Design
### Recap of A2
The data (`data/nations.csv`) consists of important statistics of countries all over the world such as GDP per capita and birth rate for each year. Clearly, it is not helpful to directly show these raw data to users. My rule of thumb is to _put a row of the raw data into a ***context***_.

Here lists our visualization elements:
* _Select Buttons_ for the Country and two Attributes, which are in the top-left corner of the dashboard.
* _Bin Slider_, lying to the right of Select Buttons, is for controlling the number of bins shown in two histograms.
*  _Data Focused_, lying to the right of Bin Slider, will show the data point near the cursor.
* _2D Progression Graph_ at the left side of the dashboard shows the progression of attribute pairs over time.
* The meanings of _Line graphs_ and _Histograms_ are self-evident. 

### Algorithm of Dataset Randomizer
The randomizer generates data of fake countries according to data of real countries. It works as follows:
1. Repeat the following process `number_of_countries` (inputted by the user) times.
2. Randomly select a country from the seed CSV. Generate a fake country by copying all relevant rows.
3. Compute the covariance matrix for ___quantitative___ columns (`gdp_percap`, `life_expect`, `population`, `birth_rate`, `neonat_mortal_rate`), where we regard each row (over different `year`) as a sample of this length-5 vector.
4. Add Gaussian noise, whose covariance matrix is set as what we just computed, to corresponding columns for the fake country. The noise is further scaled by `noise_level` (inputted by the user) and the range of `year`.

This way, we have generated some realistic fake countries because they are generated based on (data of) real countries and the covariance between different attributes are preserved.

### Optimization 1: Fenwick Trees (Structural)
#### Chosen design.
When the dataset is large, the performance bottleneck is at fetching the histogram data from the PostgreSQL server. In a high level, the server is busy computing queries of the following form:
```
SELECT COUNT(*) WHERE (x >= [lower_bound]) AND (x < [upper_bound])
```
This type of query can be actually perfectly handled by column-oriented DBMS (in this case, the column of interest is `x`). Alas, PostgreSQL is not column-oriented. Therefore, we realized the data structure for ranged queries, ___Fenwick tree___ [1], whose online query complexity is only O(log N), in `A3/server.py`. To avoid loading all data at once when initializing Fenwick trees, we adopted the idea of ___offline approximate query processing___ from [2]: to be specific, we divide the whole range of `x` into thousands of blocks, and a Fenwick tree only remembers the result of `COUNT(*)` in each block in the initialization phase.

[1] Fenwick, Peter M. "A new data structure for cumulative frequency tables." Software: Practice and experience 24.3 (1994): 327-336.

[2] Chaudhuri, S., Ding, B. and Kandula, S., 2017, May. Approximate query processing: No silver bullet. In Proceedings of the 2017 ACM International Conference on Management of Data (pp. 511-519).

#### Alternative design 1: Exact query
Note that our design only gives approximate results: for example, suppose a Fenwick tree is initialized with data `COUNT(*) WHERE (x >= t) AND (x < t + 1)`, for integer `t`. If we want to count ___exactly___ over range `10.5 <= x < 99.9`, we need to add up results of following queries:
```
SELECT COUNT(*) WHERE (x >= 11) AND (x < 99)
SELECT COUNT(*) WHERE (x >= 10.5) AND (x < 11)
SELECT COUNT(*) WHERE (x >= 99) AND (x < 99.9)
```
Note that the first query can be answered by the Fenwick tree, whereas the remaining two should be directed to the PostgreSQL server.

After some tests we chose to discard this idea of exact query. The reason is twofold:
1. It reduces the performance considerably even with the help of indexes, though it is still far better than without Fenwick trees.
2. The difference between exact query and approximate query, when visualized, is almost negligible to human perception.

#### Alternative design 2: Materialized view
It is possible to utilize PostgreSQL built-in materialized view to improve the performance. For example, if we create materialized views `SELECT COUNT(*) WHERE (x >= t * width) and (x < (t + 1) * width)` for integer `t` and an appropriate `width`, then it is faster to compute an arbitrary 
```
SELECT COUNT(*) WHERE (x >= [lower_bound]) AND (x < [upper_bound])
```
However, even with a carefully chosen `width`, this algorithm still has complexity O(N^0.5) [3], which is incomparable with O(log N) for Fenwick trees.

[3] [Sqrt Decomposition.](https://cp-algorithms.com/data_structures/sqrt_decomposition.html)

### Optimization 2: PostgreSQL Indexes (Structural)
#### Chosen design.
 Recall that `country` and `year` are columns of our data. We created ___B+ tree___ indexes on `(country)` and `(year, X)` for each `X` being quantitative columns. We base this decision on that, according to [4], an index is favorable if
> The existence of an index on an attribute may speed up greatly the execution of those queries in which a value, or range of values, is specified for that attribute, and may speed up joins involving that attribute as well.

Note that the `(country)` index clearly speeds up preparing the data for _2D Progression Graph_ because it shows the dynamic of a single country. On the other hand, `(year,X)` indexes will speed up preparing the data for _Histograms_ for a similar reason.
#### Alternative design: other indexes
We have argued why we built indexes on specific attributes (attribute lists). Another possibility is to use other types of indexes such as ___Hash table___. We consider this alternative uncompetitive because of two reasons:
1. According to [5], B+ trees are capable of speeding up ranged queries (e.g., `WHERE (x > 10) AND (x < 20)`) while Hash tables are not. Our design frequently makes ranged queries.
2. Even for queries like `WHERE (x == 10)`, B+ trees will not degrade much compared to Hash tables [6].

[4] Database Systems: the Complete Handbook, Section 8.4, by Hector Garcia-Molina, Jennifer Widom, and Jeffrey Ullman.

[5] Database Systems: the Complete Handbook, Section 14.2 and 14.3, by Hector Garcia-Molina, Jennifer Widom, and Jeffrey Ullman.

[6] [PostgreSQL Indexes: Hash Indexes are Faster than Btree Indexes?](https://www.enterprisedb.com/blog/postgresql-indexes-hash-indexes-are-faster-btree-indexes)

### Optimization 3: Speculative Query (Algorithmic)
#### Chosen design.
We implement our speculative query algorithm, inspired by the following quote in [7]:
> This is consistent with prior research that suggest that selective attention does not change drastically over time [KU87].

To be specific, if the currently shown _Histogram_ is generated by parameters `(year, attribute, number_of_bins)`, the client will try to fetch data for `(year + i, attribute, number_of_bins)` where `i` is in a small range, _whenever the client is ***idle***_.

#### Alternative design: Advanced speculation model
We could have implemented a more advanced speculation model like the one in [7]. However, given the simplicity of our dashboard, we considered this unnecessary. To be specific,
1. The current algorithm already has a high success probability in our test, where a success is defined by the event that the required data has been fetched when the user triggers the client to show the corresponding visualization.
2. We have limited time allocated for this assignment.

[7] Ottley, A., Garnett, R. and Wan, R., 2019, June. Follow The Clicks: Learning and Anticipating Mouse Interactions During Exploratory Data Analysis. In Computer Graphics Forum (Vol. 38, No. 3, pp. 41-52).

### Optimization 4: Client-Side Caching (Architectural)
#### Chosen design.
We simply memorize previous query results for _Histograms_.
#### Alternative design 1: Hash.
Initially, we considered using Hash tables to memorize, say, only 1,000 most recent query results so that the specified memory limit (1GB) is not exceeded. However, after a careful calculation of memory usage, we did not actually need this.
#### Alternative design 2: Caching other data.
We chose not to cache other graphs because (1) they are not responsible for the performance bottleneck and (2) the memory limit will be exceeded. Of course we can bring out Hash tables from the trash again, but there is no enough reason to do so.

## Overview of the Development Process
We develop the system mainly in an incremental manner.
| Accumulated Elapsed Time | Time Used | Progress |
| --- | --- | --- |
| 3.6h | 3.6h | We did not write any code. Instead, we carefully read all relevant materials and came up with a mature plan in mind. |
| 4.8h | 1.2h | We slightly upgraded A2 for better evaluation, where the performance is unchanged. We also initialized A3 codes.|
| 7.05h | 2.25h | We implemented `A3/randomizer.py` |
| 7.55h | 0.5h | We added Optimization 2 (PostgreSQL indexes). |
| 10.35h | 2.8h | We added Optimization 1 (Fenwick trees). |
| 11.35h | 1h | We further realized exact ranged queries using Fenwick trees. However, we finally decided to revert to approximate queries. |
| 12.35h | 1h | We added Optimization 4 (Client-side caching). |
| 12.95h | 0.6h | We added Optimization 3 (Speculative query). |
| 14.1h | 1.15h | We tested our system in a new virtual machine. |
| 16.85h | 2.75h | We finished this document you are reading. ;-) |

Clearly, the part that took the most time is to have the whole idea in mind. Once that was done, the coding process went smoothly.

## Acknowledgment
* The data is downloaded from a course [homepage](https://paldhous.github.io/ucb/2016/dataviz/datasets.html) of Peter Aldhous. It is accredited to [World Bank Indicators](https://data.worldbank.org/indicator/all) portal.
* I learnt advanced usage of D3.js [here](https://observablehq.com/@d3/gallery). However I did ___not___ adapt any specific design. All I needed was to comprehend grammars and APIs.

