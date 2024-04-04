import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

priority = 1.0

def get_internal_links(url):
    internal_links = set()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('/') or url in href:
            internal_links.add(urljoin(url, href))
    
    return internal_links

def generate_sitemap(domain):
    visited = set()
    sitemap = {}
    
    def crawl(url, priority):
        if url in visited:
            return
        
        print(url, priority)
        visited.add(url)
        internal_links = get_internal_links(url)
        sitemap[url] = internal_links
        
        for link in internal_links:
            if link not in visited:
                if priority > 0:
                    new_priority = max(priority - 0.1, 0.9)
                else:
                    new_priority = -0.1
                
                crawl(link, new_priority)
    
    crawl(domain, priority)
    
    return sitemap

def calculate_priority(url, domain):
    if url == domain:
        return 1.0
    elif domain in url:
        depth = url[len(domain):].count('/') + 1
        return max(0.9 - 0.1 * (depth - 1), 0.1)
    else:
        return -0.1

domain = 'https://www.blisscomputers.net/'
sitemap = generate_sitemap(domain)

root = ET.Element("urlset")
root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

url_element = ET.SubElement(root, "url")

loc_element = ET.SubElement(url_element, "loc")
loc_element.text = domain

lastmod_element = ET.SubElement(url_element, "lastmod")
lastmod_element.text = datetime.now().strftime("%Y-%m-%d")

priority_element = ET.SubElement(url_element, "priority")
priority_element.text = '1.0'

for page, links in sitemap.items():
    for link in links:
        url_element = ET.SubElement(root, "url")
        
        loc_element = ET.SubElement(url_element, "loc")
        loc_element.text = link
        
        lastmod_element = ET.SubElement(url_element, "lastmod")
        lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
        
        priority = calculate_priority(page, domain)
        priority_element = ET.SubElement(url_element, "priority")
        priority_element.text = str(priority)

tree = ET.ElementTree(root)
tree.write(f'sitemap_{datetime.now().strftime("%Y-%m-%d")}.xml', encoding="utf-8", xml_declaration=True)