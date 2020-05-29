#!/usr/bin/python
import logging

def setupLogger(loggerName, logFile, logLevel=logging.DEBUG):
  '''
  Function to create Logging setup Handy. This will log and stream.
  
  Arguments:
    loggerName (String)         : Give A Virtual Name for the logger
    logFile    (String)         : File to store the logging details
    logLevel   (logging object) : Level in which loggins starts (INFO, DEBUG, WARNING, ERROR, CRITICAL)
  Operation:
    Creates Logging file and store logs also disply the output
  Returns:
    Logger object to call
  '''
  # Create Logger
  logger = logging.getLogger(loggerName)
  logger.setLevel(logLevel)

  # Create Formatter
  formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')

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