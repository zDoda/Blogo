import requests
import os
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Your WordPress site and credentials
wordpress_url = "https://growprogramming.com"
username = os.environ.get('WP_USER_NAME')
password = os.environ.get('WP_PASS_WORD')


def wp_create_post(article, title, slug, meta, image_src):
    # The data for your new post
    post = {
        'title': title,
        'status': 'draft',
        'content': article,
        'featured_media': image_src,
        'slug': slug,
        'meta': {
            'aioseop_meta_description': meta
        }
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


def image_to_wordpress(image_src):
    # Headers for the image upload
    image_name = image_src.split('/')[-1]
    headers = {
        "Content-Disposition": f"attachment; filename={image_name}",
        "Content-Type": "image/webp",  # Change according to your image type (e.g., image/png)
    }

    # Read the image binary
    with open(image_src, "rb") as image:
        image_content = image.read()

    # Upload the image
    upload_response = requests.post(
        f"{wordpress_url}/wp-json/wp/v2/media",
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        data=image_content
    )
    current_date = datetime.now()
    date_year = current_date.year
    date_month = current_date.month
    if date_month < 10:
        date_month = f'0{date_month}'
    # Check if upload was successful
    if upload_response.status_code == 201:
        print(f'CUSTOM: growprogramming.com/wp-content/uploads/{date_year}/{date_month}/{image_name}')
        return f'https://growprogramming.com/wp-content/uploads/{date_year}/{date_month}/{image_name}'
    else:
        print("Failed to upload image.")
        print("Status Code:", upload_response.status_code)
        print("Response:", upload_response.text)


# image_to_wordpress('./output_files/ee2abfb6-01d1-4ddf-a3ef-415193ffc5ce.webp')
