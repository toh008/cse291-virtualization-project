import json
import urllib.parse
import boto3
import numpy as np
import cv2
import pickle
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    gray_img_data = base64.b64decode(event["image"])
    gray_image = pickle.loads(gray_img_data)
    
    # Load the cascade
    face_cascade = cv2.CascadeClassifier('./face.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray_image, 1.1, 4)
    
    return {
        "faces" : faces.tolist()
    }

    '''
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        #print("CONTENT TYPE: " + response['ContentType'])
        
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
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
        # Write and put the new output to S3 bucket
        #cv2.imwrite("/tmp/face.jpeg", image)
        #s3.put_object(Bucket=bucket, Key="NEW_"+key, Body=open("/tmp/face.jpeg", "rb").read())
        
        return {
            "faces" : faces.tolist()
        }
        
    except Exception as e:
        print(e)
        raise e'''
