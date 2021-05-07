import json
import boto3


def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    # TODO implement
    return {
        'statusCode': 200,
        'body': response
    }
