# dynamodb_utils.py
import boto3
from datetime import datetime

db = boto3.resource("dynamodb")
table = db.Table("CodeSubmissions")

def update_status(submission_id, status, result_key):
    table.update_item(
        Key={"submission_id": submission_id},
        UpdateExpression="SET #s = :s, result_key = :r, updated_at = :t",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": status,
            ":r": result_key,
            ":t": datetime.utcnow().isoformat()
        }
    )
