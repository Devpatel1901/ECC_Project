# main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

from fastapi.responses import JSONResponse
import boto3
import json
from starlette.status import HTTP_413_REQUEST_ENTITY_TOO_LARGE
from s3_utils import upload_to_s3
from constants import SQS_QUEUE_URL, DDB_TABLE, S3_BUCKET

MAX_INPUT_SIZE = 64 * 1024  # 64 KB


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

@app.post("/submit")
async def submit_code(language: str = Form(...), code: UploadFile = Form(...), stdin: UploadFile = Form(None)):
    submission_id = str(uuid4())

    # Validate input file size
    if stdin:
        content = await stdin.read()
        if len(content) > MAX_INPUT_SIZE:
            raise HTTPException(
                status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Input file too large. Max allowed: 64 KB"
            )
        # Rewind file pointer since we already read it
        stdin.file.seek(0)

    ext_map = {
        "python": "code.py",
        "cpp": "code.cpp",
        "java": "Code.java",
        "go": "code.go",
        "js": "code.js"
    }

    # Save to S3
    code_key = f"submissions/{submission_id}/{ext_map[language]}"
    input_key = f"submissions/{submission_id}/input.txt" if stdin else None

    await upload_to_s3(code, code_key)
    if stdin:
        await upload_to_s3(stdin, input_key)

    # Send job to SQS
    job = {
        "submission_id": submission_id,
        "language": language,
        "code_key": code_key,
        "input_key": input_key
    }
    sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(job))

    return {"submission_id": submission_id, "job": job, "status": "QUEUED"}

@app.get("/results/{submission_id}")
def get_submission_result(submission_id: str):
    table = dynamodb.Table(DDB_TABLE)

    try:
        # Step 1: Get job metadata from DynamoDB
        response = table.get_item(Key={"submission_id": submission_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Submission ID not found")

        if item["status"] != "COMPLETED":
            return JSONResponse(content={
                "status": item["status"],
                "message": "Code is still being processed. Please try again later."
            }, status_code=202)

        result_key = item.get("result_key")
        if not result_key:
            raise HTTPException(status_code=500, detail="Result key not available")

        # Step 2: Fetch result JSON from S3
        s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=result_key)
        result_content = s3_obj["Body"].read().decode("utf-8")
        result_json = json.loads(result_content)

        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/analysis/{submission_id}")
def get_analysis(submission_id: str):
    table = dynamodb.Table(DDB_TABLE)

    item = table.get_item(Key={"submission_id": submission_id}).get("Item")
    if not item or "analysis_key" not in item:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=item["analysis_key"])
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

