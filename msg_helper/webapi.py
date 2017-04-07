import logging
import lirc
from msg_helper.input import IInput

logger = logging.getLogger(__name__)

class WebAPI(IInput):
    def __init__(self, address, port, callback=None):
        super(WebAPI, self).__init__(callback)
        self.app = Flask(__name__)
        self.webapi_port = int(port)
        self.webapi_address = str(address)
        self.routes() #load all the routes

    def run(self):
        logger.info("Starting WebAPI Input...")
        self.app.run(host=self.webapi_address, port=self.webapi_port, debug=True, use_reloader=False)
    
    def cleanup(self):
        try:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None: func()
        except:
            pass

    def routes(self):
        #we use single route to catch all
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def catch_all(path):
            command = self.__parse_input__(path)
            result = self.__run_command__(command)
            return 'You enter: %s' % command + " Response: " + str(result)

    def __parse_input__(self, path):
        cmd = ""
        'convention: http://rpi.center/{Command}/{Parameter1}/{Parameter2}...'
        items = list(filter(None, path.split('/')))
        for idx, item in enumerate(items):
            cmd = cmd + item
            if idx == 0 and len(items) > 1: 
                cmd = cmd + "('"
            elif len(items) > 1 and idx < len(items)-1:
                cmd = cmd + "','"
            elif len(items) > 1 and idx == len(items)-1:
                cmd = cmd + "')"
        return cmd

    def __run_command__(self, command):
        try:
            if (self.__callback__ != None):
                for cb in self.__callback__:
                    try:
                        if cb != None: 
                            return cb(msg=command) #do not pass the input param here as synchronus
                    except Exception as ex:
                        logger.error("WebAPI Input Error: " + str(ex), exc_info=True)
        except Exception as ex:
            logger.error("WebAPI Input Error: " + str(ex), exc_info=True)
            raise
