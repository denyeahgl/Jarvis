import logging

class Logger:
    '''Jarvis 日志记类'''
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("Jarvis")

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)