import shutil
import boto3
import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from docker_executor import execute_code
from s3_utils import download_from_s3, upload_result_to_s3
from dynamodb_utils import update_status
from static_analyzer import run_static_analysis
import watchtower
from logging import LoggerAdapter
from constants import SQS_QUEUE_URL

# === Base Logging Setup === #
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
    ]
)
base_logger = logging.getLogger("CodeNexusWorker")

# === CloudWatch Log Config === #
LOG_GROUP_NAME = "CodeNexusWorkerLogs"  # You can change this

# === Context Adapter for submission_id === #
class ContextualLogger(LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[submission_id={self.extra.get('submission_id', '-')}] {msg}", kwargs

# === SQS === #
sqs = boto3.client("sqs", region_name="us-east-2")

# === Job Handler === #
def handle_message(msg):
    try:
        job = json.loads(msg["Body"])
        sid = job["submission_id"]
        lang = job["language"]

        # Create a contextual logger with CloudWatch stream per submission
        cloudwatch_handler = watchtower.CloudWatchLogHandler(
            log_group=LOG_GROUP_NAME,
            stream_name=f"worker-{sid}",
            boto3_client=boto3.client("logs", region_name="us-east-2")
        )
        cloudwatch_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

        contextual_logger = logging.getLogger(f"worker-{sid}")
        contextual_logger.setLevel(logging.INFO)
        contextual_logger.addHandler(cloudwatch_handler)

        logger = ContextualLogger(contextual_logger, extra={"submission_id": sid})
        logger.info(f"Processing: {sid} ({lang})")

        ext_map = {
            "python": "code.py",
            "cpp": "code.cpp",
            "java": "Code.java",
            "go": "code.go",
            "js": "code.js"
        }

        work_dir = f"/tmp/{sid}"
        os.makedirs(work_dir, exist_ok=True)

        code_path = os.path.join(work_dir, ext_map[lang])
        input_path = os.path.join(work_dir, "input.txt")

        download_from_s3(job["code_key"], code_path)
        if job.get("input_key"):
            download_from_s3(job["input_key"], input_path)

        analysis_result = run_static_analysis(lang, work_dir, os.path.basename(code_path))
        logger.debug(json.dumps(analysis_result, indent=2))

        analysis_key = f"results/{sid}/static_analysis.json"
        upload_result_to_s3(analysis_key, analysis_result)

        result = execute_code(lang, code_path, input_path)
        logger.debug(result)

        output_key = f"results/{sid}/output.json"
        upload_result_to_s3(output_key, result)

        update_status(sid, "COMPLETED", output_key, analysis_key)

        sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])

        try:
            shutil.rmtree(work_dir)
            logger.info(f"Cleaned up: {work_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up {work_dir}: {str(e)}")

        # Close cloudwatch handler (flush)
        cloudwatch_handler.close()
        contextual_logger.removeHandler(cloudwatch_handler)
    except Exception as e:
        base_logger.exception(f"Exception inside handle_message: {e}")

# === Threaded Worker Pool === #
MAX_WORKERS = 4

while True:
    messages = sqs.receive_message(QueueUrl=SQS_QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)

    if "Messages" not in messages:
        base_logger.info("[...] No messages found. Polling again...")
        continue

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        base_logger.info("Submitting a thread...")
        for msg in messages["Messages"]:
            executor.submit(handle_message, msg)
