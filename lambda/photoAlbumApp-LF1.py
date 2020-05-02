import json
import boto3
import datetime
import requests

ACCESS_KEY = "AKIAX2B7KX4ZPKF2GQMO"
SECRET_KEY = "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"
es_url = "https://vpc-photo-4rv6rs55az2276jgpwkzt7kz6y.us-east-1.es.amazonaws.com/"
index_name = "photos"
headers  ={
        "content-type": "application/json"
    }
def reset_for_test():
    url = es_url + index_name + "/_delete_by_query"
    rm_query = {
  "query": {
    "match": {
      "objectKey": "test.png"
    }
  }
}
    data = json.dumps(rm_query)
    response = requests.post(url, data = data, headers = headers)
    print(response.json())

def checkESIndex():
    print("checkESIndex")
    # delete previous index
    # delete = requests.delete(es_url + index_name)
    # print(delete.json())
    res_test = requests.head(es_url + index_name)
    print(res_test.status_code)
    if res_test.status_code == 404:
        print("create index")
    #  create index
        create_Photos= {
            "mappings":{
                 "properties":{
                      "objectKey": {"type": "text"},  # indexing on all the ids (not sure)
                      "bucket": {"type": "text"},
                        "name": {"type": "text"},
                        "createdTimestamp":{"type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss"
                        },
                        "labels":{"type": "keyword"}
                }
            }
        }
        create_photos = json.dumps(create_Photos)
        headers  ={
        "content-type": "application/json"
        }
        res = requests.put(es_url + index_name, data = create_photos, headers = headers)
        print(res.json())
        
def lambda_handler(event, context):
    checkESIndex()
    # reset_for_test()
    rek = boto3.client('rekognition',
                                       region_name='us-east-1',
                                       aws_access_key_id= ACCESS_KEY,
                                       aws_secret_access_key= SECRET_KEY
                                       )
    
    if "Records" not in event: return
    for record in event["Records"]:
        if 's3' not in record: continue
        if 'bucket' not in record['s3']:continue
        bucket_name = record['s3']['bucket']['name']
        if 'object' not in record['s3']: continue
        object_name = record['s3']['object']['key']
        print(bucket_name, object_name)
        response = rek.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_name,
            }
        }, MinConfidence = 85)
        labels = []
        if 'Labels' not in response: return
        for label in response['Labels']:
            labels.append(label['Name'])
        print(labels)
        dt = datetime.datetime.utcnow()
        str_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        photo_info = {
            "objectKey": object_name,
            "bucket": bucket_name,
            "createdTimestamp": str_time,
            "labels": labels
        }

        # res_test = requests.head(es_url + index_name)
        # print(res_test.status_code)
        data =  json.dumps(photo_info)
        res = requests.post(es_url + index_name + '/_doc/', data = data, headers = headers)
        print(res.json())
    return 


     
     