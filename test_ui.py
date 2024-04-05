import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

class SitemapGenerator:
    def __init__(self):
        self.visited = set()
        self.sitemap = {}
        self.page_count = 0
        self.link_count = 1

    def get_internal_links(self, url, domain):
        internal_links = set()
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href.startswith('/') or href.startswith(domain):
                internal_links.add(urljoin(url, href))
        
        return internal_links

    def calculate_priority(self, url, link, domain):
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

    def crawl(self, url, domain):
        self.page_count += 1
        print(f"{self.page_count} pages found")
        self.visited.add(url)
        
        internal_links = self.get_internal_links(url, domain)
        self.sitemap[url] = internal_links
        
        for link in internal_links.copy():
            if link in self.visited or "setCurrencyId" in link:
                self.sitemap[url].remove(link)
        
        if len(self.sitemap[url]):
            for link in self.sitemap[url]:
                self.link_count += len(self.sitemap[url])
                print(f"{self.link_count} links found")
                self.crawl(link, domain)

    def generate_sitemap(self, domain):
        self.crawl(domain, domain)
        return self.sitemap

    def generate_sitemap_desktop(self, entry):
        domain = entry.get()
        sitemap = self.generate_sitemap(domain)
        
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        url_element = ET.SubElement(root, "url")
        
        loc_element = ET.SubElement(url_element, "loc")
        loc_element.text = domain
        
        lastmod_element = ET.SubElement(url_element, "lastmod")
        lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
        
        priority_element = ET.SubElement(url_element, "priority")
        priority_element.text = '1.0'
        
        for page, links in sorted(sitemap.items(), key=lambda x: max((self.calculate_priority(x[0], link, domain) for link in x[1]), default=0), reverse=True):
            for link in links:
                url_element = ET.SubElement(root, "url")
                
                loc_element = ET.SubElement(url_element, "loc")
                loc_element.text = link
                
                lastmod_element = ET.SubElement(url_element, "lastmod")
                lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
                
                priority_element = ET.SubElement(url_element, "priority")
                priority_element.text = str(self.calculate_priority(page, link, domain))
        
        tree = ET.ElementTree(root)
        file_name = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if file_name:
            tree.write(file_name, encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("Sitemap Generated", f"Sitemap saved to {file_name}")

# Create a Tkinter window
root = tk.Tk()
root.title("Sitemap Generator")

# Add a label and entry for domain input
tk.Label(root, text="Enter Domain:").pack()
entry = tk.Entry(root)
entry.pack()

# Create an instance of the SitemapGenerator class
generator = SitemapGenerator()

# Add a button to trigger sitemap generation
generate_button = tk.Button(root, text="Generate Sitemap", command=lambda: generator.generate_sitemap_desktop(entry))
generate_button.pack()

root.mainloop()