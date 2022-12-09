import json
import urllib.parse
import boto3
import cv2

s3 = boto3.client('s3')
client = boto3.client('lambda')
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    
    video_name = event['videoname']
    source_bucket_name = event['sourcebucketname']
    target_bucket_name = event['targetbucketname']
    video_folder = video_name[:-4]
    processed_frames_bucket_name = "processedframes"
    
    s3.put_object(
        Bucket=target_bucket_name,
        Body='',
        Key=video_folder+'/'
    )
    
    s3.put_object(
        Bucket=processed_frames_bucket_name,
        Body='',
        Key=video_folder+'/'
    )
    
    try:
        url = s3.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': source_bucket_name, 'Key': video_name})
        video = cv2.VideoCapture(url)
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        for i in range(0, num_frames+1):
            sqs.send_message(QueueUrl="https://sqs.us-west-2.amazonaws.com/086130873600/frames-queue", 
                            MessageBody=json.dumps({"videoname": video_name, "sourcebucketname": source_bucket_name, "i": i, "targetbucketname": target_bucket_name, "videofolder": video_folder, "numframes": str(num_frames)}))
    
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    


'''
            client.invoke(
                FunctionName = 'arn:aws:lambda:us-west-2:086130873600:function:processVideoFrame',
                InvocationType = 'Event',
                Payload = json.dumps({"videoname": video_name, "sourcebucketname": source_bucket_name, "i": i, "targetbucketname": target_bucket_name})
            )
            '''