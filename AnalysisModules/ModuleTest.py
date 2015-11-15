__author__ = 'odrulea'
import ModuleAbstract
from lib.utils import BufferToMatrix

"""
This module does nothing.  Meant to be used as a blank template to start new modules from.
Shows you the basic 2 methods to implement: setup() and consume()
"""
class ModuleTest(ModuleAbstract.ModuleAbstract):

    MODULE_NAME = "Test Module"
    # __init__ is handled by parent ModuleAbstract

    def setup(self):
        ModuleAbstract.ModuleAbstract.setup(self)
        if self.debug:
            print "[" + self.MODULE_NAME + "] setup"

    def consume(self, ch, method, properties, body):
        """
        begin looping through the buffer coming in from the message queue subscriber
        """

        # use this if the input_feature is of type matrix (i.e. window)
        buffer_content = BufferToMatrix(body)
        if self.debug:
            print buffer_content.shape
            print buffer_content
            print
            print

        # use this if the input_feature is an array of json records (i.e. eeg)
        # buffer_content = json.loads(body)
        # for record in buffer_content:
        #     output = record
        #     if self.debug:
        #         print output





