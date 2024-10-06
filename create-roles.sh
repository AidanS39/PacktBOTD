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

