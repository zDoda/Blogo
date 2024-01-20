import time
import csv
import requests
import os
import openai
from PIL import Image
import io
import subprocess
import uuid
from tqdm import tqdm

# Initialize the OpenAI client
client = openai.OpenAI()


# Function to upload a file to OpenAI
def upload_file(file_path, purpose):
    with open(file_path, "rb") as file:
        response = client.files.create(file=file, purpose=purpose)
    return response.id


def add_file_to_asssistant(file_id, assistant_id):
    client.beta.assistants.files.create(
      assistant_id=assistant_id,
      file_id=file_id
    )


def find_substring_indexes(main_string, substring):
    return [i for i in range(len(main_string)) if main_string.startswith(substring, i)]


def list_headers(indexes, main_string):
    headers = []
    for idx in indexes:
        _temp = main_string[idx+1:].find("\n")
        headers.append(main_string[idx+1:_temp+(idx+1)])
    return headers


# Checks to see if an OpenAI thread run is in the "completed" status
def wait_for_run_completion(thread_id, run_id, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run_status.status == 'completed':
            return run_status
        time.sleep(10)
    raise TimeoutError("Run did not complete within the specified timeout.")


# def get_internal_links(thread_id, blog_post_idea, assistant_id):
#     # Generate outline
#     get_request = f'''
#     Choose internal links for {blog_post_idea} from internallinks.txt'''
#     client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=get_request
#     )
#     get_request = client.beta.threads.runs.create(
#         thread_id=thread_id,
#         assistant_id=assistant_id
#     )
#     wait_for_run_completion(thread_id, get_request.id)
#     # Retrieve outline from the thread
#     messages = client.beta.threads.messages.list(thread_id=thread_id)
#     message_json = messages.model_dump()
#     links = message_json['data'][0]['content'][0]['text']['value']
#     return links


# Blog Post Writer
def process_blog_post(thread_id, blog_post_idea, outline_id, writer_id, inter_id):
    # Generate outline
    # links = get_internal_links(thread_id, blog_post_idea, inter_id)
    outline_request = f'''
    Create an outline for an article about {blog_post_idea}.
    Outlines will have 1 'h1' or '#' header. Then write the Outline with the
    'h2' or '##' followed by 1-4 'h3' or '###' subheadings
    Example:# Title of blog.....\n\n## 1st h2\n\t### h3 subheading in the h2
    \n\t### another h3\n\n## 2nd h3\n\n and so on...
    '''
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=outline_request
    )
    print(f"Creating outline for {blog_post_idea}")
    outline_run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=outline_id
    )
    wait_for_run_completion(thread_id, outline_run.id)
    # Retrieve outline from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    message_json = messages.model_dump()
    outline = message_json['data'][0]['content'][0]['text']['value']
    # Initialize article variable
    article = None

    # Generate article
    if outline:
        article = ""
        indexes = find_substring_indexes(outline, "\n## ")
        headers = list_headers(indexes, outline)
        for header in tqdm(headers, desc=f"Writing Headers for '{blog_post_idea}'"):
            article_request = f'''
            Write a detailed section for the header '{header}' in the outline:
            \n{outline}. use markdown formatting and ensure to use tables and
            lists to add to formatting.
            '''
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=article_request
            )
            article_run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=writer_id
            )
            wait_for_run_completion(thread_id, article_run.id)
            # Retrieve article from the thread
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            message_json = messages.model_dump()
            para = message_json['data'][0]['content'][0]['text']['value']
            idx = para.find("---")
            para = para[:idx]
            article += para
    return outline, article


# Takes your TA map csv and writes to another csv
def process_content_plan(internal_links_ass, outline_ass, writer_ass):
    input_file = 'assistant_files/Topical_Authority_Map_Programming_Careers.csv'
    output_file = 'output_files/processed_content_plan.csv'
    processed_rows = []

    # Create a single thread for processing the content plan
    thread_id = client.beta.threads.create().id

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in tqdm(reader, desc="Processing Blog Posts"):
            if row.get('Processed', 'No') == 'Yes':
                continue

            blog_post_idea = row['Topic']
            outline, article = process_blog_post(
                thread_id,
                blog_post_idea,
                outline_ass.id,
                writer_ass.id,
                internal_links_ass.id
            )
            if outline and article:
                row.update({
                    'Blog Outline': outline,
                    'Article': article,
                    'Processed': 'Yes'
                })
                processed_rows.append(row)

    # Write the processed rows to the output file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=processed_rows[0].keys())
        writer.writeheader()
        writer.writerows(processed_rows)


# TODO: Use Dalle to create an image
def create_image(prompt, image_size="1792x1024"):
    """
    Create an image using DALL-E 3 API.

    :param prompt: The description of the image to be created.
    :param api_key: The API key for authenticating with the DALL-E 3 service.
    :param image_size: The size of the image. Default is "1024x1024".
    :return: The URL of the created image.
    """
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
    }
    data = {
        "prompt": prompt,
        "model": "dall-e-3",
        "size": image_size,
        "style": "natural"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        res_url = response.json().get('data')[0].get('url')
        response = requests.get(res_url)

        if response.status_code == 200:
            unique_id = uuid.uuid4()
            image = Image.open(io.BytesIO(response.content))
            image.save(f'./{unique_id}.png')
            subprocess.run(f'cwebp {unique_id}.png -o output_files/{unique_id}.webp', shell=True)
            subprocess.run(f'rm {unique_id}.png', shell=True)
        else:
            raise Exception("Failed to create image: " + response.text)

        return os.path.abspath('output_files/{unique_id}.webp')
    else:
        raise Exception("Failed to create image: " + response.text)
