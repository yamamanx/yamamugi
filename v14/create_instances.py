import boto3

ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-048f6ed62451373d9',
    InstanceType='t2.micro',
    TagSpecifications=[
        {
            'ResourceType':'instance',
            'Tags':[
                {
                    'Key':'Name',
                    'Value':'SDK'
                }
            ]
        }
    ],
    MaxCount=1,
    MinCount=1,
)