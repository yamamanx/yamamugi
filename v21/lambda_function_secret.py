import boto3
import base64
import json
import pymysql
from botocore.exceptions import ClientError


def get_secret():
    secret_name = "demo/aurora"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

    except ClientError as e:
        print(e.response['Error']['Code'])
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])

        return secret


def lambda_handler(event, context):

    secret_dict = json.loads(get_secret())
    print(secret_dict['password'])  # デモ用につき本番環境ではやっちゃだめ
    connection = pymysql.connect(
        host=secret_dict['host'],
        user=secret_dict['username'],
        password=secret_dict['password'],
        db='demo',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user"
            cursor.execute(sql)
            dbdata = cursor.fetchall()
            for rows in dbdata:
                print(rows)
    finally:
        connection.close()
