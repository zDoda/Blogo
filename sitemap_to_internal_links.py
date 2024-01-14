import xml.etree.ElementTree as ET
import requests


def get_internal_links_from_sitemap(sitemap_url, base_domain):
    # Fetch the sitemap content
    response = requests.get(sitemap_url)
    sitemap_content = response.text
    sitemap_schema_url = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    # Parse the XML content
    root = ET.fromstring(sitemap_content)

    # Extract and filter internal URLs
    internal_links = []
    schema_url = root.findall(
        f'.//{{{sitemap_schema_url}}}url'
    )
    for url in schema_url:
        loc = url.find(f'{{{sitemap_schema_url}}}loc').text
        if base_domain in loc and len(loc) > 45:
            internal_links.append(loc)
    return internal_links


internal_links = get_internal_links_from_sitemap(
    'https://www.growprogramming.com/sitemap.xml',
    'growprogramming.com')

for link in internal_links:
    print(link)
