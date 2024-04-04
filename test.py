import requests
from bs4 import BeautifulSoup

urls = []
def get_urls_from_domain(domain):
    global urls
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sub_urls = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if url and url.startswith(domain) and url not in urls:
            print(url)
            sub_urls.append(url)
            urls.append(url)
    if len(sub_urls):
        for sub_url in sub_urls:
            get_urls_from_domain(sub_url)
    return urls

def generate_sitemap(domain):
    urls = get_urls_from_domain(domain)
    
    with open('sitemap.xml', 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        
        for url in urls:
            f.write(f'\t<url>\n\t\t<loc>{url}</loc>\n\t</url>\n')
        
        f.write('</urlset>')

# Example usage
generate_sitemap('https://translate.google.com/')