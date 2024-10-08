import boto3
import json
import zipfile



def createSNSTopic(name):
    
    sns = boto3.client('sns')
    snsResponse = sns.create_topic(
        Name = name
    )
    return snsResponse



def createSNSSubscribers(topicArn):
    
    print("Please enter an email address that will recieve the notification. Enter \"stop\" to stop.")
    email = input('Email Address: ')
    
    subscriptionArns = []

    while email != 'stop':
        snsReponse = sns.subscribe(
            TopicArn = topicArn,
            Protocol = 'email',
            Endpoint = email,
            ReturnSubscriptionArn = True
        )
        subscription.append(snsResponse['SubscriptionArn'])

        print("(Optional) enter additional email addresses. Enter \"stop\" to stop.")
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

    iamResponse = iam.create_role(
        RoleName = 'PacktBOTDNotification-AllowPublishRole',
        AssumeRolePolicyDocument = json.dumps(lambdaAssumeRolePolicyDocument),
        Description = 'Role for PacktBOTD function to allow publishing a message from sns topic',
    )
    return iamResponse



def attachAllowPublishPolicy(topicArn):
    
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

    iamPolicyResponse = iam.put_role_policy(
        RoleName = roleName,
        PolicyName = 'PacktBOTDAllowPublish',
        PolicyDocument = json.dumps(allowPublishPolicy)
    )
    return iamPolicyResponse



def publishRequestsLayer():

    lambdaclient = boto3.client('lambda')

    layerResponse = lambdaclient.publish_layer_version(
        LayerName = 'python-requests-module',
        Description = 'Layer for Requests python module',
        Content = {
            'ZipFile': open('layer_content.zip', 'rb').read()
        },
        CompatibleRuntimes = ['python3.12']
    )
    return layerResponse



def createFunction(layerVersionArn, roleArn, topicArn):
    
    lines = []

    with open('lambda_function.py', 'r') as function:
        for line in function:
            if 'TOPIC_ARN' in line:
                changed_line = line.replace('TOPIC_ARN',topicArn)
                lines.append(changed_line)
            else:
                lines.append(line)

    with open('lambda_function.py', 'w') as function:
        for line in lines:
            function.write(line)

    zipfile.ZipFile('lambda_function.zip',mode='w').write('lambda_function.py')

    lambdaclient = boto3.client('lambda')

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

    ruleResponse = events.put_rule(
        Name = ruleName,
        Description = 'Timer that invokes notifyOfPacktFreeBook lambda function at specified time',
        ScheduleExpression = 'cron(' + minutes + ' ' + hours + ' * * ? *)'
    )
    return ruleResponse

def addPermissionsForScheduler(functionArn, ruleArn):

    lambdaclient = boto3.client('lambda')

    permissionResponse = lambdaclient.add_permission(
        FunctionName = functionArn,
        StatementId = '1',
        Action = 'lambda:InvokeFunction',
        Principal = 'events.amazonaws.com',
        SourceArn = ruleArn
    )

    return permissionResponse

def putLambdaAsSchedulerTarget(functionArn, ruleName):

    events = boto3.client('events')

    targetResponse = events.put_targets(
        Rule = ruleName,
        Targets = [
            {
                'Id': '1',
                'Arn': functionArn
            }
        ]
    )
    return targetResponse



# MAIN ---------------------------------------------------

# Create SNS Topic
topicName = 'PacktBOTDNotification'
snsResponse = createSNSTopic(topicName)
topicArn = snsResponse['TopicArn']

# Add Subscribers to SNS Topic
createSNSSubscribers(topicArn)

# Create IAM Role for Function
iamRoleResponse = createAllowPublishRole()
roleName = iamRoleResponse['Role']['RoleName']
roleArn = iamRoleResponse['Role']['Arn']

# Attach policy to IAM role
attachAllowPublishPolicy(topicArn) 

# Publish Requests Layer
layerResponse = publishRequestsLayer()
layerVersionArn = layerResponse['LayerVersionArn']

# Create Scheduler
ruleName = 'PacktLambdaTimer'
ruleResponse = createSchedulerRule(ruleName)
ruleArn = ruleResponse['RuleArn']

# Create Function
functionResponse = createFunction(layerVersionArn,roleArn,topicArn)
functionArn = functionResponse['FunctionArn']

# Add Permissions to Lambda for Scheduler
addPermissionsForScheduler(functionArn, ruleArn)

# Put Lambda as Scheduler's Target
putLambdaAsSchedulerTarget(functionArn, ruleName)


