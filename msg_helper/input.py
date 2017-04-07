from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import threading, uuid, time, ast, logging

logger = logging.getLogger(__name__)

class IInput:
    __metaclass__ = ABCMeta
    
    def __init__(self, callback=None, queue=False):
        self.__flagstop__ = False
        self.__callback__ = []
        if queue == True:
            self.__queue__ = Queue()
            self.__queue__.send_message = self.send_message
        else: 
            self.__queue__ = None
        if callback != None: self.__callback__.append(callback)

    def get_queue(self):
        return self.__queue__

    def add_callback(self, callback):
        self.__callback__.append(callback)

    def cleanup(self):
        if self.__queue__ is not None: self.__queue__.cleanup()
        self.__flagstop__ = True

    def reply(self, **kwargs):
        _result = 'Reply'

        _requestID = kwargs.get('requestID', None)
        if _requestID is not None: _result = _result + " RequestID: " + str(_requestID)

        _msg = kwargs.get('msg', None)
        if _msg is not None: _result = _result + " Msg: " + str(_msg)

        _message = kwargs.get('message', None)
        if _message is not None: _result = "Reply RequestID: " + str(message.msg_id) + " Msg: " + str(message.msg) + " Response: " + str(message.response)

        print(_result)
    
    @abstractmethod
    def run(self): raise NotImplementedError

    @abstractmethod
    def send_message(self, message): raise NotImplementedError


class Queue:
    def __init__(self, send_message=None, message_notfound=None):
        self.max_retry = 3
        self.retry_waiting_time = 5
        self.send_message = send_message
        #self.message_notfound = message_notfound
        self.queue = {}
        self.queue_thread = None
        self.queue_flagstop = False
        self.queue_waiting_time = 15

    def enqueue(self, message): #add msg to queue
        if isinstance(message, Message):
            self.queue.setdefault(message.msg_id, message)
            print(str(self.queue))
            self.queue_flagstop = False
            self.run()
            return "Message Queued, MsgID: " + message.msg_id
        else: return "Message is invalid"

    def dequeue(self, msg_id): #remove msg from queue manually
        return self.queue.pop(msg_id, None)
        
    def expired(self, msg_id): #if max retries reach or message expired we remove it from the queue, run on on_expired
        message = self.queue.pop(msg_id, None)
        logger.debug("Expired Msg:" + message.msg_id + " " +  message.status + " " + str(message.last_retry))
        if message is not None:
            message.status =  message.msg_status["EXPIRED"]
            if message.on_expiry is not None: return message.on_expiry(message)
        return

    def send(self, message):
        logger.debug("Sending Msg:" + message.msg_id + " " +  message.status + " " + str(message.last_retry))
        message.retry_count = message.retry_count + 1
        message.last_retry = datetime.now()
        message.status =  message.msg_status["WAITING"]
        send_status, response = self.send_message(message)
        if send_status == True and message.on_response == None: #fire and forget
            self.dequeue(message.msg_id)

    def __run_queue__(self):
        while True:
            try:
                #lets check if there is an item in the queue if not stop.
                if len(self.queue) < 1 or self.queue_flagstop == True: 
                    logger.debug("Stoping Queue Job...")
                    return
                for key, msg in list(self.queue.items()):
                    #check which one need tobe send
                    if msg.status == msg.msg_status["NEW"] or (msg.retry_count <= self.max_retry and msg.last_retry + timedelta(seconds=self.retry_waiting_time) <= datetime.now()):
                        self.send(msg)
                    elif msg.retry_count > self.max_retry or msg.msg_expiry < datetime.now():
                        self.expired(msg.msg_id)
                time.sleep(self.queue_waiting_time)
            except Exception as ex:
                logger.error("Queue Error: " + str(ex), exc_info=True)

    def run(self):
        logger.debug("Starting Queue Job...")
        self.queue_thread = threading.Thread(target=self.__run_queue__)
        if self.queue_thread is not None and self.queue_thread.isAlive() == False:
            self.queue_thread.start()
        return self

    def cleanup(self):
        self.queue_flagstop = True
        self.queue.clear()
