import json
import requests
import base64
import boto3

secret_name = "schwab-api-tokens"
secret_region = "us-east-1"

session = boto3.session.Session()
SM_client = session.client(
    service_name = 'secretsmanager',
    region_name = secret_region
)

def lambda_handler(event, context):
    
    # Get Secret
    get_secret_value_response = SM_client.get_secret_value(
        SecretId = secret_name
    )

    # ['SecretString'] contains the actual dict of key value pairs.
    secret_string = get_secret_value_response['SecretString']
    secret_string = secret_string.replace("'", '"')
    tokens = json.loads(secret_string)
    
    # getting current token values
    current_access_token = tokens['access_token']
    current_refresh_token = tokens['refresh_token']

    # To Do: Put this into secrets manager
    appKey = "your app key"
    appSecret = "your app secret"
 
    # TO DO: get refresh token here
 
    refresh_headers = {
        'Authorization': f'Basic {base64.b64encode(bytes(f"{appKey}:{appSecret}", "utf-8")).decode("utf-8")}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
 
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': current_refresh_token
    }
 
    max_retries = 3
    attempt = 0
 
    while attempt < max_retries:  
        try:
            response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers = refresh_headers, data = refresh_data)
            data = response.json()
            
            # Refresh token doesn't change, but good practice still.
            tokens['access_token'] = data['access_token']
            tokens['refresh_token'] = data['refresh_token']
            
            # Put new token values into Secrets Manager
            response = SM_client.put_secret_value(
                SecretId = "schwab-api-tokens",
                SecretString = json.dumps(tokens)
            )
            
            return {
                'statusCode': 200,
                'body': {'PassFail': 'Pass'}
            }
 
        except requests.exceptions.HTTPError as http_err:
            attempt += 1
            print(f"HTTP error occurred. Status Code: {response.status_code}, Error: {http_err}")
 
        except requests.exceptions.RequestException as req_err:
            attempt += 1
            print(f"Request error occurred. Error: {req_err}")
    
    return {
        'statusCode': 200,
        'body': {'PassFail': 'Fail'}
    }