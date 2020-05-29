#!/usr/bin/python
import logging

def setup_lambda_logger():
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')
    logger = logging.getLogger()
    for h in logger.handlers:
        h.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    
    return logger