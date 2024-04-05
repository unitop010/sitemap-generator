import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

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
                internal_links.add(urljoin(url, href))
        
        return internal_links

    def calculate_priority(self, url, link, domain):
        if url == domain:
            return 0.9
        elif "page" in link:
            return 0.6
        elif url not in link:
            return 0.5
        elif link.count('/') > 4:
            return 0.8
        else:
            return 0.7

    def crawl(self, url, domain):
        self.page_count += 1
        # print(f"{self.page_count} pages found")
        self.visited.add(url)
        
        if self.count >= 10:  # Check if we have crawled 100 links
            return
        
        internal_links = self.get_internal_links(url, domain)
        self.sitemap[url] = internal_links
        internal_links = list(set(internal_links))
        sitemap_items = list(self.sitemap.items())
        
        for link in internal_links.copy():
            if link in self.visited or "setCurrencyId" in link or "image" in link:
                self.sitemap[url].remove(link)
                
            for index, (key, value) in enumerate(sitemap_items[:-1]):  # Exclude the last sitemap item
                if isinstance(value, set) and link in value:
                    print('removed')
                    # self.sitemap[url].remove(link)
                    self.sitemap[url] = [item for item in self.sitemap[url] if item != link]
        
        if len(self.sitemap[url]):
            for link in self.sitemap[url]:
                self.link_count += len(self.sitemap[url])
                # print(f"{self.link_count} links found")
                self.count += 1  # Increment the counter after crawling a new link
                self.crawl(link, domain)

    def generate_sitemap(self, domain):
        self.crawl(domain, domain)
        return self.sitemap

    def generate_sitemap_desktop(self):
        domain = self.entry.get()
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
    
    def clickExitButton(self):
        exit()

app = SitemapGeneratorApp()
app.mainloop()