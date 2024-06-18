from bs4 import BeautifulSoup, SoupStrainer
import requests
from urllib.parse import urlparse
from os import listdir

__all__ = ['get_page', 'get_urls']

def get_page(url):
    """ Returns the HTML data of the URL
    It checks if a cache is available in '/cache' directory, if no cache is found
    then it retrives the page, saves it in '/cache' and finally returns the HTML
    """
    parsed_url = urlparse(url)
    file_name = parsed_url.hostname + '-'.join(parsed_url.path.split('/')) + '.html'
    if "{}".format(file_name) in listdir('cache'):
        with open(f'cache/{file_name}', 'r') as f:
            html_data = f.read()
    else:
        res = requests.get(url=url)
        html_data = res.text
        with open(f'cache/{file_name}', 'w') as f:
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
    get_urls('https://www.wix.com/demone2/website-under-constr')
