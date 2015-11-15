__author__ = 'odrulea'

import json

import numpy as np

from AnalysisModules.ModuleAbstract import ModuleAbstract
from lib.utils import MatrixToBuffer

"""
The Windows Module is meant for bounding raw EEG data into epochs.
The current implementation is a "rolling" window of fixed width.  This is typically used in the testing or "online"
usage of BCI.  This type of window is characterized by a fixed width, and an overlap parameter. The idea is that, as
live data is coming in, you are constantly checking it against a trained model. This could also be used as a sort of
simple buffering on raw data, if you set the overlap to 0 for example.

This module will need to be expanded (or implemented in a similar, separate module) to perform the kind of windowing
used in training phase.  In that scenario, the goal is not to be constantly checking, but rather to collect windows
in which every datum belongs to the same class label.  Such a module would have to use an input stream containing
class label information as well as an EEG input.
"""

class ModuleWindows(ModuleAbstract):
    
    MODULE_NAME = "Windows Module"
    LOGNAME = "[Analysis Service: Windows Module] "

    # __init__ is handled by parent ModuleAbstract

    def setup(self):
        super(ModuleWindows,self).setup()

        # init self vars
        # window params
        self.samples_per_second = 1000 # this is unused, just a placeholder for now
        if "samples_per_window" in self.module_params:
            self.samples_per_window = self.module_params["samples_per_window"]
        else:
            self.samples_per_window = 500

        if "window_overlap" in self.module_params:
            self.window_overlap = self.module_params["window_overlap"]
        else:
            self.window_overlap = 100

        if self.debug:
            print self.LOGNAME + "Samples per window:" + str(self.samples_per_window)
            print self.LOGNAME + "Window overlap:" + str(self.window_overlap)

        # create a blank matrix of zeros as a starting window
        self.window = np.zeros((self.samples_per_window, self.num_channels))
        self.nextWindowSegment = np.zeros((self.window_overlap, self.num_channels))
        self.trimOldWindowDataIndexRange = np.arange(self.window_overlap)

        self.plotActive = True
        self.windowFull = False
        self.fill_counter = 0
        self.rolling_counter = 0




    def consume(self, ch, method, properties, body):
        """
        Windows Module chops streaming multi-channel time series data into 'windows'
        Semantically, window = epoch = trial = matrix
        As matrix, window has dimensions [rows, cols] - standard notation for numpy, matlab, etc

        The row captures datum per second
        The column captures datum per channel. Column can represent one channel as a single time-series vector.

        If this were plotted as a time series graph,
        rows = x-axis (time)
        each col = y-axis (voltage)
        You could use this matrix to plot n-channels number of streaming graphs,
        or you could superimpose n-channels number of lines on the same streaming graph
        """

        # begin looping through the buffer coming in from the message queue subscriber
        buffer_content = json.loads(body)

        for record in buffer_content:

            # get the next data out of the buffer as an array indexed by column names
            arr = np.array([record.get(column_name, None) for column_name in self.headers])

            if self.windowFull is False:
                # window is not full yet
                # just keep collecting data into main window until we have filled up the first one
                # i.e. write next row in matrix
                self.window[self.fill_counter, :] = arr[1:len(self.headers)] # note timestamp is not used (i.e. arr[0])
                self.fill_counter = self.fill_counter + 1
                #print "still filling up first window: " + str(self.fill_counter) + " rows so far"

                # once we've reached one full window length, set the flag
                if self.fill_counter == self.samples_per_window:
                    self.windowFull = True
                    if self.debug:
                        print self.LOGNAME + "Received " + str(self.samples_per_window) + " lines:\n"

            else:
                # accumulate every new data into next window segment
                self.nextWindowSegment[self.rolling_counter, :] = arr[1:len(self.headers)]
                # not yet, just keep incrementing rolling counter
                self.rolling_counter = self.rolling_counter + 1

                # check if we have reached next window yet
                if(self.rolling_counter == self.window_overlap):
                    # reached overlap, time to roll over to next window

                    # Step 1: trim off old data rows from the back
                    self.window = np.delete(self.window, self.trimOldWindowDataIndexRange, 0)
                    # Step 2: append next window segment onto the front
                    self.window = np.vstack((self.window, self.nextWindowSegment))

                    # since we've got a new window, time to publish it
                    windowJson = MatrixToBuffer(self.window)
                    self.write(self.output_feature, windowJson)

                    # since we've rolled to a new window, time to reset the rolling counter
                    self.rolling_counter = 0

                    # debug
                    if self.debug:
                        print self.window
