from bs4 import BeautifulSoup, SoupStrainer
import requests
from urllib.parse import urlparse
from os import listdir


def get_page(url):
    """ Returns the HTML data of the URL
    It checks if a cache is available in '/cache' directory, if no cache is found
    then it retrives the page, saves it in '/cache' and finally returns the HTML
    """
    subdomain = urlparse(url).hostname.split('.')[0]
    if "{}.html".format(subdomain) in listdir('cache'):
        with open('cache/{}.html'.format(subdomain), 'r') as f:
            html_data = f.read()
    else:
        res = requests.get(url=url)
        html_data = res.text
        with open('cache/{}.html'.format(subdomain), 'w') as f:
            f.write(html_data)
    return html_data

def get_urls(base_url):
    html_data = get_page(base_url)
    base_url_hostname = urlparse(base_url).hostname
    soup = BeautifulSoup(html_data, features='lxml', parse_only=SoupStrainer('a'))
    links = []
    for link in soup.find_all('a', href=True):
        url = link['href']
        if (url not in links 
            and urlparse(url).path 
            and urlparse(url).hostname in [None, base_url_hostname]
            ):
            links.append(url)
    return links
    



if __name__=='__main__':
    url="https://cimen-fluid-demo.squarespace.com/?nochrome=true/"
    get_urls(url)