# CloudbrainAnalysis
Modular analysis of cloudbrain data streams, with visualization component

This application depends upon the cloudbrain library being importable by Python.

This a very early rough draft. Here's what we have so far:

## Prerequisites

1. cloudbrain https://github.com/marionleborgne/cloudbrain
2. tornado http://www.tornadoweb.org

## Installation
Install using normal procedure
```
python setup.py install
```

## Quickstart
* make sure you have a device connector streaming live data
(mock connector example given)
```
  python {cloudbrain path}/cloudbrain/publishers/sensor_publisher.py --mock -n openbci -i octopicorn -c localhost -p 99
```
* Start both Analysis and Visualization by a single convenience script at root dir called "run.py" (should be started
with the same device id, name, rabbitmq params as above)
```
  python {CloudbrainAnalysis path}/run.py -i octopicorn -c localhost -n openbci
```
* Point your web browser to http://localhost:9999/index.html - Currently the eeg/flot is the only demo working
* Ctrl-C to stop analysis process & viz server
* Edit analysis processing chain and parameters by modifying AnalysisModules/conf.yml You can try commenting out
module blocks to turn them on or off. Set debug to True to see live output from command line.

## Analysis Modules Overview
In the folder "AnalysisModules", find the conf.yml.  This file is used to set a processing chain of analysis modules,
defining the order, names of input and output metrics, and any special params used by each module.

For now, the only modules defined are "Windows", "Downsample" and "Test".  It is up to the user to make sure that,
if one module follows another, that module 1 output is compatible with module 2 input.  For example, if a module is
expecting scalar input, don't put a module that emits matrices in front of it.

Some limitations to be aware of:
- only works with openbci device type for now
- only 1 input and 1 output per module for now. input is required, output is optional.
- the config vars 'input_feature' and 'output_feature' define metric names to read/write on rabbitmq
- only rabbitmq is supported, not pipes
- there are some random things hardcoded

