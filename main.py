import openai
import time
import csv
from tqdm import tqdm

# Initialize the OpenAI client
client = openai.OpenAI()


# Function to upload a file to OpenAI
def upload_file(file_path, purpose):
    with open(file_path, "rb") as file:
        response = client.files.create(file=file, purpose=purpose)
    return response.id


# Upload your files
internal_links_file_id = upload_file(
    'internallinks.txt',
    'assistants'
)
content_plan_file_id = upload_file(
    'Topical_Authority_Map_Programming_Careers.csv',
    'assistants'
)


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


def get_internal_links(thread_id, blog_post_idea):
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
        assistant_id=assistant.id
    )
    wait_for_run_completion(thread_id, get_request.id)
    # Retrieve outline from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    get_request = next(
        (m.content for m in messages.data if m.role == "assistant"),
        None
    )


def process_blog_post(thread_id, blog_post_idea):
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
        assistant_id=assistant.id
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
            assistant_id=assistant.id)
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


def process_content_plan():
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
            outline, article = process_blog_post(thread_id, blog_post_idea)

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

# Example usage
process_content_plan()
