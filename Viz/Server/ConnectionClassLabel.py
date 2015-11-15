# -*- coding: utf-8 -*-
"""
This connection type is meant to handle class label tags coming from the, and routs them back to server
"""
import sys
import logging
import pika
from sockjs.tornado.conn import SockJSConnection

#logging.getLogger().setLevel(logging.ERROR)
class ClassLabelConnection(SockJSConnection):
    """
    Connection to collect class labels
    """
    def on_open(self, info):
        self.send('ClassLabel Connection established: server will begin receiving data.')

    def on_message(self, message):
        self.send('ClassLabel Connection got your message: ' + message)
