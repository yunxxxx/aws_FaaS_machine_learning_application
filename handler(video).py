#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"


import os
import subprocess
import math
import json
import boto3
import tempfile

def video_splitting_cmdline(video_filename):
    filename = os.path.basename(video_filename)
    outfile = os.path.splitext(filename)[0] + ".jpg"

    split_cmd = 'ffmpeg -i ' + video_filename + ' -vframes 1 ' + '/tmp/' + outfile
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

    fps_cmd = 'ffmpeg -i ' + video_filename + ' 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    fps = subprocess.check_output(fps_cmd, shell=True).decode("utf-8").rstrip("\n")
    return outfile

def invoke_face_recognition(bucket_name, image_file_name):
    lambda_client = boto3.client('lambda')
    function_name = 'face-recognition'
    payload = {
        'bucket_name': bucket_name,
        'image_file_name': image_file_name
    }
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
    print(response)
    
def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    # Extracting bucket name and key from S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Download the video file to a temporary location
    temp = '/tmp/' + os.path.basename(object_key)

    # temp_file = tempfile.NamedTemporaryFile(delete=False)
    # temp_file_name = temp_file.name

    s3_client.download_file(bucket_name, object_key, temp)

    # Perform video splitting
    results = video_splitting_cmdline(temp)

    result_file_path = '/tmp/' + results

    # Upload the resulting frame to S3
    s3_path = os.path.splitext(object_key)[0] + '.jpg'
    s3_client.upload_file(result_file_path, "s3 name", s3_path)
    invoke_face_recognition('s3 name', s3_path)

    
    return {
        'statusCode': 200,
        'body': json.dumps('Video processing successful!')
    }
