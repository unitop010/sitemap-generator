import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import sys

sys.setrecursionlimit(999999999)

def get_internal_links(url):
    internal_links = set()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('/') or href.startswith(domain):
            if "setCurrencyId" not in href and "image" not in href:
                internal_links.add(urljoin(url, href))
    
    return internal_links

def calculate_priority(url, link):
    if url == domain:
        return 0.9
    elif url not in link:
        return 0.5
    elif "page" in link:
        return 0.6
    elif link.count('/') > 4:
        return 0.8
    else:
        return 0.7

def generate_sitemap(domain):
    visited = set()
    visited.add(domain)
    sitemap = {}
    count = 0  # Initialize a counter to keep track of the number of links crawled
    page_count = 0
    link_count = 1
    
    def crawl(url):
        nonlocal count  # Access the count variable from the outer function
        nonlocal page_count, link_count
        
        if count >= 10:  # Check if we have crawled 100 links
            return
        
        page_count += 1
        print(f"{page_count} pages found")
        visited.add(url)
        
        internal_links = get_internal_links(url)
        sitemap[url] = internal_links
        
        for link in internal_links.copy():
            if link in visited or "setCurrencyId" in link:
                sitemap[url].remove(link)
        
        if len(sitemap[url]):
            for link in sitemap[url]:
                link_count += len(sitemap[url])
                print(f"{link_count} links found")
                count = count + 1  # Increment the counter after crawling a new link
                crawl(link)
            
    crawl(domain)
    
    return sitemap

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

for page, links in sorted(sitemap.items(), key=lambda x: max((calculate_priority(x[0], link) for link in x[1]), default=0), reverse=True):
    for link in links:
        url_element = ET.SubElement(root, "url")
        
        loc_element = ET.SubElement(url_element, "loc")
        loc_element.text = link
        
        lastmod_element = ET.SubElement(url_element, "lastmod")
        lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
        
        priority_element = ET.SubElement(url_element, "priority")
        priority_element.text = str(calculate_priority(page, link))

tree = ET.ElementTree(root)
tree.write(f'sitemap_{datetime.now().strftime("%Y-%m-%d")}.xml', encoding="utf-8", xml_declaration=True)