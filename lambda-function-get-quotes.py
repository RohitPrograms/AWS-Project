import json
import boto3
import requests
import datetime

secret_name = "schwab-api-tokens"
secret_region = "us-east-1"

session = boto3.session.Session()
SM_client = session.client(
    service_name = 'secretsmanager',
    region_name = secret_region
)

def futures_symbol_builder(futures_symbols):

    futures_dict = {
        1 : 'F',
        2 : 'G',
        3 : 'H',
        4 : 'J',
        5 : 'K',
        6 : 'M',
        7 : 'N',
        8 : 'Q',
        9 : 'U',
        10 : 'V',
        11 : 'X',
        12 : 'Z'
    }

    current_date = datetime.datetime.today()
    current_month = current_date.month
    current_year = current_date.year

    futures_string = ""
    for futures_symbol in futures_symbols:
        for i in range(1,13):
            if i > current_month:
                futures_string += futures_symbol + futures_dict[i] + str(current_year)[-2:] + ","
            else:
                futures_string += futures_symbol + futures_dict[i] + str(current_year + 1)[-2:] + ","
    
    return futures_string[:-1]

symbols = futures_symbol_builder(['/CL', '/NG'])

def lambda_handler(event, context):

    # Get Secret
    get_secret_value_response = SM_client.get_secret_value(
        SecretId = secret_name
    )

    # ['SecretString'] contains the actual dict of key value pairs.
    secret_string = get_secret_value_response['SecretString']
    secret_string = secret_string.replace("'", '"')
    tokens = json.loads(secret_string)

    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    # Access API data
    base_url = f"https://api.schwabapi.com/marketdata/v1/quotes"
    
    params = {
        'symbols': symbols,
        'fields': 'quote',
        'indicative': 'false'
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    PassFail = 'Fail'
    data = None
    max_retries = 3
    attempt = 0

    while attempt < max_retries:  
        
        try:
            response = requests.get(base_url, headers = headers, params = params)

            if response.text.strip() == "":
                print('Access Token Expired. Use Refresh Token')
                break

            else:
                data = response.json()
                PassFail = 'Pass'
                break

        except requests.exceptions.HTTPError as http_err:
            attempt += 1
            print(f"HTTP error occurred. Status Code: {response.status_code}, Error: {http_err}")


        except requests.exceptions.RequestException as req_err:
            attempt += 1
            print(f"Request error occurred. Error: {req_err}")
    
    return {
        'statusCode': 200,
        'body': {'PassFail': PassFail, 'data': data}
    }