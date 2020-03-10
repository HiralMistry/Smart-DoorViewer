import boto3

access_key = "TODO : Add your key"
access_secret = "TODO : Add your secret"
region = "us-west-2"

client = boto3.client('rekognition', aws_access_key_id=access_key, aws_secret_access_key=access_secret, region_name=region)
res = client.start_project_version(ProjectVersionArn='TODO : Model ARN')

print(res)


