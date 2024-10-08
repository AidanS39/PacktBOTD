rm -rf python

pip3 install --target ./python/lib/python3.12/site-packages/ -r requirements.txt

zip -r layer_content.zip ./python
