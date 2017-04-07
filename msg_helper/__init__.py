import sys, os, glob, inspect, importlib, logging, ast
import uuid, time, logging

logger = logging.getLogger(__name__)

class Message():
    msg_status = {'NEW': "New Message in Queue not send yet",
              'WAITING': "Message sent, waiting for response",
              'EXPIRED': "Message exceed retries or expired",
              'SUCCESS': "Response Received from remote"}

    def __init__(self, msg, sender, receiver, on_response=None, on_expiry=None, requestID=None, expiry=60):
        self.msg = msg
        self.sender = sender
        self.receiver = receiver        
        if requestID is not None:
            self.msg_id = str(requestID)
        else:
            self.msg_id = self.sender + "_" + str(uuid.uuid4())
        #self.msg_id = "12345"
        self.retry_count = 0
        self.last_retry = datetime.min
        self.msg_timestamp = datetime.now()
        self.msg_timestamp_utc = datetime.utcnow()
        self.msg_expiry = self.msg_timestamp + timedelta(seconds=expiry)
        self.response = None
        self.status = self.msg_status["NEW"]
        self.parameters = None
        self.on_response = on_response        
        if on_expiry is not None:
            self.on_expiry = on_expiry
        else:
            self.on_expiry = self.on_response

    def response_received(self, response): #if response is received, parse it and call on_response callback
        logger.debug("Message.response_received: " + str(response))
        if self.on_response is not None:
            self.status =  self.msg_status["SUCCESS"]
            self.response = response
            _old_sender = self.sender
            self.sender = self.receiver
            self.receiver = _old_sender
            return self.on_response(self)
        else: return



_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

from msg_helper import *
