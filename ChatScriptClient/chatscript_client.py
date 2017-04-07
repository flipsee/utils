import socket, logging

logger = logging.getLogger("ChatScriptClient")

class Client():
    def __init__(self, user_name=None, bot_name=None, host=None, port=1024):
        self.delimiter = '\0'
        self.response_buff_size = 1024 
        self.sock = None
        self.connected = False

        self.user_name = user_name
        self.bot_name = bot_name
        if host == None:
            self.host = socket.gethostname() #localhost
        else:
            self.host = host        
        self.port = port

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(1)
            logger.debug('Client Connected')
            self.connected = True
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def close(self):
        try:
            self.sock.close()
            logger.debug('Client Closed')
            self.connected = False
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def send_message(self, message, user_name=None, bot_name=None):
        _send_status = False
        _response = None
        try:
            if user_name is not None: self.user_name = user_name
            if bot_name is not None: self.bot_name = bot_name
            if self.connected == False: self.connect()
            if self.user_name is not None and self.bot_name is not None and message is not None and message != '':
                _msg = self.user_name + self.delimiter + self.bot_name + self.delimiter + message + self.delimiter
                self.sock.send(_msg.encode())
                
                while len(_response) < self.response_buff_size:
                    _packet = sock.recv(self.response_buff_size - len(data))
                    if not _packet: break
                    _response += _packet

                #_response = self.sock.recv(self.response_buff_size).decode()
                _send_status = True
            else:
                logger.debug('Invalid Message')
                _response = 'Invalid Message'
        except Exception as ex:
            logger.error(ex, exc_info=True)
            _response = ex
        finally:
            self.close()
            return _send_status, _response
