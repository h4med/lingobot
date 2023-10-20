# app/log_config.py

import logging

def configure_logging(name, include_file_line=True, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.propagate = False

    logger.setLevel(level)
    ch = logging.StreamHandler()

    if include_file_line:
        formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s [%(name)s] - %(levelname)s - %(message)s')
    
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger