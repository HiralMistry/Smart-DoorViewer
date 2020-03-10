import boto3
  
access_key = "TODO : Add your access key"
access_secret = "TODO : Add your secret"
region ="us-west-2"
queue_url = "TODO : Add your sqs url"
url = "TODO : Add your sqs url for response"

  
def build_speech_response(title, output, reprompt_text, should_end_session):
   return {
       'outputSpeech': {
           'type': 'PlainText',
           'text': output
       },
       'card': {
           'type': 'Simple',
           'title': "SessionSpeech - " + title,
           'content': "SessionSpeech - " + output
       },
       'reprompt': {
           'outputSpeech': {
               'type': 'PlainText',
               'text': reprompt_text
           }
       },
       'shouldEndSession': True
   }

def build_response(session_attributes, speech_response):
   return {
       'version': '1.0',
       'sessionAttributes': session_attributes,
       'response': speech_response
   }

def receive_message(client, url, waittime):
    while(True):
        try:
            response = client.receive_message(QueueUrl = url, MaxNumberOfMessages = 1)
        
            message = response['Messages'][0]['Body']
            receipt = response['Messages'][0]['ReceiptHandle']
            client.delete_message(QueueUrl = url, ReceiptHandle = receipt)
            return message
        except:
            pass
    return "There was an error while checking person at door."

def post_message(client, message_body, url):
   response = client.send_message(QueueUrl = url, MessageBody= message_body)

def lambda_handler(event, context):
   client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)

   try:
       intent_name = event['request']['intent']['name']
   except:
       message = "Sorry but I do not understand that request"
       speech_res = build_speech_response("Person Query", message, "", "false")
       return build_response({}, speech_res)
  
   if intent_name == "CheckDoor":
       post_message(client, 'image', queue_url)
       while (True):
           message = receive_message(client, url, 30)
           break
   else:
       message = "Sorry but I do not understand that request"
  
   speech_res = build_speech_response("Person Query", message, "", "false")
   return build_response({}, speech_res)