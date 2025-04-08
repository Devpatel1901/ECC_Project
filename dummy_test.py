from s3_utils import download_from_s3
import boto3

if __name__ == '__main__':
    download_from_s3('results/6273bcd3-c5ab-40a2-8203-16a62a8ba910/output.txt', 'py_output.txt')
    download_from_s3('results/82030125-dbfd-4f85-bbe2-20331fdd1127/output.txt', 'cpp_output.txt')
    # download_from_s3('results/682d98bc-12fa-4ef8-95f3-83df3c1b4044/output.txt', 'java_output.txt')
    # download_from_s3('results/84b1b3f0-8728-490d-8672-2e915664ad55/output.txt', 'go_output.txt')
    # download_from_s3('results/77bf0951-0a3d-4940-89a9-a33f27d8d200/output.txt', 'js_output.txt')

    # sqs = boto3.client("sqs")
    # QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/774305605898/CodeExecutionQueue"

    # messages = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)
    # print(messages)