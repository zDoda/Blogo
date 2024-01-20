import openai_api
import uuid

# Upload your files
internal_links_file_id = openai_api.upload_file(
    'assistant_files/internallinks.txt',
    'assistants'
)

example_post_file_id = openai_api.upload_file(
    'assistant_files/example_blog.md',
    'assistants'
)

outline_file_id = openai_api.upload_file(
    'assistant_files/outline.md',
    'assistants'
)

# content_plan_file_id = openai_api.upload_file(
#     'Topical_Authority_Map_Programming_Careers.csv',
#     'assistants'
# )

# Create an Assistant
internal_links_assistant = openai_api.client.beta.assistants.create(
    name="Internal Links Assistant",
    model="gpt-4-1106-preview",
    instructions='''
        Read internallinks.txt - You always choose 7-10 strictly relevant
        internal links to the blog idea given by user. For example
        for blogs about coding languages choose python, C++, and Rust blog
        posts and for blogs post about career help provide resume,
        interview prep, and job information links.
    ''',
    tools=[{"type": "retrieval"}],
)

openai_api.add_file_to_asssistant(
    internal_links_file_id,
    internal_links_assistant.id
)

outline_assistant = openai_api.client.beta.assistants.create(
    name="Content Creation Assistant",
    model="gpt-4-1106-preview",
    instructions='''
        Read outline.md - You will be given a blog post idea,
        then you will write an Outline to a blog post about the topic.
        There should be 5-7 'h2' or '##' headers, include a Frequently Asked
        Questions section at the end of the outline.
    ''',
    tools=[{"type": "retrieval"}],
)

content_writer_assistant = openai_api.client.beta.assistants.create(
    name="Content Creation Assistant",
    model="gpt-3.5-turbo-1106",
    instructions='''
        You are a Software Engineer blog writer, you talk about many topics
        in software engineering. Be opinionated, concise, and descriptive.
        Read example_blog.md - Using that as a guideline, you will recieve
        a blog outline and internal links that are relevant to that topic.
        Write one section at a time. Include a key concepts table at the
        beginning of the blog after a short interduction paragraph, Before
        each 'h2' or '##' section "<Insert Picture Here>", if there are no more
        headers from the outline, write "<blog_post_done>"
    ''',
    tools=[{"type": "retrieval"}],
)

openai_api.add_file_to_asssistant(
    example_post_file_id,
    content_writer_assistant.id
)

# thread_id = openai_api.client.beta.threads.create().id
# outline, article = openai_api.process_blog_post(
#     thread_id,
#     "How to get started in AI/ML programming",
#     outline_assistant.id,
#     content_writer_assistant.id,
#     internal_links_assistant.id
# )
#
# unique_id = uuid.uuid4()
# with open(f'./blog_posts/{unique_id}_blog_post.md', 'w') as file:
#     file.write(f'Outline:\n{outline}\n\nArticle:\n{article}')

# print(create_image('create a comicbook picture of a guy coding'))
openai_api.process_content_plan(
    internal_links_assistant,
    outline_assistant,
    content_writer_assistant
)
