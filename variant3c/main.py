from flask import Flask,render_template,request
import boto3
import shlex
import subprocess

ACCESS_ID="ASIARIDOM2UAJFBR57FN"
ACCESS_KEY="NKXuqjMl6zJPoWFlKN901o+hxsNxXcgaloBxMQ2h"
ACCESS_TOKEN="FwoGZXIvYXdzENv//////////wEaDEWO/dy5KsN44JBQQyKrAXTxsIcdmPAQqqMXZnEq1bwpZnpn+2m9tSiBSIi7xPvHLZjx4dhXTS2rLs2ygnqkJbb1KNfZbefAUWxywipXQiOkn9ogrC3KEEoudP1MzfVrBw3PoHvKpSvLrCi3DoVUI1eEliBEKVj7H10CICQPt34ZMZ7G0RoCT5a5qSRLOgpmgZYNsvnbThmKe5HLXWF88ooS/W6wTII9VdbhAb5tMIquEvE7lMUlZQr7LijbiLWcBjItsc54myj213UXfFGF7BjOWG/AWlQY9lyELlIP1zYuT9kGiSFjAqTb5B3X2ywe"
s3 = boto3.client('s3')
#s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY, aws_session_token=ACCESS_TOKEN)
app = Flask('__name__')

@app.route('/', methods=['POST'])
def home():
    print("incoming connection")
    content = request.json
    source_bucket_name = content['sourcebucketname']
    folder_dir = content['videofolder'] + "/"
    target_bucket_name = content['targetbucketname']
    video_name = content['videoname']
    num_frames = int(content['numframes'])
    for i in range(0, num_frames):
            name = video_name + "_frame" + str(i) + ("_%d.jpeg" % num_frames)
            s3.download_file(source_bucket_name, folder_dir+name, "./tmp/"+name)

    ffmpeg_cmd = "/usr/bin/ffmpeg -f image2 -i ./tmp/" + video_name + "_frame%d_" + str(num_frames) + ".jpeg ./tmp/output.mp4"
    command1 = shlex.split(ffmpeg_cmd)
    p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    s3.put_object(Bucket=target_bucket_name, Key="processed_"+video_name+".mp4", Body=open("./tmp/output.mp4", "rb").read())
    #s3resource = boto3.resource('s3')
    #bucket = s3resource.Bucket(source_bucket_name)
    #bucket.objects.filter(Prefix=folder_dir).delete()

    return "Done"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)