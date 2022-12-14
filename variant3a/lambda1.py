import json
import urllib.parse
import boto3

s3 = boto3.client('s3')
client = boto3.client('lambda')

target_bucket_name = "rawframes"

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        
        response = client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:086130873600:function:splitVideoFrames',
            InvocationType = 'Event',
            Payload = json.dumps({"videoname": key, "sourcebucketname": bucket, "targetbucketname": target_bucket_name})
        )
        
        
    
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
