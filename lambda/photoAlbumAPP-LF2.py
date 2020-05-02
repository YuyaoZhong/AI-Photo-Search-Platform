import json
import boto3
import requests

ACCESS_KEY = "AKIAX2B7KX4ZPKF2GQMO"
SECRET_KEY = "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"
BOT_NAME = "PhotoAlbumSearch"
es_url = "https://vpc-photo-4rv6rs55az2276jgpwkzt7kz6y.us-east-1.es.amazonaws.com/"
index_name = "photos"
headers  ={
        "content-type": "application/json"
    }
def search_in_es(query):
    search_url = es_url + index_name + '/_search'
    es_query = {
          "query": {
            "match": {
              "labels": query 
            }
          }
        }
    data = json.dumps(es_query)
    response = requests.get(search_url, data = data, headers = headers).json()
    print(response)
    if "hits" not in response or "hits" not in response["hits"]: return []
    results = response["hits"]["hits"]
    if len(results) == 0: return []
    visited_imgs = {}
    imgs = []
    for res in results:
        if "_source" not in res: continue
        res = res["_source"]
        if "objectKey" not in res or "bucket" not in res: continue
        objectKey, bucket = res["objectKey"], res["bucket"]
        # in order to avoid repetition
        if bucket not in visited_imgs: visited_imgs[bucket] = set()
        if objectKey in visited_imgs[bucket]: continue 
        visited_imgs[bucket].add(objectKey)
        labels = res["labels"] if "labels" in res else [] # error hanlder for results that not include labels?
        imgUrl = "https://%s.s3.amazonaws.com/%s" % (bucket, objectKey)
        photo = {
            "url": imgUrl,
            "labels": labels
        }
        # photo model to modify
        '''
        {
  "type" : "object",
  "properties" : {
    "url" : {
      "type" : "string"
    },
    "labels" : {
      "type" : "array",
      "items" : {
        "type" : "string"
      }
    }
  }
}
        '''
        imgs.append(photo)
    return imgs

def error_response(error_code):
    body ={
        "message": "execution error. check the input parameters of query."
    }
    response = {
        "statusCode": error_code,
        "headers":{
            'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*',
            'Content-Type': 'application/json'
        },
        "body": json.dumps(body)
    }
    return response
    
def lambda_handler(event, context):
    if "queryStringParameters" not in event:
        return error_response(500)
    q_paras = event["queryStringParameters"]
    if "q" not in q_paras: return error_response(500)
    q = q_paras["q"]
    print("[INFO] -- Will going to search: ", q)
    
    client = boto3.client('lex-runtime',
                      region_name='us-east-1',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
                      
    try:
        response = client.post_text(
        botName= BOT_NAME,
        botAlias='demo',
        userId='userTest111',
        inputText= q)
    except e:
        print(e)
        return
    print(response)
    if "slots" not in response: return []
    qa, qb = response["slots"]["qa"], response["slots"]["qb"]
    if not qa and not qb: return []
    
    
    # query for all results
    # response = requests.get(es_url + index_name + '/_doc/_search?pretty')
    # print(response.json())
    
    # reference for the url
    # imgUrl = "https://%s.s3.amazonaws.com/%s" % (photo_info["bucket_name"], photo_info["objectKey"])
    res = []
    if qa:
        imgs_a = search_in_es(qa)
        print(imgs_a)
        res.extend(imgs_a)
 
    body = {"results":res}
    response = {
        "statusCode": 200,
        "headers":{
            'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*',
            'Content-Type': 'application/json'
        },
        "body": json.dumps(body)
    }
    #response = json.dumps(response)
    return response
