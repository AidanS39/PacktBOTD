#!/bin/bash

BUCKET_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 20 | head -n 1)

BUCKET_NAME="packtbotd-cftemplates-$BUCKET_ID"
echo $BUCKET_NAME

aws s3 mb s3://$BUCKET_NAME
aws s3 ls
aws s3 rb s3://$BUCKET_NAME
aws s3 ls
