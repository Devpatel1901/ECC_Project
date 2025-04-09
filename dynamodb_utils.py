# dynamodb_utils.py
import boto3
from datetime import datetime

db = boto3.resource("dynamodb")
table = db.Table("CodeSubmissions")

def update_status(submission_id, status, result_key, analysis_key=None):
    expression = "SET #s = :s, result_key = :r"
    values = {
        ":s": status,
        ":r": result_key
    }
    names = {
        "#s": "status"
    }

    if analysis_key:
        expression += ", analysis_key = :a"
        values[":a"] = analysis_key

    table.update_item(
        Key={"submission_id": submission_id},
        UpdateExpression=expression,
        ExpressionAttributeValues=values,
        ExpressionAttributeNames=names
    )

