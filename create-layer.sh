#!/bin/bash

rm -rf package

pip3 install --target ./package/python/lib/python3.12/site-packages/ -r requirements.txt

zip -r layer_content.zip ./package/python

LAYER_VERSION_ARN="$(aws lambda publish-layer-version \
       	--layer-name "requests-python-module" \
       	--description "python requests module and dependencies" \
       	--compatible-runtimes "python3.12" \
       	--zip-file "fileb://layer_content.zip" \
	--output json \
	--query 'LayerVersionArn')"

echo "Layer: $LAYER_VERSION_ARN"
