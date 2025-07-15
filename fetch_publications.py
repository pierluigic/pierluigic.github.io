import xml.etree.ElementTree as ET
import requests

# Function to fetch XML data from URL
def fetch_xml_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Function to parse XML and generate Markdown
def xml_to_markdown(xml_content):
    root = ET.fromstring(xml_content)
    markdown_output = """---
layout: page
title: Publications
permalink: /publications/
---\n\n"""

    for hit in root.findall('.//hit'):
        try:
            venue = hit.find('.//venue').text
    
            # Exclude arXiv (CoRR) publications
            if venue.lower() == 'corr':
                continue
    
            title = hit.find('.//title').text
            year = hit.find('.//year').text
            tp = hit.find('.//type').text
            authors = hit.findall('.//author')
            authors_list = ', '.join([f"**{author.text}**" if author.text == "Pierluigi Cassotti" else author.text for author in authors])
            url = hit.find('.//ee').text
    
            markdown_output += f"### [{title}]({url})\n"
            markdown_output += f"- **Year:** {year}\n"
            markdown_output += f"- **Authors:** {authors_list}\n"
            if tp == "Conference and Workshop Papers":
                markdown_output += f"- **Conference/Workshop:** {venue}\n\n"
            elif tp == "Journal Articles":
                markdown_output += f"- **Journal:** {venue}\n\n"
            else:
                markdown_output += f"\n\n"
        except:
            pass

    return markdown_output


# Automatically retrieve XML from DBLP URL
xml_url = 'https://dblp.org/search/publ/api?q=pierluigi%20cassotti&h=1000&format=xml'
xml_content = fetch_xml_from_url(xml_url)

markdown_result = xml_to_markdown(xml_content)

# Save Markdown to file
with open('publications.markdown', 'w', encoding='utf-8') as file:
    file.write(markdown_result)

