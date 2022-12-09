import json
import urllib.parse
import boto3
import requests

s3 = boto3.client('s3')

target_bucket_name = "myprocessedvideos"

def lambda_handler(event, context):
     
    # Get the object from the event and show its content type
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    arr = key.split("/")[-1].split("_")
    folder_dir = arr[0] + "/"
    num_frames = int((arr[-1])[:-5])
    
    count = 0
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=source_bucket_name, Prefix=folder_dir)
    for page in pages:
        for obj in page['Contents']:
            count += 1
    
    if (num_frames == count-1):
        url = 'http://ec2-18-246-6-243.us-west-2.compute.amazonaws.com:5000'
        myobj = {'sourcebucketname': source_bucket_name, 'videofolder':arr[0], 'targetbucketname': target_bucket_name, 'videoname':arr[0], 'numframes': str(num_frames)}
        try:
            x = requests.post(url, json = myobj, timeout=0.5)
        except:
            #ignore exception of timeout, ec2 will handle the rest
            pass
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
