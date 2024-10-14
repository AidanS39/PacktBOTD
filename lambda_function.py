import json
import boto3
import requests

def lambda_handler(event, context):
    
    page = requests.get("https://www.packtpub.com/free-learning")
    html = page.text
    encoded_html = html.encode(page.encoding)
    
    book = html[html.index('product-info__title') + 34:]
    book = book[0: book.index('</h3>')]
    sns = boto3.client("sns")
    
    sns.publish(
        TopicArn = "arn:aws:sns:us-east-1:654654278162:PacktBOTDNotification",
        Subject = "ALERT: NEW FREE BOOK OF THE DAY",
        Message = book + " is today\'s Packt Book of the Day! \n\nGet it here:\n https://www.packtpub.com/free-learning"
        )
    
    
    return {
        'statusCode': 200,
        'body': book
    }
