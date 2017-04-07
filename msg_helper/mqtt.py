import logging
import paho.mqtt.client as mq
from msg_helper.input import IInput

logger = logging.getLogger(__name__)

class MQTT(IInput): #make mqtt class to also inherit the queue to simplify the structure???
    def __init__(self, server, port, subscribe_topic, publish_topic=None, callback=None, queue=None):
        super(MQTT, self).__init__(callback, queue)
        self.client = mq.Client()
        self.client.on_connect = self.__client_connect__
        self.client.on_message = self.__client_message__
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client.connect(server, int(port), 60)
        self.__event_subscriptions__ = {} #topic, callback method.
    
    def add_event_subscription(self, event_name, callback):
        self.client.subscribe(event_name)
        _event_name = event_name.replace("#", "").replace("+", "")
        logger.info("Subscribing to: " + _event_name + ", callback: " + str(callback))
        self.__event_subscriptions__.update({_event_name: callback})

    def __client_connect__(self, client, userdata, flags, rc):
        logger.info("Subscribing to: " + str(self.subscribe_topic))
        self.client.subscribe(self.subscribe_topic)

    def __client_message__(self, client, userdata, msg):
        logger.debug("MQTT Received Topic: " + msg.topic + " Msg: " + str(msg.payload))
        _msg = msg.payload.decode(encoding="utf-8", errors="ignore")

        _found_in_subscription = False
        for key, callback in self.__event_subscriptions__.items():
            if msg.topic.startswith(key):
                _found_in_subscription = True
                try:
                    #print(ast.literal_eval(_msg))
                    callback(**ast.literal_eval(_msg))
                    return
                except Exception as ex:
                    logger.error(ex, exc_info=True)
                    raise

        if _found_in_subscription == False:
            _topics = msg.topic.split("/")
            _requestID=_topics[-1]
            _message = None

            if self.__queue__ is not None:
                _message = self.__queue__.dequeue(_requestID)
        
            if _message is not None:            
                _message.response_received(response=_msg)
            else:
                _message = Message(msg=_msg, sender=_topics[0], receiver=_topics[2], requestID=_topics[-1])

                if (self.__callback__ != None):
                    for cb in self.__callback__:
                        try:
                            if cb != None: cb(msg=_message.msg, input=self, requestID=_message.msg_id, message=_message)
                        except Exception as ex:
                            logger.error("MQTT Input Error: " + str(ex), exc_info=True)
                            raise

    def publish_msg(self, msg, topic=None):
        _topic = self.publish_topic
        if topic is not None: _topic = topic        
        logger.debug("MQTT Publishing Message Topic: " + str(topic) + " Msg: " + str(msg))
        self.client.publish(_topic, str(msg))

    def send_message(self, message):
        try:
            self.reply(message=message)
            return True, "Message sent"
        except Exception as ex:
            logger.error(ex, exc_info=True)
            return False, "Failed to send message"

    def reply(self, **kwargs):
        _message = kwargs.get('message', None)
        logger.debug("Mqtt sendng Msg: " + str(_message))
        """ {ESP8266}/inbox/{RPiCenter}/{Date Time}/{Trx ID} """
        if _message is not None and isinstance(_message, Message):
            _topic = _message.receiver + "/inbox/" + _message.sender + "/" + str(_message.msg_timestamp) + "/" + str(_message.msg_id)
            #do we need to publish the Msg or the Response?
            if _message.response is not None:
                _msg = _message.response
            else:
                _msg = _message.msg
            logger.debug("MQTT Publishing Message Topic: " + str(_topic) + " Msg: " + str(_msg))
            self.client.publish(_topic, str(_msg))

    def run(self):
        logger.info("Starting MQTT Input...")
        try:
            if self.client is not None: self.client.loop_start()
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def cleanup(self):
        super(MQTT, self).cleanup()
        if self.client is not None:
            self.client.loop_stop() 
            self.client.disconnect()
