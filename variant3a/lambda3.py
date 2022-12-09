import json
import urllib.parse
import boto3
import cv2

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    video_name = json.loads(event['Records'][0]['body'])['videoname']
    source_bucket_name = json.loads(event['Records'][0]['body'])['sourcebucketname']
    i = int(json.loads(event['Records'][0]['body'])['i'])
    target_bucket_name = json.loads(event['Records'][0]['body'])['targetbucketname']
    video_folder = json.loads(event['Records'][0]['body'])['videofolder']
    num_frames = int(json.loads(event['Records'][0]['body'])['numframes'])
    
    url = s3.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': source_bucket_name, 'Key': video_name})
    video = cv2.VideoCapture(url)
    video.set(cv2.CAP_PROP_POS_FRAMES, i)
    success, img = video.read()
    
    if (success):
        video_name = video_name.replace(".", "")
        new_img_name = video_folder + "_frame%d_%d.jpg" % (i,num_frames)
        frame_file = "/tmp/" + new_img_name
        cv2.imwrite(frame_file, img)
        s3.put_object(Bucket=target_bucket_name, Key=video_folder+"/"+new_img_name, Body=open("/tmp/"+new_img_name, "rb").read())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
