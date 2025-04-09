from s3_utils import download_from_s3
import boto3

if __name__ == '__main__':
    download_from_s3('results/5f0b0f38-2df9-4bd2-aa37-d66aafd9c143/output.json', 'cpp_output.json')
    download_from_s3('results/edd7747b-3842-416a-9545-a3076c721477/output.json', 'py_output.json')

    # sqs = boto3.client("sqs")
    # QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/774305605898/CodeExecutionQueue"

    # messages = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)
    # print(messages)