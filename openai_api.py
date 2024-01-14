import time
import csv
import requests
import os
import openai
from tqdm import tqdm

# Initialize the OpenAI client
client = openai.OpenAI()


# Function to upload a file to OpenAI
def upload_file(file_path, purpose):
    with open(file_path, "rb") as file:
        response = client.files.create(file=file, purpose=purpose)
    return response.id


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
        time.sleep(0.5)
    raise TimeoutError("Run did not complete within the specified timeout.")


# TODO: is this even needed??? for right now lets just keep it
def get_internal_links(thread_id, blog_post_idea, assistant_id):
    # Generate outline
    get_request = f'''
    Choose 7 internal links for {blog_post_idea} from internallinks.txt. For
    example for blogs about coding languages choose python, C++, and Rust blog
    posts and for blogs post about career help provide resume, interview prep,
    and job information links
    '''
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=get_request
    )
    get_request = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    wait_for_run_completion(thread_id, get_request.id)
    # Retrieve outline from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    get_request = next(
        (m.content for m in messages.data if m.role == "assistant"),
        None
    )


# Blog Post Writer
def process_blog_post(thread_id, blog_post_idea, assistant_id):
    # Generate outline
    outline_request = f'''
    use the internal links from {get_internal_links} and
    use them to create an outline for an article about {blog_post_idea}.
    '''
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=outline_request
    )
    outline_run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    wait_for_run_completion(thread_id, outline_run.id)
    # Retrieve outline from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    outline = next(
        (m.content for m in messages.data if m.role == "assistant"),
        None
    )
    message_json = messages.model_dump()
    response = message_json['data'][0]['content'][0]['text']['value']
    outline = response
    # Initialize article variable
    article = None

    # Generate article
    if outline:
        article_request = f'''
        Write a detailed article based on the following outline:\n{outline} use
        markdown formatting and ensure to use tables and lists to add to
        formatting. Use 7 relevant internal links maximum
        '''
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=article_request
        )
        article_run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id)
        wait_for_run_completion(thread_id, article_run.id)
        # Retrieve article from the thread
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        article = next(
            (m.content for m in messages.data if m.role == "assistant"),
            None
        )
        message_json = messages.model_dump()
        response = message_json['data'][0]['content'][0]['text']['value']
        article = response
    return outline, article


# Takes your TA map csv and writes to another csv
def process_content_plan(assistant):
    input_file = 'Topical_Authority_Map_Programming_Careers.csv'
    output_file = 'processed_content_plan.csv'
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
                assistant.id
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
def create_image(prompt, image_size="1024x1024"):
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
        res_json = response.json().get('data')[0].get('url')
        return res_json
    else:
        raise Exception("Failed to create image: " + response.text)
