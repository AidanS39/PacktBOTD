#!/bin/bash


ROLE_NAME="PacktBOTDNotification-AllowPublishRole"

ROLE_ARN="$(aws iam create-role \
	--role-name "$ROLE_NAME" \
	--assume-role-policy-document "file://AssumeRolePolicyDocument.json" \
	--output text \
	--query 'Role.Arn' )"

	echo "$ROLE_ARN"
	   
aws iam put-role-policy \
	--role-name "$ROLE_NAME" \
	--policy-name "PacktBOTDAllowPublish" \
	--policy-document "file://PacktBOTDAllowPublish_filled.json"

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

echo "Layer: $LAYER_VERSION_ARN"

aws lambda create-function \
	--function-name "notifyOfPacktFreeBook" \
	--description "function to send message to PacktBOTD Notification SNS topic" \
	--runtime "python3.12" \
	--architectures "arm64" \
	--zip-file "fileb://lambda_function.zip" \
	--handler "lambda_function.lambda_handler" \
	--layers "$LAYER_VERSION_ARN" \
	--role "$ROLE_ARN"
