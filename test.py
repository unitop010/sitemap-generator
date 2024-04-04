import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

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
    visited = set(domain)
    sitemap = {}
    count = 0  # Initialize a counter to keep track of the number of links crawled
    
    def crawl(url, depth):
        nonlocal count  # Access the count variable from the outer function
        links_to_remove = []
        
        if count >= 10:  # Check if we have crawled 100 links
            return
        
        if url in visited and "setCurrencyId" in url:
            return
        
        visited.add(url)
        internal_links = get_internal_links(url)
        sitemap[depth] = internal_links
        
        for link in internal_links.copy():
            if link not in visited and "setCurrencyId" not in link:
                new_depth = depth - 0.1
                print(link, new_depth)
                crawl(link, new_depth)
                count += 1  # Increment the counter after crawling a new link
            else:
                links_to_remove.append(link)

        for link in links_to_remove:
            sitemap[depth].remove(link)
    
    crawl(domain, 1.0)
    
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

for depth, links in sitemap.items():
    for link in links:
        
        url_element = ET.SubElement(root, "url")
        
        loc_element = ET.SubElement(url_element, "loc")
        loc_element.text = link
        
        lastmod_element = ET.SubElement(url_element, "lastmod")
        lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
        
        priority_element = ET.SubElement(url_element, "priority")
        priority_element.text = str(depth - 0.1)

tree = ET.ElementTree(root)
tree.write(f'sitemap_{datetime.now().strftime("%Y-%m-%d")}.xml', encoding="utf-8", xml_declaration=True)