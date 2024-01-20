import requests
from bs4 import BeautifulSoup
import html2text


def url_to_markdown(url):
    # Fetch the content from the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    main_content = soup.find('body')  # Adjust this line as needed

    # Convert to Markdown
    markdown = html2text.html2text(str(main_content))
    index = markdown.find("* * *")
    index2 = markdown.find("\n# ")
    return markdown[index2+1:index]


url = 'https://growprogramming.com/software-engineer-locations/'
markdown_content = url_to_markdown(url)
# print(markdown_content)
with open('example_blog.md', 'w') as file:
    file.write(markdown_content)
