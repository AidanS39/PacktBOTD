#!/bin/bash

TOPIC_ARN="$(aws sns create-topic \
	--name "PacktBOTDNotification" \
	--output text \
	--query 'TopicArn')"

cp PacktBOTDAllowPublish.json PacktBOTDAllowPublish_filled.json
sed -i "s/SNS_ARN/$TOPIC_ARN/g" PacktBOTDAllowPublish_filled.json

# echo "$TOPIC_ARN" >> topic_arn.txt

#aws sns delete-topic \
#	--topic-arn "$TOPIC_ARN"

echo -e "Please enter an email address that will recieve the notification.\n\n "
 
read -p "Email Address: " EMAIL

while [ "$EMAIL" != "stop" ]
do
	SUBSCRIPTION_ARN="$(aws sns subscribe \
		--topic-arn "$TOPIC_ARN" \
		--protocol "email" \
		--notification-endpoint "$EMAIL" \
		--return-subscription-arn \
		--output text \
		--query 'SubscriptionArn')"

	echo "$SUBSCRIPTION_ARN" >> subscription_arns.txt

	echo -e "(Optional) Enter additional email addresses. Enter \"stop\" to stop."
	read -p "Email Address: " EMAIL
done

