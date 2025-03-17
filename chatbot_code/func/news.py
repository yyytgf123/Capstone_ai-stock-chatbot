from bs4 import BeautifulSoup
from flask import Flask
import urllib
import boto3
import os

def get_urls(target_url):
    html = urllib.request.urlopen(target_url).read()
    soup = BeautifulSoup(html, 'html.parser')    
    return soup

def extract_Data(soup):
    table = soup.find_all('div', 'article_view')
    return table