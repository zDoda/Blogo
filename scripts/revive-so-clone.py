import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import ollama
import os

# Replace these with your WordPress credentials and URL
wp_url = "https://growprogramming.com/wp-json/wp/v2"
wp_username = os.environ.get("WP_USER_NAME")
wp_password = os.environ.get("WP_PASS_WORD")

# Function to reword the first paragraph using ollama


def reword_paragraph(text):
    # Interact with ollama API
    result = ollama.generate(
        model='llama3.1',
        prompt=f'''Reword the following paragraph, make sure only 
        respond with new paragraph: \n {text}
        '''
    )
    return result['response']


# Retrieve all published posts
response = requests.get(
    f"{wp_url}/posts", auth=HTTPBasicAuth(wp_username, wp_password), params={'per_page': 100})
if response.status_code != 200:
    print(f"Failed to retrieve posts: {response.status_code}")
    exit(1)

all_posts = response.json()

# Iterate over each post and update it
for post in all_posts:
    post_id = post['id']
    post_content = post['content']['rendered']

    # Find the end of the first paragraph
    first_paragraph_end = post_content.find('</p>') + 4

    if first_paragraph_end > 0:
        first_paragraph = post_content[:first_paragraph_end]
        remaining_content = post_content[first_paragraph_end:]

        # Reword the first paragraph using ollama
        reworded_paragraph = reword_paragraph(first_paragraph)

        # Update post content
        new_content = reworded_paragraph + remaining_content

        # Prepare the data for the post update
        post_data = {
            'content': new_content,
            'date': datetime.now().isoformat(),
            'status': 'publish'
        }

        # Update the post via the REST API
        update_response = requests.post(f"{wp_url}/posts/{post_id}",
                                        auth=HTTPBasicAuth(
                                            wp_username, wp_password),
                                        json=post_data)

        if update_response.status_code == 200:
            print(f"Updated post ID: {post_id}")
        else:
            print(f"Failed to update post ID: {
                  post_id} - {update_response.text}")

print("All posts updated.")

