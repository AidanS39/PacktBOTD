import boto3
import botocore
import json
import zipfile
import botocore.exceptions



def createSNSTopic(name):
    
    sns = boto3.client('sns')

    try:
        snsResponse = sns.create_topic(
            Name = name
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return snsResponse



def createSNSSubscribers(topicArn):
   
    print("Please enter an email address that will recieve the notification. Enter \"stop\" to stop.")
    email = input('Email Address: ')
    
    sns = boto3.client('sns')
    subscriptionArns = []

    while email != 'stop':
        try:
            snsResponse = sns.subscribe(
                TopicArn = topicArn,
                Protocol = 'email',
                Endpoint = email,
                ReturnSubscriptionArn = True
            )
            subscriptionArns.append(snsResponse['SubscriptionArn'])
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'InvalidParameter':
                print(f'{email} is not a valid email address.')
            else:
                raise error
        except Exception as exception:
            raise exception
            

        print("Enter another email address that will recieve the notification. Enter \"stop\" to stop.")
        email = input('Email Address: ')
    return subscriptionArns



def createAllowPublishRole():

    lambdaAssumeRolePolicyDocument = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    iam = boto3.client('iam')

    try:
        iamResponse = iam.create_role(
            RoleName = 'PacktBOTDNotification-AllowPublishRole',
            AssumeRolePolicyDocument = json.dumps(lambdaAssumeRolePolicyDocument),
            Description = 'Role for PacktBOTD function to allow publishing a message from sns topic',
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return iamResponse



def attachAllowPublishPolicy(topicArn, roleName):
    
    allowPublishPolicy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sns:Publish",
                "Resource": topicArn
            }
        ]
    }

    iam = boto3.client('iam')

    policyName = 'PacktBOTDAllowPublish'
    try:
        iamPolicyResponse = iam.put_role_policy(
            RoleName = roleName,
            PolicyName = policyName,
            PolicyDocument = json.dumps(allowPublishPolicy)
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return policyName



def publishRequestsLayer():

    lambdaclient = boto3.client('lambda')

    try:
        layerResponse = lambdaclient.publish_layer_version(
            LayerName = 'python-requests-module',
            Description = 'Layer for Requests python module',
            Content = {
                'ZipFile': open('layer_content.zip', 'rb').read()
            },
            CompatibleRuntimes = ['python3.12']
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return layerResponse



def createFunction(layerVersionArn, roleArn, topicArn):
    
    lines = []

    with open('function_not_filled.py', 'r') as function:
        for line in function:
            if 'TOPIC_ARN' in line:
                changed_line = line.replace('TOPIC_ARN',topicArn)
                lines.append(changed_line)
            else:
                lines.append(line)

    with open('lambda_function.py', 'w') as function:
        for line in lines:
            function.write(line)

    filename = 'lambda_function.zip'

    zipfile.ZipFile(filename,mode='w').write('lambda_function.py')

    lambdaclient = boto3.client('lambda')

    try:
        functionResponse = lambdaclient.create_function(
            FunctionName = 'notifyOfPacktFreeBook',
            Description = 'Function to send message to PacktBOTD Notification SNS topic',
            Runtime = 'python3.12',
            Architectures = ['arm64'],
            Handler = 'lambda_function.lambda_handler',
            Layers = [layerVersionArn],
            Role = roleArn,
            Timeout = 5,
            Code = {
                'ZipFile': open('lambda_function.zip', 'rb').read()
            }
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    except:
        print(f"Error: {filename} not found.")
    else:
        return functionResponse



def getHoursFromInput():
    while True:
        try:
            hours = int(input("Hours(0-23): "))
            if hours < 0 or hours > 23:
                print("That is not a valid hour.")
            else:
                return hours
        except:
            print("That is not a valid hour.")
        
def getMinutesFromInput():
    while True:
        try:
            minutes = int(input("Minutes (0-59): "))
            if minutes < 0 or minutes > 59:
                print("That is not a valid number of minutes.")
            else:
                return minutes
        except:
            print("That is not a valid number of minutes.")
        

def createSchedulerRule(ruleName):
    
    print("Please enter a time (in UTC) in which the notification will occur every day.")

    hours = str(getHoursFromInput())
    minutes = str(getMinutesFromInput())

    events = boto3.client('events')

    try:
        ruleResponse = events.put_rule(
            Name = ruleName,
            Description = 'Timer that invokes notifyOfPacktFreeBook lambda function at specified time',
            ScheduleExpression = 'cron(' + minutes + ' ' + hours + ' * * ? *)'
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return ruleResponse

def addPermissionsForScheduler(functionArn, ruleArn):

    lambdaclient = boto3.client('lambda')

    try:
        permissionResponse = lambdaclient.add_permission(
            FunctionName = functionArn,
            StatementId = '1',
            Action = 'lambda:InvokeFunction',
            Principal = 'events.amazonaws.com',
            SourceArn = ruleArn
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return permissionResponse

def putLambdaAsSchedulerTarget(functionArn, ruleName):

    events = boto3.client('events')

    targetId = '1'
    try:
        targetResponse = events.put_targets(
            Rule = ruleName,
            Targets = [
                {
                    'Id': targetId,
                    'Arn': functionArn
                }
            ]
        )
    except botocore.exceptions.ClientError as error:
        raise error
    except Exception as exception:
            raise exception
    else:
        return targetId

def writeCleanupJSON(json_file):
    with open('cleanup.json', 'w') as jsonfile:
        jsonfile.write(json_file)

# MAIN ---------------------------------------------------

def main():
    try:
        filename = 'layer_content.zip'
        content_layer = open(filename)
        content_layer.close()
    except:
        print(f"Error: {filename} not found. Please run 'create_layer.sh' before running 'create_topic.py'.")
        return -1

    cleanup_resources = dict()

    # Create SNS Topic
    topicName = 'PacktBOTDNotification'
    snsResponse = createSNSTopic(topicName)
    topicArn = snsResponse['TopicArn']

    cleanup_resources['topicArn'] = topicArn
    # Add Subscribers to SNS Topic
    subscribeResponse = createSNSSubscribers(topicArn)

    cleanup_resources['topicSubscribers'] = subscribeResponse

    # Create IAM Role for Function
    iamRoleResponse = createAllowPublishRole()
    roleName = iamRoleResponse['Role']['RoleName']
    roleArn = iamRoleResponse['Role']['Arn']

    cleanup_resources['roleArn'] = roleArn
    cleanup_resources['roleName'] = roleName
    # Attach policy to IAM role
    policyName = attachAllowPublishPolicy(topicArn, roleName) 
    
    cleanup_resources['policyName'] = policyName
    # Publish Requests Layer
    layerResponse = publishRequestsLayer()
    layerVersionArn = layerResponse['LayerVersionArn']
    layerArn = layerResponse['LayerArn']
    layerVersion = layerResponse['Version']

    cleanup_resources['layerVersionArn'] = layerVersionArn
    cleanup_resources['layerArn'] = layerArn
    cleanup_resources['layerVersion'] = layerVersion
    # Create Scheduler
    ruleName = 'PacktLambdaTimer'
    ruleResponse = createSchedulerRule(ruleName)
    ruleArn = ruleResponse['RuleArn']

    cleanup_resources['ruleArn'] = ruleArn
    cleanup_resources['ruleName'] = ruleName
    # Create Function
    functionResponse = createFunction(layerVersionArn,roleArn,topicArn)
    functionArn = functionResponse['FunctionArn']

    cleanup_resources['functionArn'] = functionArn
    # Add Permissions to Lambda for Scheduler
    addPermissionsForScheduler(functionArn, ruleArn)

    # Put Lambda as Scheduler's Target
    eventTargetResponse = putLambdaAsSchedulerTarget(functionArn, ruleName)
    
    cleanup_resources['targetId'] = eventTargetResponse
    #write cleanup resource dictionary to json file
    cleanup_json = json.dumps(cleanup_resources)
    writeCleanupJSON(cleanup_json)
        

main()


