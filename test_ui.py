import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
import requests, os
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import sys

sys.setrecursionlimit(999999999)

class StatusBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.page_count_label = tk.Label(self, text="Page Count: 0")
        self.page_count_label.pack(side=tk.LEFT)

        self.link_count_label = tk.Label(self, text="Link Count: 0")
        self.link_count_label.pack(side=tk.RIGHT)

class SitemapGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.visited = set()
        self.sitemap = {}
        self.page_count = 0
        self.link_count = 1
        self.count = 0
        
        self.title("Sitemap Gen")
        label_frame0 = LabelFrame(self, text="Enter Your Domain:", height=50, width=230)
        label_frame0.place(x=15,y=10)

        self.entry = tk.Entry(self, bd=1)
        self.entry.insert(0, "https://www.blisscomputers.net/")
        self.entry.place(x=30,y=30,width=200)

        self.generate_button = tk.Button(self, text="Generate", command=self.generate_sitemap_desktop)
        self.generate_button.place(x=20, y=150, width=100)
        
        self.close_button = tk.Button(self, text="Close", command=self.clickExitButton)
        self.close_button.place(x=140, y=150, width=100)
        
        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status_bar()
        
        
        self.geometry("300x200")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_cordinate = int((screen_width / 2) - (260 / 2))
        y_cordinate = int((screen_height / 2) - 200)

        self.geometry("{}x{}+{}+{}".format(260, 200, x_cordinate, y_cordinate))

    def update_status_bar(self):
        self.status_bar.page_count_label.config(text=f"Page Count: {self.page_count}")
        self.status_bar.link_count_label.config(text=f"Link Count: {self.link_count}")

    def get_internal_links(self, url, domain):
        internal_links = set()
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href.startswith('/') or href.startswith(domain):
                if "setCurrencyId" not in href and "image" not in href:
                    internal_links.add(urljoin(url, href))
        
        return internal_links

    def calculate_priority(self, url, link, domain):
        keys_list = list(self.sitemap.keys())
        
        if keys_list[url] == domain:
            return 0.9
        elif "page" in link:
            return 0.6
        elif keys_list[url] not in link:
            return 0.5
        elif link.count('/') > 4:
            return 0.8
        else:
            return 0.7

    def crawl(self, url, domain):
        self.page_count += 1
        print(f"{self.page_count} pages found")
        self.visited.add(url)
        
        if self.count >= 10:  # Check if we have crawled 100 links
            return
        
        internal_links = self.get_internal_links(url, domain)
        internal_links = list(set(internal_links))
        self.sitemap[url] = internal_links
        sitemap_items = list(self.sitemap.items())
        
        for link in internal_links:
            if link in self.visited:
                self.sitemap[url] = [item for item in self.sitemap[url] if item != link]
                
            for index, (key, value) in enumerate(sitemap_items[:-1]):  # Exclude the last sitemap item
                if isinstance(value, list) and link in value:
                    self.sitemap[url] = [item for item in self.sitemap[url] if item != link]
        
        if len(self.sitemap[url]):
            for link in self.sitemap[url]:
                self.link_count += len(self.sitemap[url])
                print(f"{self.link_count} links found")
                self.count += 1  # Increment the counter after crawling a new link
                self.crawl(link, domain)

    def crawl_url(self, index, domain):
        internal_links = set()
        self.page_count += 1
        print(f"{self.page_count} page found")
        
        if self.count >= 10:  # Check if we have crawled 100 links
            return
        
        for crawling_link in self.sitemap[index]:
            for internal_link in self.get_internal_links(crawling_link, domain):
                if internal_link not in self.visited:
                    internal_links.add(internal_link)
                    
        internal_links = list(set(internal_links))
        if len(internal_links):
            self.sitemap[index + 1] = internal_links
            self.link_count += len(internal_links)
            print(f"{self.link_count} links found")
            for internal_link in internal_links:
                self.crawl_url(internal_link, domain)

    def generate_sitemap(self, domain):
        self.sitemap[0].add(domain)
        self.crawl_url(0, domain)
        return self.sitemap

    def generate_sitemap_desktop(self):
        domain = self.entry.get()
        sitemap = self.generate_sitemap(domain)
        
        links_per_file = 50
        sitemap_links = [link for page, links in sitemap.items() for link in links]
        sitemap_chunks = [sitemap_links[i:i + links_per_file] for i in range(0, len(sitemap_links), links_per_file)]
        print(len(sitemap_links))
        for index, chunk in enumerate(sitemap_chunks):
            root = ET.Element("urlset")
            root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
            
            # Add the specified item at the beginning of the first file
            if index == 0:
                url_element = ET.SubElement(root, "url")
                
                loc_element = ET.SubElement(url_element, "loc")
                loc_element.text = domain
                
                lastmod_element = ET.SubElement(url_element, "lastmod")
                lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
                
                priority_element = ET.SubElement(url_element, "priority")
                priority_element.text = '1.0'
            
            for link in chunk:
                url_element = ET.SubElement(root, "url")
                
                loc_element = ET.SubElement(url_element, "loc")
                loc_element.text = link
                
                lastmod_element = ET.SubElement(url_element, "lastmod")
                lastmod_element.text = datetime.now().strftime("%Y-%m-%d")
                
                priority_element = ET.SubElement(url_element, "priority")
                priority_element.text = str(self.calculate_priority(index, link, domain))
            
            tree = ET.ElementTree(root)
            folder_name = f'sitemap_{datetime.now().strftime("%Y-%m-%d")}'
            os.makedirs(folder_name, exist_ok=True)
            
            if index == 0:
                file_name = os.path.join(folder_name, "sitemap.xml")
            else:
                file_name = os.path.join(folder_name, f"sitemap{index}.xml")
            
            if file_name:
                tree.write(file_name, encoding="utf-8", xml_declaration=True)
        
        messagebox.showinfo("Sitemaps Generated", f"Sitemaps split and saved in the folder: {folder_name}")
    
    def clickExitButton(self):
        exit()

app = SitemapGeneratorApp()
app.mainloop()