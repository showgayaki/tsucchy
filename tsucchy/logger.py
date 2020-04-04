from logging import Formatter, handlers, getLogger
import os


class Logger:
    def __init__(self, file_path, level, name=__name__,):
        self.logger = getLogger(name)
        self.logger.setLevel(level)
        self.level = level
        formatter = Formatter("[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] %(message)s")

        # file
        dir_name = os.path.basename(file_path)
        log_dir = os.path.join(file_path, 'log')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        filename = '{}/log/{}.log'.format(file_path, dir_name)

        handler = handlers.RotatingFileHandler(filename=filename, maxBytes=1048576, backupCount=3)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def logging(self, msg):
        if self.level == 10:
            self.logger.debug(msg)
        elif self.level == 20:
            self.logger.info(msg)
        elif self.level == 30:
            self.logger.warning(msg)
        elif self.level == 40:
            self.logger.error(msg)
        elif self.level == 50:
            self.logger.critical(msg)