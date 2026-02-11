import xml.etree.ElementTree as ET
import requests

class SitemapScraper:
    def parse_sitemap(self, sitemap_url):
        try:
            response = requests.get(sitemap_url, timeout=30)
            root = ET.fromstring(response.content)
            
            urls = []
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                urls.append(url.text)
            
            return urls
        except Exception as e:
            return []
