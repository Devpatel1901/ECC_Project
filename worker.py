# worker.py
import shutil
import boto3
import json
import os
from docker_executor import execute_code
from s3_utils import download_from_s3, upload_result_to_s3
from dynamodb_utils import update_status
from static_analyzer import run_static_analysis

sqs = boto3.client("sqs")
QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/774305605898/CodeExecutionQueue"

while True:
    messages = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)

    if "Messages" not in messages:
        print("[...] No messages found. Polling again...")
        continue

    for msg in messages["Messages"]:
        job = json.loads(msg["Body"])
        sid = job["submission_id"]
        lang = job["language"]

        print(f"[+] Processing: {sid} ({lang})")

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

        print(analysis_result)

        analysis_key = f"results/{sid}/static_analysis.json"
        upload_result_to_s3(analysis_key, analysis_result)

        result = execute_code(lang, code_path, input_path)
        print(result)
        output_key = f"results/{sid}/output.json"
        upload_result_to_s3(output_key, result)

        update_status(sid, "COMPLETED", output_key, analysis_key)

        # Delete message
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])

        try:
            shutil.rmtree(work_dir)
            print(f"[+] Cleaned up: {work_dir}")
        except Exception as e:
            print(f"[!] Failed to clean up {work_dir}: {str(e)}")
