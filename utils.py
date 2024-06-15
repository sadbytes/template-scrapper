from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from os import listdir

def get_page(url):
    """ Returns the HTML data of the URL
    It checks if a cache is available in '/cache' directory, if no cache is found
    then it retrives the page, saves it in '/cache' and finally returns the HTML
    """
    subdomain = urlparse(url).hostname.split('.')[0]
    if subdomain in listdir('cache'):
        with open('cache/{}'.format(subdomain), 'r') as f:
            html_data = f.read()
    else:
        res = requests.get(url=url)
        html_data = res.text
        with open('cache/{}'.format(subdomain), 'w') as f:
            f.write(html_data)
    return html_data

def get_urls(url):
    html_data = get_page(url)
    soup = BeautifulSoup(html_data, 'html.parser')
    links = []
    print(soup.a)
    # print(soup.find_all('a'))
    for a in soup.find_all('a'):
        link = a.get('href')
        if link and link not in links:
            links.append(link.get('href'))
    return links



if __name__=='__main__':
    url="https://cimen-fluid-demo.squarespace.com/?nochrome=true/"
    print(get_urls(url))