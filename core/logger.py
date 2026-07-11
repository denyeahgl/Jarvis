import logging

class Logger:
    """Jarvis 日志类"""

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 关闭第三方库的 INFO 日志
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)

        self.logger = logging.getLogger("Jarvis")

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)