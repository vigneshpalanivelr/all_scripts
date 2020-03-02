#!/usr/bin/python2
import logging

def setupLogger(loggerName, logFile, loglevel=logging.INFO)
  # Create Logger
  logger = logging.getLogger(loggerName)
  logger.setlevel(loglevel)
  
  # Create Formatter
  formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)', datefmt='%Y-%m-%d %H:%M:%S %Z')
  
  # Create file handler which logs even DEBUG messages
  fileHandler = logging.FileHandler(logFile, mode='w')
  fileHandler.setLevel(logging.DEBUG)
  fileHandler.setFormatter(formatter)
  
  # Create stream handler which logs even DEBUG messages
  streamHandler = logging.StreamHandler()
  streamHandler.setLevel(logging.DEBUG)
  streamHandler.setFormatter(formatter)
  
  # Add Handlers to Logger
  logger.addHandler(fileHandler)
  logger.addHandler(streamHandler)
  
  # Return logger
  return logger
