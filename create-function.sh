#!/bin/bash

# CREATE ROLES FOR LAMBDA TO PUBLISH SNS ---------------------------------

echo "creating policies"

ROLE_NAME="PacktBOTDNotification-AllowPublishRole"

ROLE_ARN="$(aws iam create-role \
	--role-name "$ROLE_NAME" \
	--assume-role-policy-document "file://AssumeRolePolicyDocument.json" \
	--output text \
	--query 'Role.Arn' )"

echo "$ROLE_ARN"

sleep 5

POLICY_NAME="PacktBOTDAllowPublish"

aws iam put-role-policy \
	--role-name "$ROLE_NAME" \
	--policy-name "$POLICY_NAME" \
	--policy-document "file://PacktBOTDAllowPublish_filled.json"

# CREATE LAYER -----------------------------------------------------------------

echo "creating requests layer"

rm -rf package

pip3 install --target ./python/lib/python3.12/site-packages/ -r requirements.txt

zip -r layer_content.zip ./python

LAYER_VERSION_ARN="$(aws lambda publish-layer-version \
       	--layer-name "requests-python-module" \
       	--description "python requests module and dependencies" \
       	--compatible-runtimes "python3.12" \
       	--zip-file "fileb://layer_content.zip" \
	--output text \
	--query 'LayerVersionArn')"

# CREATE FUNCTION --------------------------------------------------------------

echo "creating function"

FUNCTION_ARN="$(aws lambda create-function \
	--function-name "notifyOfPacktFreeBook" \
	--description "function to send message to PacktBOTD Notification SNS topic" \
	--runtime "python3.12" \
	--architectures "arm64" \
	--zip-file "fileb://lambda_function.zip" \
	--handler "lambda_function.lambda_handler" \
	--layers "$LAYER_VERSION_ARN" \
	--role "$ROLE_ARN" \
	--output text \
	--query 'FunctionArn' )"


# CREATE SCHEDULER AND ROLES ---------------------------------------------------

echo "creating scheduler"

SCHEDULER_RULE_NAME="PacktLambdaTimer"

SCHEDULER_RULE_ARN="$(aws events put-rule \
	--name "$SCHEDULER_RULE_NAME" \
	--schedule-expression "cron(10 4 * * ? *)" \
	--output text \
	--query 'RuleArn')"

aws lambda add-permission \
	--function-name "$FUNCTION_ARN" \
	--statement-id "1" \
	--action "lambda:InvokeFunction" \
	--principal "events.amazonaws.com" \
	--source-arn "$SCHEDULER_RULE_ARN"

aws events put-targets \
	--rule "$SCHEDULER_RULE_NAME" \
	--targets Id="1",Arn="$FUNCTION_ARN"

# CLEAN UP RESOURCES -----------------------------------------------------------

read -p "Press any key to clean up resources..."  -n 1 -s

LAYER_VERSION_NUMBER="$(aws lambda get-layer-version-by-arn \
	--arn "$LAYER_VERSION_ARN" \
	--output text \
	--query 'Version')"

aws lambda delete-layer-version \
	--layer-name "requests-python-module" \
	--version-number "$LAYER_VERSION_NUMBER"

aws lambda delete-function \
	--function-name "$FUNCTION_ARN"

echo "Deleted function and requents"

aws iam delete-role-policy \
	--role-name "$ROLE_NAME" \
	--policy-name "$POLICY_NAME" 

aws iam delete-role \
	--role-name "$ROLE_NAME"

echo "Deleted function role and policies"

aws events remove-targets \
	--rule "$SCHEDULER_RULE_NAME" \
	--ids "1"

aws events delete-rule \
	--name "$SCHEDULER_RULE_NAME"

echo "Deleted scheduler"

bash cleanup.sh

