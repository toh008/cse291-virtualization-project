import json
import urllib.parse
import boto3
import shlex
import subprocess
import os
from time import sleep

s3 = boto3.client('s3')
client = boto3.client('lambda')

def lambda_handler(event, context):
    video_name = event['videoname']
    source_bucket_name = event['sourcebucketname']
    target_bucket_name = event['targetbucketname']
    folder_dir = event['folderdir']
    frame_name = event['framename']
    current_frame_num = int(event['currentframenum'])
    total_frames = int(event['totalframes'])
    print(current_frame_num)
    if (current_frame_num == total_frames):
        print("DONE!")
        return {
            'statusCode': 200,
            'body': json.dumps('Done combining all frames!')
        }
    
    # mp4 does not exist yet so create it by combining frames 0 and 1 and recurse
    if (current_frame_num == 0):
        frame0 = frame_name % 0
        frame1 = frame_name % 1
        s3.download_file(source_bucket_name, folder_dir+frame0, "/tmp/"+frame0)
        s3.download_file(source_bucket_name, folder_dir+frame1, "/tmp/"+frame1)
        with open('/tmp/tmp.txt', 'w') as file:
            file.write('file /tmp/'+frame0+'\n')
            file.write('file /tmp/'+frame1)
        ffmpeg_cmd = "/opt/bin/ffmpeg -f concat -safe 0 -i /tmp/tmp.txt -c copy /tmp/output.mp4"
        command1 = shlex.split(ffmpeg_cmd)
        p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        s3.put_object(Bucket=target_bucket_name, Key=video_name, Body=open("/tmp/output.mp4", "rb").read())

        response = client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:086130873600:function:combineFramesv2',
            InvocationType = 'Event',
            Payload = json.dumps({"videoname": video_name, "sourcebucketname": source_bucket_name, "targetbucketname": target_bucket_name, "folderdir": folder_dir, "framename": frame_name, "currentframenum": "2", "totalframes": total_frames})
        )
        
    else:
        frame_n = frame_name % current_frame_num
        print(frame_n)
        s3.download_file(source_bucket_name, folder_dir+frame_n, "/tmp/"+frame_n)
        s3.download_file(target_bucket_name, video_name, "/tmp/"+video_name)
        with open('/tmp/tmp'+str(current_frame_num)+'.txt', 'w') as file:
            file.write('file /tmp/'+video_name+'\n')
            file.write('file /tmp/'+frame_n)
        ffmpeg_cmd = "/opt/bin/ffmpeg -f concat -safe 0 -i /tmp/tmp"+str(current_frame_num)+".txt -c copy /tmp/output"+str(current_frame_num)+".mp4"
        command1 = shlex.split(ffmpeg_cmd)
        p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        '''
        p = subprocess.Popen(command1, stdout=subprocess.PIPE)
        while p.poll() is None:
            l = p.stdout.readline() # This blocks until it receives a newline.
            print(l)
        print(p.stdout.read())
        '''
        #s3.delete_object(Bucket=target_bucket_name, Key=video_name)
        s3.put_object(Bucket=target_bucket_name, Key=video_name, Body=open("/tmp/output"+str(current_frame_num)+".mp4", "rb").read())
        '''
        s3.download_file(source_bucket_name, folder_dir+frame_n, "/tmp/"+frame_n)
        s3.download_file(target_bucket_name, video_name, "/tmp/"+video_name)
        ffmpeg_cmd = "/opt/bin/ffmpeg -loop 1 -framerate 24 -t 1 -i /tmp/" + video_name + " -i /tmp/" + frame_n + " -filter_complex \"[0][1]concat=n=2:v=1:a=0\" /tmp/output.mp4"
        #ffmpeg_cmd = "/opt/bin/ffmpeg -f image2 -i /tmp/" + arr[0] + "_frame%d_" + str(num_frames) + ".jpeg /tmp/output.mp4"
        command1 = shlex.split(ffmpeg_cmd)
        p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(ffmpeg_cmd)
        s3.put_object(Bucket=target_bucket_name, Key=video_name, Body=open("/tmp/output.mp4", "rb").read())
        # TODO: delete frame after done
        '''
        
        response = client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:086130873600:function:combineFramesv2',
            InvocationType = 'Event',
            Payload = json.dumps({"videoname": video_name, "sourcebucketname": source_bucket_name, "targetbucketname": target_bucket_name, "folderdir": folder_dir, "framename": frame_name, "currentframenum": str(current_frame_num+1), "totalframes": total_frames})
        )
        
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
