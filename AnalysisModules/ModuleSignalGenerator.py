__author__ = 'odrulea'
from AnalysisModules.ModuleAbstract import ModuleAbstract
import time
import random
import numpy as np

"""
This module generates a signal and publishes to the message queue.

This can include the following types of data:
- random numbers (eeg)
- sine waves
- class labels

"""
class ModuleSignalGenerator(ModuleAbstract):

    MODULE_NAME = "Signal Generator Module"

    # LOGNAME is a prefix used to prepaend to debugging output statements, helps to disambiguate messages since the
    # modules run on separate threads
    LOGNAME = "Analysis Service: Signal Generator Module"

    # __init__ is handled by parent ModuleAbstract

    def setup(self):
        ModuleAbstract.setup(self)

        if self.debug:
            self.LOGNAME = "[" + self.LOGNAME + ": " + self.id + "] "

        # time counter, counts number of ticks in current period
        self.counter = 0;

        # params
        # frequency (Hz)
        self.frequency = 1.
        if self.module_params["frequency"]:
            self.frequency = self.module_params["frequency"]
        # range
        self.range = [0,1]
        if self.module_params["range"]:
            self.range = self.module_params["range"]
        # pattern
        self.pattern = "rand"
        if self.module_params["pattern"]:
            self.pattern = self.module_params["pattern"]

        # num_channels
        # apply default of 1 if nothing was set by a device configuration at command line
        if self.num_channels is None:
            self.num_channels = 1
        if "num_channels" in self.module_params and self.module_params["num_channels"]:
            self.num_channels = self.module_params["num_channels"]

        # what pattern to generate
        if self.pattern == "sine":
            # SINE WAVE PATTERN
            A = 5. # amplitude
            sampling_rate = float(self.frequency) # sampling frequency
            # np.linspace(-np.pi, np.pi, sampling_rate) --> make a range of x values, as many as sampling rate
            self.sine_data = [A * np.sin(x * sampling_rate) for x in np.linspace(-np.pi, np.pi, sampling_rate)]
            self.generate_pattern_func = "generateSine"
        else:
            # RANDOM PATTERN
            self.generate_pattern_func = "generateRandom"

        #if self.debug:
        #   print "FREQUENCY: " + str(self.frequency) + " Hz"
        #   print "RANGE: " + str(self.range)

    def generateSine(self,x):
        message = {"channel_%s" % i: self.sine_data[x] for i in xrange(self.num_channels)}
        return message

    def generateRandom(self,x):
        if self.outputs['data']['data_type'] == self.DATA_TYPE_RAW_DATA:
            message = {"channel_%s" % i: random.randint(self.range[0],self.range[1]) * random.random() for i in xrange(self.num_channels)}
        elif self.outputs['data']['data_type'] == self.DATA_TYPE_CLASS_LABELS:
            message = {"class":random.randint(self.range[0],self.range[1])}
        return message

    def generate(self):
        sleep_length = 1 # default to 1 sec delay
        if self.frequency:
            # how many fractions of 1 whole second? that is how long we will sleep
            sleep_length = (1. / float(self.frequency))

        while(True):
            # get message by whatever pattern has been specified
            message = getattr(self,self.generate_pattern_func)(self.counter)

            message['timestamp'] = int(time.time() * 1000000)
            # sleep long enough to get the frequency right
            time.sleep(sleep_length)

            # deliver 'data' output
            self.write('data', message)

            # reset counter at end of each period
            # example, if your frequency is 250Hz, counter goes from 0-249 then resets to 0
            self.counter += 1
            if self.counter >= self.frequency:
                self.counter = 0
