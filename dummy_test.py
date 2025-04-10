import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

sqs = boto3.client("sqs", region_name="us-east-2")
QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/774305605898/CodeExecutionQueue"

while True:
    logger.info("Polling...")
    res = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=5)
    logger.info(json.dumps(res, indent=2))

    if "Messages" in res:
        logger.info("✅ Got a message!")
    else:
        logger.info("🚫 No messages.")
