## How to launch

### Prerequisite
We assume that you have installed `pip3` and `postgresql` and you have ___all___ privileges to modify everything about the database. Furthermore, you have created one user (`cmsc828d` by default) and one database (`a2database` by default) for that user. 

### PostgreSQL
Give the user (`cmsc828d` by default) the ___superuser___ privilege, otherwise the server cannot automatically load the table `nations` from `data/nations.csv` when accessing the PostgreSQL server when initializing.
```
# After logging into your PostgreSQL server as admin (postgres)
ALTER USER cmsc828d WITH SUPERUSER;
```

### Installing Python packages
You need to install Python packages by the following command:
```
pip3 install flask psycopg2-binary colorama
```

### Configuration
Please double-check that the parameters for connecting to the PostgreSQL server are correct in `config.ini`. The default values are listed as follows:
```
[DEFAULT]
database = a2database
user = cmsc828d
password = 
host = 127.0.0.1
port = 5432
```

### Launch
Now, you are ready to launch the web server:
```
python3 server.py
```
Open the web page [http://127.0.0.1:10007/](http://127.0.0.1:10007/) with any browser to enjoy! You may need to use `ctrl`+`-` to zoom out the dashboard if your screen is not large enough.

## Design
The data (`data/nations.csv`) consists of important statistics of countries all over the world such as GDP per capita and birth rate for each year. Clearly, it is not helpful to directly show these raw data to users. My rule of thumb is to _put a row of the raw data into a ***context***_.

Here lists our visualization elements:
* _Select Buttons_ for the Country and two Attributes, which are in the top-left corner of the dashboard.
* _Bin Slider_, lying to the right of Select Buttons, is for controlling the number of bins shown in two histograms.
*  _Data Focused_, lying to the right of Bin Slider, will show the data point near the cursor.
* _2D Progression Graph_ at the left side of the dashboard shows the progression of attribute pairs over time.
* The meanings of _Line graphs_ and _Histograms_ are self-evident. 

### Select Buttons for the Country and two Attributes
* __Alternative 1.__ According to our visualization design, it makes no sense to visualize data of all countries at once in our 2D Progression Graph and Line Graphs, because it will make the graph too messy since there are 200+ countries. Users will be perception overloaded.
* __Alternative 2.__ We have considered to visualize data of multiple (~5) countries at once. However, we felt that one has no enough reason to compare just a few countries. Given the limited time, we decided to invest on other features. For country-wise comparison, we realized it by histograms.
* __Chosen Design.__ To help the user get more focused, we choose to visualize only two attributes of a country at once. This way the whole dashboard is cleaner and yet conveying enough information to explore.

### 2D Progression Graph
This is the main interactive element in our dashboard.  We decided to realize it at the very beginning because it would achieve ___graph sophistication___ [1]: The reader can navigate the graph to correlate two different attributes rather than simply tell a tendency of increasing or decreasing for one attribute over time.
* __Chosen Design.__ 
  * First, note that it actually visualizes ___3D___ (year and two attributes) data tuples. We adapted the visualization from [[2, 24:00]](https://www.youtube.com/watch?v=Jq2Rc0WlYTE) to successfully visualize them in 2D space.
  * If the user moves her cursor near different data points, all graphs will generate a corresponding point and the real-time data will be shown in the Data Focused element. This functionality meets our goal to _put data points into a  **context**_.
  * The graph can be zoomed by using wheels. It can be dragged as well when you have zoomed in. 
* __Alternative Design.__ 
  * Initially we have considered a 3D line graph. But it is clearly unnecessary once we knew that there is a better design: After all, a 3D graph arguably consumes more cognitive resource of the user.
  * At first we did not incorporate arrows in the graph. The result was that sometimes it is difficult to tell the flow of time: one needs to move her cursor continuously in one direction and then look at the Data Focused element or Line Graphs to tell the flow of time.
  * A possible alternative is to only put some points (scatter graph) in the 2D space. Note that this will result in a better data-ink ratio [3]. However, this encoding will nearly lose the information of the `year` attribute, which we considered unfavorable.

[1] Tufte, Edward R. "The visual display of quantitative information." Chapter 3. The Journal for Healthcare Quality (JHQ) 7.3 (1985): 15.
[2] Steve Franconeri. "Thinking with Data Visualizations, Fast and Slow." OpenVis Conf 2018.
[3] Tufte, Edward R. "The visual display of quantitative information." Chapter 6. The Journal for Healthcare Quality (JHQ) 7.3 (1985): 15.

### Line Graphs
The design tells itself. So, we directly discuss an alternative design here.
* __Alternative Design.__
  * Clearly, one possible design is to switch the x-axis and the y-axis. However, this will render the curve ___vertical___ rather than ___horizontal___. By [4] we know that humans perform better when perceiving a horizontally stretched curve. Therefore, this design was discarded.
  * Another possible modification is to use shaded area rather than a single curve to encode the data (time series). Actually, this is suggested by Tufte in [4]. However, we finally decided not to use this design because (i) a line graph has a better data-ink ratio [3] and (ii) a shaded area may suggest the user to think that higher value is better, which is clearly not the case if the attribute is, say, neonatal mortality rate.

[3] Tufte, Edward R. "The visual display of quantitative information." Chapter 6. The Journal for Healthcare Quality (JHQ) 7.3 (1985): 15.
[4] Tufte, Edward R. "The visual display of quantitative information." Chapter 9. The Journal for Healthcare Quality (JHQ) 7.3 (1985): 15.

### Histograms
The design tells itself. So, we directly discuss an alternative design here.
* __Alternative Design.__ Clearly, a possible modification is to use line graphs here to achieve a better data-ink ratio [3]. Note that we faced a similar situation when deciding whether to use line graphs in the previous Line Graphs section. So why we finally used ___shaded area___ (i.e., canonical histogram) here? The answer is that in this case, the argument (ii) in the previous section completely breaks down: using shaded area here will not trigger any confusion, because the area (or equivalently the height since the width is constant) of a bin is proportional to the frequency, which is undoubtedly an ___positively accumulating___ attribute. Furthermore, using histograms here is suggested by Tufte because it is a high contrast display [4].

[3] Tufte, Edward R. "The visual display of quantitative information." Chapter 6. The Journal for Healthcare Quality (JHQ) 7.3 (1985): 15.
[4] Tufte, Edward R. "The visual display of quantitative information." Chapter 9. The Journal for Healthcare Quality (JHQ) 7.3 (1985): 15.

## Overview of the Development Process
We develop the system mainly in an incremental manner.
| Accumulated Elapsed Time | Time Used | Progress |
| --- | --- | --- |
| 3h | 3h | We realized a prototype of the system, which only includes a non-interactive 2D Progression Graph displaying a curve rather than arrows. |
| 6.75h | 3.75h | The 2D Progression Graph was zoomable. Select Buttons are added.|
| 8.55h | 1.8h | The Data Focused element and the focus system (refer to section __2D Progression Graph/Chosen Design__) were added. |
| 10.95h | 2.4h | We obtained the current system except that histograms are missing and the layout was messier. |
| 14.7h | 3.75h | All codes done. |
| 15.1h | 0.4h | We let the server output colored PostgreSQL commands for graders' convenience. We also automated the process of initial PostgreSQL data loading from `data/nations.csv`.|
| 17.1h | 2h | We tested our system in a new virtual machine. |
| 19.2h | 2.1h | We finished this document you are reading. ;-) |


## Acknowledgment
* The data is downloaded from a course [homepage](https://paldhous.github.io/ucb/2016/dataviz/datasets.html) of Peter Aldhous. It is accredited to [World Bank Indicators](https://data.worldbank.org/indicator/all) portal.
* I learnt advanced usage of D3.js [here](https://observablehq.com/@d3/gallery). However I did ___not___ adapt any specific design. All I needed is to comprehend grammars and APIs.
