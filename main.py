#!/usr/bin/env python3
import openai_api
import argparse

wordpress_url = ""


def main():
    parser = argparse.ArgumentParser(description="BLOGO csv2wordpress")
    parser.add_argument('input', help='Input file or parameter')
    parser.add_argument('-u', '--url', help='URL of the WordPress site')
    args = parser.parse_args()

    wordpress_url = args.url

    # Upload your files
    example_post_file_id = openai_api.upload_file(
        'assistant_files/example_blog.md',
        'assistants'
    )

    outline_file_id = openai_api.upload_file(
        'assistant_files/outline.md',
        'assistants'
    )

    # Create an Assistant
    outline_assistant = openai_api.client.beta.assistants.create(
        name="Content Creation Assistant",
        model="gpt-4-1106-preview",
        instructions='''
            Read outline.md - You will be given a blog post idea,
            then you will write an Outline to a blog post about the topic.
            There should be 5-7 'h2' or '##' headers, include a Frequently
            Asked Questions section at the end of the outline.
        ''',
        tools=[{"type": "retrieval"}],
    )
    openai_api.add_file_to_asssistant(
        outline_file_id,
        outline_assistant.id
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
            each 'h2' or '##' section "<Insert Picture Here>", if there are no
            more headers from the outline, write "<blog_post_done>"
        ''',
        tools=[{"type": "retrieval"}],
    )

    openai_api.add_file_to_asssistant(
        example_post_file_id,
        content_writer_assistant.id
    )

    # Your main logic here
    openai_api.process_content_plan(
        outline_assistant,
        content_writer_assistant,
        args.input,
        wordpress_url
    )


if __name__ == "__main__":
    main()
