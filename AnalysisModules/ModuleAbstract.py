__author__ = 'odrulea'
from abc import ABCMeta, abstractmethod
from cloudbrain.subscribers.PikaSubscriber import PikaSubscriber
from cloudbrain.publishers.PikaPublisher import PikaPublisher
from cloudbrain.utils.metadata_info import get_num_channels

class ModuleAbstract(object):
    __metaclass__ = ABCMeta

    MODULE_NAME = "Abstract"

    def __init__(self, device_name, device_id, rabbitmq_address, input_feature, output_feature=None, module_params = None):
        """
        global constructor for all module classes, not meant to be overwritten by subclasses
        :param device_name:
        :param device_id:
        :param rabbitmq_address:
        :param input_feature:
        :param output_feature:
        :param module_params:
        :return:
        """

        # set global properties common to all
        self.device_name = device_name
        self.device_id = device_id
        self.rabbitmq_address = rabbitmq_address
        self.input_feature = input_feature
        self.output_feature = output_feature
        self.module_params = module_params # subclasses can set further from this in setup()

        self.subscribers = {}
        self.publishers = {}
        self.output_buffers = {}
        self.buffer_size = 100

        self.num_channels = 0
        self.headers = []

        # debug
        self.debug = False
        if 'debug' in self.module_params:
            if self.module_params['debug'] is True:
                self.debug = True


        # call setup()
        self.setup()


    def setup(self):
        """
        Generic setup for any analysis module, can be overriden by implementing in any child class
        This sets up subscriber and publisher based on input and output feature names
        """
        # usually this module is used with incoming EEG,
        # so we'd like to know num channels, and a header is for convenience
        # hard-coded "eeg" could be a problem if the device's metric name for raw data is not "eeg"
        self.num_channels = get_num_channels(self.device_name,"eeg")
        self.headers = ['timestamp'] + ['channel_%s' % i for i in xrange(self.num_channels)]

        # if input, instantiate subscribers
        if self.input_feature is not None:
            self.subscribers[self.input_feature] = PikaSubscriber(device_name=self.device_name,
                                                         device_id=self.device_id,
                                                         rabbitmq_address=self.rabbitmq_address,
                                                         metric_name=self.input_feature)

        # if output, instantiate publishers
        if self.output_feature is not None:
            self.publishers[self.output_feature] = PikaPublisher(
                                                        device_name=self.device_name,
                                                        device_id=self.device_id,
                                                        rabbitmq_address=self.rabbitmq_address,
                                                        metric_name=self.output_feature)

            # also instantiate an output buffer for each publisher
            self.output_buffers[self.output_feature] = []


    def start(self):
        """
        Consume and write data to file
        :return:
        """
        # unleash the hounds!
        if self.publishers:
            if self.debug:
                print "[" + self.MODULE_NAME + "] starting publishers"
            for publisherKey, publisher in self.publishers.iteritems():
                publisher.connect()
                if self.debug:
                    print "[" + self.MODULE_NAME + "] publisher " + publisherKey + " connected"

        # it begins!
        if self.debug:
            print "[" + self.MODULE_NAME + "] starting subscribers"
        for subscriberKey, subscriber in self.subscribers.iteritems():
            subscriber.connect()
            subscriber.consume_messages(self.consume)
            if self.debug:
                print "[" + self.MODULE_NAME + "] subscriber " + subscriberKey + " connected and started"

        return

    def stop(self):
        """
        Unsubscribe and close file
        :return:
        """
        print "Abstract: stopped"
        self.subscriber.disconnect()


    def consume(self, ch, method, properties, body):
        """
        consume the message queue from rabbitmq
        :return:
        """
        print "Abstract: consume"

    def write(self, metric_name, datum):
        """
        add one data point to the buffer
        """
        self.output_buffers[metric_name].append(datum)

        # if buffer is full, publish it, using appropriate publisher
        if len(self.output_buffers[metric_name]) >= self.buffer_size:
            self.publishers[metric_name].publish(self.output_buffers[metric_name])
            self.output_buffers[metric_name] = []
