import json
import urllib.parse
import boto3
import shlex
import subprocess
import os

s3 = boto3.client('s3')

target_bucket_name = "variant2myprocessedvideos"

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    arr = key.split("/")[-1].split("_")
    file_name = key.split("/")[0]
    folder_dir = key.split("/")[0] + "/"
    num_frames = int((arr[-1])[:-5])
    
    count = 0
    paginator = s3.get_paginator('list_objects_v2')
    print(folder_dir)
    pages = paginator.paginate(Bucket=source_bucket_name, Prefix=folder_dir)
    for page in pages:
        for obj in page['Contents']:
            count += 1

    if (num_frames == count-1):
        for i in range(0, num_frames):
            name = "frame" + str(i) + ("_%d.jpeg" % num_frames)
            s3.download_file(source_bucket_name, folder_dir+name, "/tmp/"+name)
        
        ffmpeg_cmd = "/opt/bin/ffmpeg -f image2 -i /tmp/" + "frame%d_" + str(num_frames) + ".jpeg /tmp/output.mp4"
        command1 = shlex.split(ffmpeg_cmd)
        p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        s3.put_object(Bucket=target_bucket_name, Key="processed_"+file_name+".mp4", Body=open("/tmp/output.mp4", "rb").read())
        s3resource = boto3.resource('s3')
        bucket = s3resource.Bucket(source_bucket_name)
        bucket.objects.filter(Prefix=folder_dir).delete()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    