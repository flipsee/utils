import logging

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    from chatscript_client import Client

    try:
        logging.info("=== ChatScriptClient Started ===")
        user_name = "Mark"
        bot_name = "Harry"
        crc = Client(user_name, bot_name)
       
        while True:
            _input = input(">> ")
            _send_status, _response = crc.send_message(message=_input)
            if _send_status:
                print(bot_name + ": " + str(_response))
            else:
                print("Exception while sending the message: " + str(ex))
    except KeyboardInterrupt:
        logging.info("=== Shutdown requested! exiting ===")
    except Exception as ex:
        logging.error(ex, exc_info=True)
        raise

if __name__ == '__main__':
    main()
