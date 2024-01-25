import requests
import os
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import pytz

# Your WordPress site and credentials
username = os.environ.get('WP_USER_NAME')
password = os.environ.get('WP_PASS_WORD')


def wp_create_post(article, title, slug, meta, image_src, config):
    # The data for your new post
    if config['status']:
        if config['time'] is None:
            future_date = datetime.now(pytz.utc) + timedelta(hours=1)
        else:
            future_date = config['time']

        future_date_iso = future_date.isoformat()
        post = {
            'title': title,
            'status': config['status'],
            'content': article,
            'featured_media': image_src,
            'slug': slug, 'meta': {
                'aioseop_meta_description': meta
            },
            'author': 1,
            'excerpt': meta,
            'date_gmt': future_date_iso
        }
    else:
        post = {
            'title': title,
            'status': config['status'],
            'content': article,
            'featured_media': image_src,
            'slug': slug, 'meta': {
                'aioseop_meta_description': meta
            },
            'author': 1,
            'excerpt': meta
        }

    # Endpoint for creating a new post
    endpoint = config['url'] + '/wp-json/wp/v2/posts'

    # Make the POST request
    response = requests.post(endpoint, auth=HTTPBasicAuth(username, password), json=post)

    # Check the response
    if response.status_code == 201:
        print("Post created successfully: " + response.json()['link'])
        return future_date + timedelta(hours=1)
    else:
        print("Failed to create post: " + response.text)


def image_to_wordpress(image_src, wp_url):
    # Headers for the image upload
    if image_src:
        image_name = image_src.split('/')[-1]
        headers = {
            "Content-Disposition": f"attachment; filename={image_name}",
            "Content-Type": "image/webp",
        }

        # Read the image binary
        if image_src != "":
            with open(image_src, "rb") as image:
                image_content = image.read()

        # Upload the image
        upload_response = requests.post(
            f"{wp_url}/wp-json/wp/v2/media",
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
            return f'{wp_url}/wp-content/uploads/{date_year}/{date_month}/{image_name}', upload_response.json()["id"]
        else:
            print("Failed to upload image.")
            print("Status Code:", upload_response.status_code)
            print("Response:", upload_response.text)
    else:
        return "", 0


# image_to_wordpress('./output_files/ee2abfb6-01d1-4ddf-a3ef-415193ffc5ce.webp')
