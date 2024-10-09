# PacktBOTD
Serverless Notification Application for Packt's Book of the Day using AWS Resources and Python.

DISCLAIMER: I am still working on making this project easily deployable. This is a learning experience for me!

## Summary

Packt Book of the Day is a serverless notification application that notifies users via email of Packt's featured free eBooks, which can be found here:

https://www.packtpub.com/free-learning/

The featured free eBook that Packt offers changes every 24 hours. At a high level, PacktBOTD uses AWS serverless resources to every 24 hours, identify the name of the book and then email users of the new featured book.

## Usage

### Requirements

1. [Python](https://www.python.org/) (v3 or newer) - The application is deployed mainly by a python script.
   
2. Bash shell - The application requires users to run at least one bash script when deploying the application. \
   For Windows users, the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) can be used for accessing a bash shell.

3. [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) - The resources deployed require users to have an AWS account connected to the AWS CLI installed on their local machine.

### Deployment

1. Install [boto3](https://aws.amazon.com/sdk-for-python/) with pip using `pip install boto3` \
   More information on installing and configuring your AWS account with boto3 can be found here: \
   https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html

2. Create the requests layer with the `create_layer.sh` shell script provided by running `./create_layer.sh`
   
3. Run the `create_topic.py` python script with `python3 create_topic.py`. You will need to provide some input such as any email addresses you want to subscribe to the SNS topic, and the time you want the SNS topic to publish the Book of the Day message.

4. Currently, a solution is being created to clean up the AWS resources and files created. For now, AWS resources and files need to be cleaned up manually. This step will be updated once a solution has been created.

## Architecture

![Architecture Diagram](https://github.com/AidanS39/PacktBOTD/blob/main/PacktBOTD_ArchitectureDrawing.jpg?raw=true)

The application uses Amazon EventBridge, AWS Lambda, and Amazon Simple Notification Service, as shown above in the diagram. The EventBridge event *PacktLambdaTimer* is a timed event that triggers the Lambda function *notifyOfPacktFreeBook* every 24 hours. *PacktLambdaTimer* uses the cron notation `cron(10 4 * * ? *)`, which sets a timer for the event to trigger the lambda function at 12:10 AM ET every day.

The lambda function *notifyOfPacktFreeBook* runs a python script that uses the modules boto3 - the Python SDK for AWS, and requests - "an elegant and simple HTTP library". The script uses requests to parse the HTML of `https://www.packtpub.com/free-learning/`. The script then extracts the name of the free eBook from the parsed HTML. Finally extracting the name, the script uses boto3 to programmatically publish an SNS message to the SNS Topic *PacktBOTDNotification*, which notifies the topic's subscribers via email of the name of the newly featured eBook.
