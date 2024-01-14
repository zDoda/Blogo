from openai_api import upload_file, process_content_plan, create_image, client

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

# Example usage
print(create_image(
        'comic book style, software engineer brainstorming ideas',
        '1792x1024'
    )
)
# process_content_plan(assistant)
