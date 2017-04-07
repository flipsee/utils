import lirc
from msg_helper.input import IInput

class IR(IInput):
    __remote_command__ = {'KEY_0': 'RedLed.on',
            'KEY_1': 'RedLed.off',
            'KEY_2': 'GreenLed.on',
            'KEY_3': 'GreenLed.off',
            'KEY_4': 'BlueLed.on',
            'KEY_5': 'BlueLed.off',
            'KEY_6': 'Display.show_message("Hello World")',
            'KEY_7': 'Display.clear',
            'KEY_8': 'show_temp_to_screen',
            'KEY_9': 'Display.show_message(TempSensor.temperature())',
            'KEY_UP': 'Display.show_message(run_command("TempSensor.temperature"))',
            'KEY_DOWN': 'Display.show_message(rpicenter.run_command("Btn.get_laststatechange"))'}

    def __init__(self, callback=None, remote_command=None):
        super(IR, self).__init__(callback)
        if remote_command is not None:
            self.__remote_command__ = remote_command

    def run(self):
        self.__flagstop__ = False
        logger.info("Starting IR Input...")
        try:
            sockid = lirc.init("rpicenter", blocking = False)

            while True:
                if self.__flagstop__:
                    lirc.deinit() 
                    return
                try:
                    codeIR = lirc.nextcode()
                    if codeIR:
                        action = codeIR[0]
                        logger.debug("IR Input Received: " + action)
                        if (self.__callback__ != None):
                            for cb in self.__callback__:
                                if cb != None:
                                    try:
                                        #find the command from the dict
                                        command = self.__remote_command__.get(action,"Empty")
                                        logger.debug("IR Remote Command: " + str(command))

                                        if command != "Empty": cb(msg=command, input=self)
                                    except Exception as ex:
                                        logger.error("IR Input Error: " + str(ex), exc_info=True)
                                        raise
                except Exception as ex:
                    logger.error("IR Input Error: " + str(ex), exc_info=True)
                    raise
        except KeyboardInterrupt:
            logger.debug("Shutdown requested...exiting IR")
            raise
