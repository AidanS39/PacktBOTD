# PacktBOTD
Serverless Notification Application for Packt's Book of the Day using AWS Resources and Python. \
\
NOTICE: I am still working on making this project easily deployable. This is a learning experience for me!

### Summary

Packt Book of the Day is a serverless notification application that notifies users via email of Packt's featured free eBooks, which can be found here:

https://www.packtpub.com/free-learning/

The featured free eBook that Packt offers changes every 24 hours. At a high level, PacktBOTD uses AWS serverless resources to every 24 hours, identify the name of the book and then email users of the new featured book.

### Architecture

![Architecture Diagram](https://github.com/AidanS39/PacktBOTD/blob/main/PacktBOTD_ArchitectureDrawing.png?raw=true)

The application uses Amazon EventBridge, AWS Lambda, and Amazon Simple Notification Service, as shown above in the diagram. The EventBridge event *PacktLambdaTimer* is a timed event that triggers the Lambda function *notifyOfPacktFreeBook* every 24 hours. *PacktLambdaTimer* uses the cron notation `cron(10 4 * * ? *)`, which sets a timer for the event to trigger the lambda function at 12:10 AM ET every day.

The lambda function *notifyOfPacktFreeBook* runs a python script that uses the modules boto3 - the Python SDK for AWS, and requests - "an elegant and simple HTTP library". The script uses requests to parse the HTML of `https://www.packtpub.com/free-learning/`. The script then extracts the name of the free eBook from the parsed HTML. Finally extracting the name, the script uses boto3 to programmatically publish an SNS message to the SNS Topic *PacktBOTDNotification*, which notifies the topic's subscribers via email of the name of the newly featured eBook.

Currently, the subscribers of the SNS topic *PacktBOTDNotification* are manually added to the SNS topic through the AWS console. However, a programmatic solution can be easily implemented in the case of users subscribing through the topic through a website or application.
