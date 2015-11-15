__author__ = 'odrulea'

from AnalysisModules.ModuleAbstract import ModuleAbstract
from cloudbrain.utils.metadata_info import get_num_channels
import json

class ModuleDownsample(ModuleAbstract):

    MODULE_NAME = "Downsample Module"
    LOGNAME = "[Analysis Service: Downsample Module] "

    # __init__ is handled by parent ModuleAbstract

    def setup(self):
        super(ModuleDownsample, self).setup()
        self.factor = 1
        self.counter = 0

        # usually this module is used with incoming EEG,
        # so we'd like to know num channels, and a header is for convenience
        self.num_channels = get_num_channels(self.device_name,self.input_feature)
        self.headers = ['timestamp'] + ['channel_%s' % i for i in xrange(self.num_channels)]

    def consume(self, ch, method, properties, body):
        """
        Downsample Module does exactly what it says
        """

        # begin looping through the buffer coming in from the message queue subscriber
        buffer_content = json.loads(body)


        for record in buffer_content:
            """
            record is a dict type object
            """
            # get the nth next data out of the buffer
            # output is an array indexed by column names, i.e. one datapoint per channel
            if(self.counter % self.factor == 0):
                # pass through
                self.write(self.output_feature,record)
                if self.debug:
                    print record

                self.counter = 0

            self.counter = self.counter + 1




