import boto3
import botocore
import json
import os
import botocore.exceptions

with open('cleanup.json', 'r') as cleanup_json:
    resources = json.load(cleanup_json)

if 'ruleName' in resources.keys() and 'targetId' in resources.keys():
    events = boto3.client('events')
    events.remove_targets(
        Rule = resources['ruleName'],
        Ids = [resources['targetId']]
    )

if 'functionArn' in resources.keys():
    try:
        lambdaclient = boto3.client('lambda')
        lambdaclient.delete_function(
            FunctionName = resources['functionArn']
        )
    except:
        pass

if 'ruleName' in resources.keys():
    events = boto3.client('events')
    events.delete_rule(
        Name = resources['ruleName']
    )

if 'layerArn' in resources.keys() and 'layerVersion' in resources.keys():
    lambdaclient = boto3.client('lambda')
    lambdaclient.delete_layer_version(
        LayerName = resources['layerArn'],
        VersionNumber = resources['layerVersion']
    )

if 'roleName' in resources.keys():
    iam = boto3.client('iam')
    if 'policyName' in resources.keys():
        iam.delete_role_policy(
            RoleName = resources['roleName'],
            PolicyName = resources['policyName']
        )
    iam.delete_role(
        RoleName = resources['roleName']
    )

if 'topicArn' in resources.keys():
    sns = boto3.client('sns')
    sns.delete_topic(
        TopicArn = resources['topicArn']
    )
    if 'topicSubscribers' in resources.keys():
        for subscriber in resources['topicSubscribers']:
            sns.unsubscribe(
                SubscriptionArn = subscriber
            )

def delete_folder_contents(folder):
    with os.scandir(folder) as directory:
        for file in directory:
            if file.is_dir():
                delete_folder_contents(file.path)
                os.rmdir(file.path)
            elif file.is_file():
                os.remove(file.path)

delete_folder_contents('python')
os.rmdir('python')
os.remove('layer_content.zip')
os.remove('lambda_function.py')
os.remove('lambda_function.zip')
os.remove('cleanup.json')

print(resources.keys())
        
