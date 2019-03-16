import logging
import logstash


logger = logging.getLogger("python-logstash-logger")
logger.setLevel(logging.INFO)
host_demo = "10.120.14.204"
logger.addHandler(logstash.TCPLogstashHandler(host_demo,5000))

def logerror(error_message):
    logger.error(error_message)

def loginfo(message):
    logger.info(message)


#loginfo("bcc_test")