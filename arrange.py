import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('sitemap_2024-04-05.xml')
root = tree.getroot()

# Extract the url elements and their priority values
urls = root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
urls.sort(key=lambda x: float(x.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority').text), reverse=True)

# Reconstruct the sorted XML structure
root[:] = urls

# Output the sorted XML
tree.write('sorted_xml_file.xml', encoding='utf-8')