import logging
from msg_helper.input import IInput

logger = logging.getLogger(__name__)

class Console(IInput):
    def __init__(self, callback=None):
        super(Console, self).__init__(callback)

    def run(self):
        self.__flagstop__ = False
        logger.info("Starting Console Input...")

        while True:
            if self.__flagstop__: return
            
            try:
                _msg = input("Enter Console command:\n")
                if (self.__callback__ != None):
                    for cb in self.__callback__:
                        try:
                            if cb != None: cb(msg=_msg, input=self)
                        except Exception as ex:
                            logger.error("Console Input Error: " + str(ex), exc_info=True)
            except Exception as ex:
                logger.error("Console Input Error: " + str(ex), exc_info=True)            
                raise