## Analysis Modules Demo
* start streaming data using cloudbrain with a mock openbci (assumes you're running rabbitmq locally)
```
python {cloudbrain path}/cloudbrain/publishers/sensor_publisher.py --mock -n openbci -i octopicorn -c localhost -p 99
```
* start the analysis modules script in a separate terminal window, using same device id and rabbitmq host
```
python {CloudbrainAnalysis path}/AnalysisModules/AnalysisService.py -i octopicorn -c localhost -n openbci
```
If debug is on for a given module, it should output to command line.


## Visualizations Overview
This is very rough.  Under the folder "Viz", there are demos, intended to show a chart visualization per metric/module, per library.
For example, starting with raw eeg, there will be an example using libraries flot, chart.js v1.0, chart.js v2.0,
rickshaw, and other libraries.

The intent here is to provide for many different impementations to be demoed so we can compare performance and
feasibility of different chart libraries for a specific type of visualization.

For example, in general, we prefer chart libraries that support WebGL.  However, the main library we've tried that
supports this, chart.js, only offers 5 types of chart.  So, it makes sense to branch out and use different libraries for
different visualizations, rather than try and find one lib that works well for everything.

The visualizations run using a tornado server copying the pattern used in cloudbrain's rt_server and frontend.
The server was modified to use the "multiplex" capability, so that we are not limited to one connection per window. This
was modelled after a sockjs example found here:
https://github.com/mrjoes/sockjs-tornado/tree/master/examples/multiplex
That is why there is reference to "ann" and "bob".  The server is defined in server.py.

The tornado server just passes through all get requests to their relative location based on the "www" folder as root.
That is why all the visualization code is presently stuffed into the folder "Multiplex".

If you establish an "ann" type connection, it will use a PlotConnection, which is just a proxy for the connection
defined in connection_subscriber.py. This is meant for output from cloudbrain to a javascript visualization via websocket.

If you establish a "bob" type connection, it will use a ClassLabelConnection, which, as the type name suggests, is
meant for the javascript frontend to actually send data back to cludbrain via websocket.  This is not yet implemented.
The idea here is that the frontend visualization will require the capability to show some UI to the user meant for
training (or calibration) sessions, in which capturing class label tag is critical.

The current limitations are so many it's not wort listing out.  Only basic eeg and downsampled eeg ("eegd") has been
worked on.  Only the flot example works, though the chartjs examples should be close.

## Visualizations Demo
1. assuming you're running a mock connector as specified in step 1 above, you can start your server by
```
python {CloudbrainAnalysis path}/Viz/VisualizationServer.py
```

2. open your browser and visit the path you want, relative to the www folder, like this
http://localhost:9999/index.html
(only working demo for now is the flot eeg)

3. the "eeg" metric should work if you have mock connector streaming.  if you also have analysis modules running, with
the downsample module output, then the "eegd" metric should work as well.  The basic idea is that you pick the metric you
want to see and click "connect" to start streaming it.  The actual websocket connection is opened when the page loads.


## Run Analysis and Visualization in One Call
Sometimes, you might prefer to start/stop the AnalysisService.py and VisualizationServer.py in their own separate 
terminal window, and this is supported.  However, for convenience, most people will want to start/stop both at once.
You can start both processes by a script at root dir called "run.py"
```
python {CloudbrainAnalysis path}/run.py -i octopicorn -c localhost -n openbci
```
In the future, this will likely be the preferred method, since visualization and analysis will share certain startup
variables, like *device name* and *device id*, not to mention, they will probably also be pulling from a common config 
file. At present, the config file **conf.yml** is only used in the AnalysisModules folder.


## Data Representation
For calculations on EEG data, we will follow the machine learning conventions of "vector" and "matrix".  For anyone
new to this field, it's helpful to know that a *vector* is simply an array. And a *matrix* is an array of arrays.

Specifically, in EEG data, all of the data coming from a single electrode is considered an array of voltage values over
time, or a *vector* containing time-series data for that electrode.  Each electrode, or "channel", is represented as a
vector of voltage readings.

When you have more than one electrode, you now have multiple vectors, and we will put the vectors together in a matrix.

Suppose that, for an EEG system with output resolution of 250Hz, you have 3 electrodes, and you're analyzing one second
of data from this system.  Since our system is 250Hz, or 250 readings per second, this means we have 250 readings x
3 channels.  By using a matrix, this will be represented as a grid. We have two choices:

##### 250 x 3 matrix (example 1)
|time |0 | 1| 2| 3| 4| 5| 6| 7| 8| 9|...|
|-----|--|--|--|--|--|--|--|--|--|--|---|
|Fz   |0.1|0.2|0.3|0.4|0.5|0.6|0.7|0.8|0.9|1.0|...|
|C3   |0.0|0.2|0.4|0.6|0.8|1.0|1.2|1.4|1.6|1.8|...|
|C4   |0.3|0.6|0.9|1.2|1.5|1.8|2.1|2.4|2.7|3.0|...|


##### 3 x 250 matrix (example 2)
|time |Fz | C3| C4|
|-----|---|---|---|
|0    |0.1|0.0|0.3|
|1    |0.2|0.2|1.6|
|2    |0.3|0.4|0.9|
|3    |0.4|0.6|1.2|
|4    |0.5|0.8|1.5|
|5    |0.6|1.0|1.8|
|6    |0.7|1.2|2.1|
|7    |0.8|1.4|2.4|
|8    |0.9|1.6|2.7|
|9    |1.0|1.8|3.0|
|...  |...|...|...|


The choice of whether to represent electrode channel data vectors as rows (example 1), or as columns (example 2), is 
debatable.  Our convention in CloudbrainAnalysis will be to use a 250 columns and 3 rows (example 1).  Each row will 
represent all the datapoints of a single electrode channel.  Each column will represent data across all channels at one 
point in time.

One justification for this is simply that this is intuitively how we tend to think of time series data, with the
horizontal axis of a graph meaning "time".  Additionally, this is a similar convention to what is used in scikit-learn
and MNE packages.  

It has been suggested that there is performance optimization which can be realized by performing calculations on 
elements which are contiguous in memory.  You can read more about that in the section "Note on array order" here: 
http://scikit-image.org/docs/dev/user_guide/numpy_images.html


### To Do
- establish a convention for modules to specify what kinds of visualization they are compatible with.
- establish a convention whereby, if any module in configuration has specified a visualization component, the
visualization server will be auto-started
- conf.yml should be default only, but can be overriden by incoming command line option
- conf.yml should be used by both analysis and viz server

### Metrics To Be Implemented
- downsample using a good algorithm (lttb found in utils folder)
- bandpass filter
- fft
- sfft
- discrete wavelet transform
- windows especially adapted for training (i.e. determine window size based on class label, not fixed number, so all data in a window shares the same class label)
- filter channels (i.e. 8 channels coming in, 2 channels coming out)
- notch filter
- noise/artifact removal
- csp



