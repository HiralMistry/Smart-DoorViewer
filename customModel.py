import boto3
import botocore
from botocore.exceptions import NoCredentialsError
import os
import time
import glob, sys


access_key = "TODO : Add your access key"
access_secret = "TODO : Add your secret"
region = "us-west-2"
queue_url = "TODO : Add SQS url"
url = "TODO : Add SQS url for response messages"

s3_client = boto3.client('s3',aws_access_key_id=access_key, aws_secret_access_key=access_secret)
bucket = 'TODO : bucket'
directory = 'TODO : directory'

def getFiles(dir):
        return [os.path.basename(x) for x in glob.glob(str(dir) + '*.jpg')]

def removeLocal(dir, file):
        os.remove(dir + file)

def upload_s3(s3_client, dir, f, bucket):
        try:
                s3_client.upload_file(dir+f, bucket, f)
                print 'upload successful'
                return
        except:
                print('Unexpected error: ', sys.exc_info())
                return

def pop_message(client, url):
        response = client.receive_message(QueueUrl = url, MaxNumberOfMessages = 1)

        #last message posted becomes messages
        message = response['Messages'][0]['Body']
        receipt = response['Messages'][0]['ReceiptHandle']
        client.delete_message(QueueUrl = url, ReceiptHandle = receipt)
        return message

def detect_custom_labels(filename):
        client = boto3.client('rekognition', aws_access_key_id=access_key, aws_secret_access_key=access_secret, region_name=region)

        response = client.detect_custom_labels(ProjectVersionArn='TODO:Model ARN',
                Image={'S3Object':{ 'Bucket':bucket, 'Name':filename} }, MaxResults=4, MinConfidence= 10)
        print(response)

        return response['CustomLabels']

client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)

time_start = time.time()

while (time.time() - time_start < 60):
        print("Checking...")
        try:
                message = pop_message(client, queue_url)
                print('Message is : ',message)
                if message == 'image':
                        filename = 'capture_'+str(time.time())+'.jpg'
                        os.system("raspistill -o "+filename)
                        filenames = getFiles(directory)
                        print filenames

                        for f in filenames:
                                print 'uploading  %s to %s' % (f, bucket)
                                upload_s3(s3_client, directory, f, bucket)
                                removeLocal(directory, f)

                        labels = detect_custom_labels(filename)

                        for i in range(len(labels)):
                                label = labels[i]
                                message = 'I think person at your door is '+label['Name']
                                response = client.send_message(QueueUrl = url, MessageBody= message)
                                print (label)
                                print(' This is Name : ',label['Name'])
                        break
        except:
                pass

print('Exiting...')
