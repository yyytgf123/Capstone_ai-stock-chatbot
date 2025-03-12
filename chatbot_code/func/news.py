from bs4 import BeautifulSoup
from flask import Flask
import urllib
import boto3
import os

### bedrock setting ###
inferenceProfileArn= os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")
app = Flask(__name__)
bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")

#######################
def get_urls(target_url):
    html = urllib.request.urlopen(target_url).read()
    soup = BeautifulSoup(html, 'html.parser')    
    return soup

def extract_Data(soup):
    table = soup.find_all('div', 'article_view')
    return table