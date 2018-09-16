import os
import json
import logging
import logging.config
from datetime import datetime



class Logger(object):
    def __init__(self, class_name=None):


        c = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    }
                },

                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO",
                        "formatter": "simple",
                        "stream": "ext://sys.stdout"
                    },

                    "info_file_handler": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "INFO",
                        "formatter": "simple",
                      "filename": "./logs/info.log",
                        "maxBytes": 10485760,
                        "backupCount": 20,
                        "encoding": "utf8"
                    },

                    "error_file_handler": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "DEBUG",
                        "formatter": "simple",
                        "filename": "./logs/errors.log",
                        "maxBytes": 10485760,
                        "backupCount": 20,
                        "encoding": "utf8"
                    }
                },

                "loggers": {
                    "my_module": {
                        "level": "INFO",
                        "handlers": ["console"],
                        "propagate": "no"
                    }
                },

                "root": {
                    "level": "INFO",
                    "handlers": ["console", "info_file_handler", "error_file_handler"]
                }
            }

        info_path = os.path.splitext(c['handlers']['info_file_handler']['filename'])[0]
        error_path = os.path.splitext(c['handlers']['error_file_handler']['filename'])[0]
        date = datetime.now().strftime('%Y-%m-%d')
        c['handlers']['info_file_handler']['filename'] = info_path + '_' + date + '.log'
        c['handlers']['error_file_handler']['filename'] = error_path + '_' + date + '.log'

        try:
            logging.config.dictConfig(c)
        except ValueError or FileNotFoundError:
            try:
                os.makedirs("./logs")
            except FileExistsError:
                pass
            c['handlers']['info_file_handler']['filename'] = './logs/info' + '_' + date + '.log'
            c['handlers']['error_file_handler']['filename'] = './logs/errors' + '_' + date + '.log'
            logging.config.dictConfig(c)

        self.logger = logging.getLogger(class_name)

    def get(self):
        return self.logger
