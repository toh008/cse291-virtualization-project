import json
import boto3
import cv2
import numpy as np

s3 = boto3.client('s3')

target_bucket_name = "myprocessedvideos"

def lambda_handler(event, context):
    
    bucket = "s3varianttest" #event['Records'][0]['s3']['bucket']['name']
    key = "tmp.jpeg" #urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    original_image = "img.jpeg"
    
    response = s3.get_object(Bucket=bucket, Key=key)
    response2 = s3.get_object(Bucket=bucket, Key=original_image)
        
    img_data = response['Body'].read()
    np_array = np.fromstring(img_data, np.uint8)
    gray_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    img_data = response2['Body'].read()
    np_array = np.fromstring(img_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    # Load the cascade
    face_cascade = cv2.CascadeClassifier('./face.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray_image, 1.1, 4)
    
    # Draw rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), 2)
        
    # Write and put the new output to S3 bucket
    cv2.imwrite("/tmp/face.jpeg", image)
    
    s3.put_object(Bucket=target_bucket_name, Key="face.jpeg", Body=open("/tmp/face.jpeg", "rb").read())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
