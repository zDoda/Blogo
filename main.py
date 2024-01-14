from openai_api import upload_file, process_content_plan, create_image, client
from PIL import Image
import io
import requests
# Upload your files
internal_links_file_id = upload_file(
    'internallinks.txt',
    'assistants'
)

content_plan_file_id = upload_file(
    'Topical_Authority_Map_Programming_Careers.csv',
    'assistants'
)

# Create an Assistant
assistant = client.beta.assistants.create(
    name="Content Creation Assistant",
    model="gpt-3.5-turbo-1106",
    instructions='''
        Read internallinks.txt - You always choose 7 strictly
        relevant internal links. Then you create a detailed outline on the blog
        post topic, including a maximum of 7 HIGHLY relevant
        internal links. These will finally be used to write an article.
    ''',
    tools=[{"type": "retrieval"}],
)
response = requests.get(create_image(
    'comic book style, software engineer brainstorming ideas',
    '1792x1024'
))
# Example usage
image = Image.open(io.BytesIO(response.content))
image.save('./image.webp')
# process_content_plan(assistant)
