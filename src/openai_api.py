import csv
import time
import requests
import os
import openai
import io
import uuid
import random
from src import wordpress
import markdown
from PIL import Image
from tqdm import tqdm

# Initialize the OpenAI client
client = openai.OpenAI()

art_styles = [
    "Comic book",
    "Anime",
    "Minimalism",
    "Futurism",
    "Steampunk",
    "Watercolor",
    "Pastel",
    "Manga",
]


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
            image.save(f'output_files/{unique_id}.webp')
        else:
            print("Failed to create image: " + response.text)

        return os.path.abspath(f'output_files/{unique_id}.webp')
    else:
        print("Failed to create image: " + response.text)


def chat_completion(prompt: str, config) -> str:
    model = "gpt-3.5-turbo-1106"
    if config['gpt']:
        model = config['gpt']
    try:
        completion = client.chat.completions.create(
            model=f"{model}",
            messages=[
                {"role": "system", "content": 'You are a helpful assistant'},
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def image_gen(blog_post_idea, config):
    image_prompt_prompt = f'''
    Write a image prompt that relates with {blog_post_idea}, has
    a {random.choice(art_styles)}
    '''
    image_prompt = chat_completion(image_prompt_prompt, config)
    image_src = create_image(image_prompt)
    return image_src


# Vector Store
def create_vector_store(vs_name):
    return client.beta.vector_stores.create(name=vs_name).id

# Function to upload a file to OpenAI
def upload_file(file_path, purpose):
    with open(file_path, "rb") as file:
        response = client.files.create(file=file, purpose=purpose)
    return response.id


def add_file_to_vs(file_id, vs_id):
    client.beta.vector_stores.files.create(
      vector_store_id=vs_id,
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


def check_headers(article):
    h2_indexes = find_substring_indexes(article, "## ")
    for idx in h2_indexes:
        if article[idx-1] != '\n' and article[idx-1] != '#':
            article = article[:idx] + '\n\n' + article[idx:]
    h3_indexes = find_substring_indexes(article, "### ")
    for idx in h3_indexes:
        if article[idx-1] != '\n' and article[idx-1] != '#':
            article = article[:idx] + '\n\n' + article[idx:]
    return article


# Checks to see if an OpenAI thread run is in the "completed" status
def wait_for_run_completion(thread_id, run_id, timeout=900):
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


# Blog Post Writer
def process_blog_post(thread_id, blog_post_idea, outline_id, writer_id, slug, config):
    # Generate outline
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
    featured_image = ""
    featured_id = 0

    # Generate article
    if outline:
        article = ""
        indexes = find_substring_indexes(outline, "\n## ")
        headers = list_headers(indexes, outline)
        for header_idx, header in enumerate(tqdm(headers, desc=f"Writing Headers for '{blog_post_idea}'")):
            article_request = f'''
            Write a detailed section for the header '{header}' in the outline:
            \n{outline}. use markdown formatting.
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

            # Parsing out gpt comments below
            idx = para.find("---")
            para = para[:idx]

            image_id = 0
            image_src = ""
            if header_idx == 0:
                image_src = image_gen(blog_post_idea, config)
                featured_image, featured_id = wordpress.image_to_wordpress(image_src, config['url'])
            elif header_idx % config['numimages'] == 0:
                image_src = image_gen(blog_post_idea, config)
                hosted_src, image_id = wordpress.image_to_wordpress(image_src, config['url'])
                para = f"\n![{blog_post_idea}-{uuid.uuid4()}]({hosted_src})\n{para}"

            article += para

    # Getting data for post
    title_request = f'''
    Give the Title description for an article using the info below.\n
    Blog Idea: {blog_post_idea}\n Outline:\n{outline}.\n
    The Title under 59 chars",
    Example Titles:
    Software Engineers with ADHD: Thriving in the Tech Industry
    Break Into Tech w/ an Associate’s Degree in Computer Science
    Software Engineer Locations: Top Cities for Tech Jobs in 2024
    Respond with just the title. No quotation marks.
    '''
    meta_request = f'''
    Give theMeta description for an article using the info below.\n
    Blog Idea: {blog_post_idea}\n Outline:\n{outline}.\n
    The meta description that is under 160 chars
    Example Meta Descriptions:
    As a software engineer with ADHD, you know that your job requires intense
    focus, attention to detail, and the ability to manage complex tasks.
    Respond with just the meta description. No quatation marks.
    '''

    # Fixing GPT header bugs
    article = check_headers(article)
    html = markdown.markdown(article)

    # Retrieve article from the thread
    meta_str = chat_completion(meta_request, config)
    title_str = chat_completion(title_request, config)
    with open(f'blog_posts/{title_str}.html', 'w') as file:
        file.write(html)

    # Upload to Wordpress
    config['time'] = wordpress.wp_create_post(
        html,
        title_str,
        slug,
        meta_str,
        featured_id,
        config
    )

    return outline, article, config


# Takes your TA map csv and writes to another csv
def process_content_plan(outline_ass, writer_ass, config):
    input_file = os.path.abspath(config['input_file'])

    # Create a single thread for processing the content plan
    thread_id = client.beta.threads.create().id

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in tqdm(reader, desc="Processing Blog Posts"):
            blog_post_idea = row['Topic']
            outline, article, config = process_blog_post(
                thread_id,
                blog_post_idea,
                outline_ass.id,
                writer_ass.id,
                row['Slug'],
                config
            )
