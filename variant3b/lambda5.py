import json
import urllib.parse
import boto3
import shlex
import subprocess
import os

s3 = boto3.client('s3')
client = boto3.client('lambda')

target_bucket_name = "myprocessedvideos"

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    arr = key.split("/")[-1].split("_")
    folder_dir = arr[0] + "/"
    #num_frames = int((arr[-1])[:-5])
    num_frames = int((arr[-1])[:-4])
    
    count = 0
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=source_bucket_name, Prefix=folder_dir)
    for page in pages:
        for obj in page['Contents']:
            count += 1

    if (num_frames == count-1):
        name = arr[0] + "_frame%d" + ("_%d.mp4" % num_frames)
        
        response = client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:086130873600:function:combineFramesv2',
            InvocationType = 'Event',
            Payload = json.dumps({"videoname": "processed_"+arr[0]+".mp4", "sourcebucketname": source_bucket_name, "targetbucketname": target_bucket_name, "folderdir": folder_dir, "framename": name, "currentframenum": "0", "totalframes": num_frames})
        )
        
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
