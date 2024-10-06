import requests
import base64
import pprint as pp
import boto3
import json


def authenticate():

    # Your key and secret here
    appKey = "key"
    appSecret = "secret"
    
    # Authenticate to get redirect link
    authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={appKey}&redirect_uri=https://127.0.0.1'
    print(f"Click to authenticate: {authUrl}")

    # ridirect link has code
    returnedLink = input("Paste the redirect URL here:")
    code = f"{returnedLink[returnedLink.index('code=')+5:returnedLink.index('%40')]}@"

    headers = {
        'Authorization': f'Basic {base64.b64encode(bytes(f"{appKey}:{appSecret}", "utf-8")).decode("utf-8")}', # Authenticates the client (you obviously) 
        'Content-Type': 'application/x-www-form-urlencoded' # specifies the type of data that is being sent through a POST request.
    }

    # code is used to get tokens. POST means you're sending data to a server. So we want to send our code
    data = {
        'grant_type': 'authorization_code', # standard value on OAuth2.0 to get tokens
        'code': code, # the auth code that you received after the user authenticated and granted your application permissions.
        'redirect_uri': 'https://127.0.0.1'
    }

    max_retries = 3
    attempt = 0

    while attempt < max_retries:  
        try:
            response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers = headers, data = data)
            fetch_tokens = response.json()

            SM_client = boto3.client(
                'secretsmanager',
                region_name='us-east-1',
                aws_access_key_id = "access_key_id",
                aws_secret_access_key = "secret_access_key"
            )

            # Get Secret
            get_secret_value_response = SM_client.get_secret_value(
                SecretId = "schwab-api-tokens"
            )

            # ['SecretString'] contains the actual dict of key value pairs.
            secret_string = get_secret_value_response['SecretString']
            secret_string = secret_string.replace("'", '"')
            tokens = json.loads(secret_string)

            tokens['access_token'] = fetch_tokens['access_token']
            tokens['refresh_token'] = fetch_tokens['refresh_token']

            response = SM_client.put_secret_value(
                SecretId = "schwab-api-tokens",
                SecretString = json.dumps(tokens)
            )
            break

        except requests.exceptions.HTTPError as http_err:
            attempt += 1
            if attempt == max_retries:
                print(print(f"HTTP error occurred. Status Code: {response.status_code}, Error: {http_err}"))

        except requests.exceptions.RequestException as req_err:
            attempt += 1
            if attempt == max_retries:
                print(f"Request error occurred. Error: {req_err}")
    

authenticate()