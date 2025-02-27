# import logging
#
#
#
# Logs = logging.getLogger()
# Logs.setLevel("DEBUG")
# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
# Logs.addHandler(consoleHandler)
#
# logging.getLogger('boto3').setLevel(logging.WARNING)
# logging.getLogger('botocore').setLevel(logging.WARNING)
#
#
# async def async_info(request_id,funtion_name, log_stream):
#     Logs.info('{} {} {}'.format(request_id,funtion_name, log_stream))
#
#
# async def async_debug(request_id,funtion_name, log_stream):
#     Logs.debug('{} {} {}'.format(request_id,funtion_name, log_stream))
#
#
# async def async_error(request_id,funtion_name, log_stream):
#     Logs.error('{} {} {}'.format(request_id,funtion_name, log_stream))
#
#
# async def async_warning(request_id,funtion_name, log_stream):
#     Logs.warning('{} {} {}'.format(request_id,funtion_name, log_stream))
#
#
# async def async_critical(request_id,funtion_name, log_stream):
#     Logs.critical('{} {} {}'.format(request_id,funtion_name, log_stream))



# class LogLevels():
#     """
#     Creating enums using class
#     """
#     def _init_(self,log_level,log_stream,exc_info=False,request_id=''):
#         self.log_level=log_level
#         self.request_id=request_id
#         self.log_stream=log_stream
#         self.INFO = logging.INFO
#         self.DEBUG = logging.DEBUG
#         self.WARNING = logging.WARNING
#         self.ERROR = logging.ERROR
#         self.CRITICAL = logging.CRITICAL
#
#
#     def log_conditions(self):
#         if self.log_level == self.INFO:
#            SBLogger.info('{} {} '.format(self.request_id,self.log_stream))
#         if self.log_level == self.WARNING:
#             SBLogger.warning('{} {}  '.format(self.request_id,self.log_stream))
#         if self.log_level == self.ERROR:
#             SBLogger.error('{} {}'.format(self.request_id,self.log_stream))
#         if self.log_level == self.DEBUG:
#            SBLogger.debug('{} {} '.format(self.request_id,self.log_stream))
#         if self.log_level == self.CRITICAL:
#             SBLogger.critical('{} {}'.format(self.request_id,self.log_stream))
#
#
# def logs(log_level,request_id,log_stream='',exc_info=False):
#     LogLevels(log_level=log_level,log_stream=log_stream,exc_info=exc_info,request_id=request_id).log_conditions()

from loguru import logger
import asyncio
from app.utils.smtp.smtp import send_alert_system

def custom_function(request_id, function_name, log_stream):
    print(f"Executing function for log: {request_id} {function_name} {log_stream}")
    to_address = ""
    email_message = f"Subject: Alert System!\n\nCode Fat gaya"
    send_alert_system(to_address, email_message)

def log_callback(message):
    try:
        request_id, function_name, log_stream = message.record["message"].split(" ", 2)
        asyncio.create_task(custom_function(request_id, function_name, log_stream))  # Run in background
    except ValueError:
        print("Invalid log format")

logger.add(log_callback, level="ERROR")

# Asynchronous logging functions
async def async_info(request_id, function_name, log_stream):
    logger.info(f"{request_id} {function_name} {log_stream}")

async def async_debug(request_id, function_name, log_stream):
    logger.debug(f"{request_id} {function_name} {log_stream}")

async def async_error(request_id, function_name, log_stream):
    logger.error(f"{request_id} {function_name} {log_stream}")

async def async_warning(request_id, function_name, log_stream):
    logger.warning(f"{request_id} {function_name} {log_stream}")

async def async_critical(request_id, function_name, log_stream):
    logger.critical(f"{request_id} {function_name} {log_stream}")

asyncio.run(async_error("121111", "", "Validation Execution Started"))
