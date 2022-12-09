import json
import urllib.parse
import boto3
import cv2
import subprocess
import shlex
import os

s3 = boto3.client('s3')

target_bucket_name = "variant1myprocessedvideos"
ffmpeg_bucket = "myrawvideos"
s3.download_file(ffmpeg_bucket, "ffmpeg", "/tmp/ffmpeg")
os.chmod("/tmp/ffmpeg", 0o0777)

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        url = s3.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': bucket, 'Key': key})
        video = cv2.VideoCapture(url)
        success, img = video.read()
        count = 0
        while (success):
            frame_file = ("/tmp/frame%d.jpg" % count)
            cv2.imwrite(frame_file, img)
            count += 1
            success, img = video.read()
        
        i = 0
        cascade_classifier = cv2.CascadeClassifier('./opencv-cascade-classifier.xml')
        while (i < count): 
            img = cv2.imread("/tmp/frame%d.jpg" % i)
            grayscale_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = cascade_classifier.detectMultiScale(grayscale_img, 1.1, 4)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imwrite(("/tmp/new_frame%d.jpg" % i), img)
            i += 1
        
        ffmpeg_cmd = "/tmp/ffmpeg -f image2 -i /tmp/" + "new_frame%d.jpg /tmp/output.mp4"
        command1 = shlex.split(ffmpeg_cmd)
        p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        s3.put_object(Bucket=target_bucket_name, Key="processed_video.mp4", Body=open("/tmp/output.mp4", "rb").read())
        
        '''
        image_names = ["/tmp/new_frame%d.jpg" % i for i in range(0, count)]
        images = []
        width = 0
        height = 0
        for img in image_names:
            frame = cv2.imread(img)
            height, width, layers = frame.shape
            images.append(frame)
        video = cv2.VideoWriter("/tmp/output.mp4", cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 15, (width, height))
        for i in range(len(images)):
            video.write(images[i])
        video.release()
        '''

        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

