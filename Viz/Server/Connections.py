__author__ = 'odrulea'
# -*- coding: utf-8 -*-
"""
Team: I just had to make some changes to this rt_server in order to be able to use it.  Since I don't want to step on anyone else's toes I've copied it in here.
Here is a list of all the changes I've made:

1. this rt_server is not really a server anymore, it's just one connection, of which multiple could be used
2. the host for RABBITMQ_ADDRESS should not be hard-coded to go to cloudbrain.rocks. I've kept that as the default,
but added a settable property on the connection configuration JSON passed from the html if someone wants to use
localhost, for example
OD

"""
import json
import logging

from sockjs.tornado.conn import SockJSConnection
from cloudbrain.settings import RABBITMQ_ADDRESS

from TornadoSubscriber import TornadoSubscriber
from lib.utils import BufferToMatrix


#logging.getLogger().setLevel(logging.ERROR)

class ConnectionPlot(SockJSConnection):
    """RtStreamConnection connection implementation"""
    # Class level variable
    clients = set()

    def __init__(self, session):
        super(self.__class__, self).__init__(session)
        self.subscribers = {}


    def send_probe_factory(self, metric_name):

        def send_probe(body):
            #logging.debug("GOT [" + metric_name + "]: " + body)
            if metric_name == "window":
                """
                matrix type output is a base64 encoded blob which needs to be decoded
                """
                buffer_content = BufferToMatrix(body)
                self.send(buffer_content,True)
            else:
                """
                every other type of output is a dict, so just decode it
                gotcha: Pika tends to make all keys in the dict utf8
                """
                buffer_content = json.loads(body)
                for record in buffer_content:
                    #print "*************************************************"
                    #print record
                    #print "*************************************************"
                    #print type(record)
                    #print type(metric_name)
                    record["metric"] = metric_name
                    self.send(json.dumps(record))

        return send_probe


    def on_open(self, info):
        logging.info("Got a new connection...")
        self.clients.add(self)

    # This will receive instructions from the client to change the
    # stream. After the connection is established we expect to receive a JSON
    # with deviceName, deviceId, metric; then we subscribe to RabbitMQ and
    # start streaming the data.
    #
    # NOTE: it's not possible to open multiple connections from the same client.
    #       so in case we need to stream different devices/metrics/etc. at the
    #       same time, we need to use a solution that is like the multiplexing
    #       in the sockjs-tornado examples folder.
    def on_message(self, message):
        #logging.info("Got a new message: " + message)

        msg_dict = json.loads(message)
        if msg_dict['type'] == 'subscription':
            print "received SUB"
            self.handle_channel_subscription(msg_dict)
        elif msg_dict['type'] == 'unsubscription':
            self.handle_channel_unsubscription(msg_dict)
            print "received UNSUB"
    def handle_channel_subscription(self, stream_configuration):
        device_name = stream_configuration['deviceName']
        device_id = stream_configuration['deviceId']
        metric = stream_configuration['metric']

        # rabbitmq address can be passed in with stream_configuration JSON from frontend
        if 'rabbitmq_address' in stream_configuration:
            rabbitmq_address = stream_configuration['rabbitmq_address']
        else:
            rabbitmq_address = RABBITMQ_ADDRESS

        if metric not in self.subscribers:
            self.subscribers[metric] = TornadoSubscriber(callback=self.send_probe_factory(metric),
                                       device_name=device_name,
                                       device_id=device_id,
                                       rabbitmq_address=rabbitmq_address,
                                       metric_name=metric)

            self.subscribers[metric].connect()

    def handle_channel_unsubscription(self, unsubscription_msg):
        logging.info('Unsubscription received for ' + unsubscription_msg['metric'])
        if unsubscription_msg['metric'] in self.subscribers:
            self.subscribers[unsubscription_msg['metric']].disconnect()

    def on_close(self):
        logging.info('Disconnecting client...')
        for metric in self.subscribers.keys():
            subscriber = self.subscribers[metric]
            if subscriber is not None:
                logging.info('Disconnecting subscriber for metric: ' + metric)
                subscriber.disconnect()

        self.subscribers = {}
        #self.timeout.stop()
        self.clients.remove(self)
        logging.info('Client disconnection complete!')

    def send_heartbeat(self):
        self.broadcast(self.clients, 'message')

"""
This connection type is meant to handle class label tags coming from the, and routs them back to server
"""
class ConnectionClassLabel(SockJSConnection):
    """
    Connection to collect class labels
    """
    def on_open(self, info):
        self.send('ClassLabel Connection established: server will begin receiving data.')

    def on_message(self, message):
        self.send('ClassLabel Connection got your message: ' + message)