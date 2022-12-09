import json
import urllib.parse
import boto3
import cv2
import numpy as np

s3 = boto3.client('s3')

target_bucket_name = "processedframes"

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    arr = key.split("/")
    folder_dir = arr[0] + "/"
    filename = arr[-1]

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        
        img_data = response['Body'].read()
        
        # Convert S3 image to np array for cv2
        np_array = np.fromstring(img_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        # Convert image into grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Load the cascade
        face_cascade = cv2.CascadeClassifier('./face.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray_image, 1.1, 4)
        
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), 2)
            
        # Write and put the new output to S3 bucket
        cv2.imwrite("/tmp/face.jpeg", image)
        
        '''
        # Convert image to video format
        # Comment out the below code and use .jpeg if using combineFrames
        height, width, layers = image.shape
        video = cv2.VideoWriter("/tmp/face.mp4", cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 15, (width, height))
        video.write(image)
        video.write(image)
        video.release()
        '''
        
        s3.put_object(Bucket=target_bucket_name, Key=folder_dir+filename[:-4]+".jpeg", Body=open("/tmp/face.jpeg", "rb").read())
        #s3.put_object(Bucket=target_bucket_name, Key=folder_dir+filename[:-4]+".mp4", Body=open("/tmp/face.mp4", "rb").read())
        s3.delete_object(Bucket=bucket, Key=key)
    
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

