import requests
from requests.auth import HTTPBasicAuth

# Your WordPress site and credentials
wordpress_url = "https://growprogramming.com"
username = 'your_username'
password = 'your_password'

# The data for your new post
post = {
    'title': 'My Awesome Blog Post',
    'status': 'draft',  # 'draft' if you don't want to publish it immediately
    'content': 'This is the content of my awesome blog post',
}

# Endpoint for creating a new post
endpoint = wordpress_url + '/wp-json/wp/v2/posts'

# Make the POST request
response = requests.post(endpoint, auth=HTTPBasicAuth(username, password), json=post)

# Check the response
if response.status_code == 201:
    print("Post created successfully: " + response.json()['link'])
else:
    print("Failed to create post: " + response.text)
