import json
import urllib.parse
import boto3
import numpy as np 
import cv2
import pickle
import base64

s3 = boto3.client('s3')
client = boto3.client('lambda')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = "networkvarianttest"
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
        gray_img_data = pickle.dumps(gray_image)
        
        response = client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:086130873600:function:opencv-test',
            InvocationType = 'RequestResponse',
            Payload = json.dumps({"image": base64.b64encode(gray_img_data).decode('ascii')})
        )
        
        responseFromHelper = json.load(response["Payload"])
        
        faces = responseFromHelper['faces']
        
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), 2)
            
        # Write and put the new output to S3 bucket
        cv2.imwrite("/tmp/face.jpeg", image)
        s3.put_object(Bucket="networkvarianttest", Key="face.jpeg", Body=open("/tmp/face.jpeg", "rb").read())
        
        return {
            "test": 1
        }
        
    except Exception as e:
        print(e)
        raise e
