import json
import urllib.parse
import boto3
import numpy as np 
import cv2
import pickle
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = "s3varianttest"
    key = "img.jpeg"
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print(response['ContentType'])
        
        img_data = response['Body'].read()
        
        # Convert S3 image to np array for cv2
        np_array = np.fromstring(img_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        # Convert image into grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("/tmp/frame.jpeg", gray_image)
        s3.put_object(Bucket="s3varianttest", Key="tmp.jpeg", Body=open("/tmp/frame.jpeg", "rb").read())
        
        return {
            "test": 1
        }
        
    except Exception as e:
        print(e)
        raise e
