import json
import urllib.parse
import boto3
import cv2

s3 = boto3.client('s3')

target_bucket_name = "variant2rawframes"
processed_frames_bucket_name = "variant2processedframes"

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    video_folder = key[:-4]
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
        response = s3.get_object(Bucket=bucket, Key=key)
        url = s3.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': bucket, 'Key': key})
        video = cv2.VideoCapture(url)
        success, img = video.read()
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0
        while (success):
            frame_file = "/tmp/frame%d_%d.jpg" % (count,num_frames)
            cv2.imwrite(frame_file, img)
            s3.put_object(Bucket=target_bucket_name, Key=video_folder+"/"+("frame%d_%d.jpg" % (count,num_frames)), Body=open("/tmp/frame%d_%d.jpg" % (count,num_frames), "rb").read())
            count += 1
            success, img = video.read()
            
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
