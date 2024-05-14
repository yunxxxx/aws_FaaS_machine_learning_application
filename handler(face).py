__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
#import imutils
import cv2
import json
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
#from shutil import rmtree
import numpy as np
import torch
import boto3


os.environ['TORCH_HOME'] = '/tmp/'
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

def face_recognition_function(key_path):
    # Face extraction
    img = cv2.imread(key_path, cv2.IMREAD_COLOR)
    boxes, _ = mtcnn.detect(img)

    # Face recognition
    key = os.path.splitext(os.path.basename(key_path))[0].split(".")[0]
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    face, prob = mtcnn(img, return_prob=True, save_path=None)
    saved_data = torch.load('/tmp/data.pt')  # loading data.pt file
    if face != None:
        emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
        embedding_list = saved_data[0]  # getting embedding data
        name_list = saved_data[1]  # getting list of names
        dist_list = []  # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        idx_min = dist_list.index(min(dist_list))

        # Save the result name in a file
        with open("/tmp/" + key + ".txt", 'w+') as f:
            f.write(name_list[idx_min])
        return "/tmp/" + key + ".txt"
    else:
        print(f"No face is detected")
    return


def handler(event, context):
    s3_client = boto3.client('s3')

    # Extracting bucket name and key from S3 event
    bucket_name = event['bucket_name']
    object_key = event['image_file_name']

    # Download the video file to a temporary location
    temp = '/tmp/' + os.path.basename(object_key)
    temp2 = '/tmp/' + os.path.basename("data.pt")

    # temp_file = tempfile.NamedTemporaryFile(delete=False)
    # temp_file_name = temp_file.name

    s3_client.download_file(bucket_name, object_key, temp)
    s3_client.download_file("s3 name", "data.pt", temp2)

    # Perform video splitting
    results = face_recognition_function(temp)


    s3_path = os.path.splitext(object_key)[0] + '.txt'
    s3_client.upload_file(results, "s3 name", s3_path)
    return {
        'statusCode': 200,
        'body': json.dumps('Video processing successful!')
    }
