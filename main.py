#!/usr/bin/env python3
import openai_api
import argparse

wordpress_url = ""


def main():
    parser = argparse.ArgumentParser(
        description="BLOGO a CLI Tool to turn your Topical Authority SEO maps into fully written articles that are uploaded to your site",
        epilog="Example usage: main.py topical_authority_map.csv https://wordpress-site.com",
        formatter_class=argparse.HelpFormatter
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input file or parameter\n'
    )
    parser.add_argument(
        'url',
        type=str,
        help='URL of your WordPress site\n'
    )
    parser.add_argument(
        '-n', '--numimages',
        type=int,
        choices=[0, 1, 2, 3],
        default=2,
        help='1 generated image per 0, 1, 2, or 3 <h2> headings.\n'
    )
    parser.add_argument(
        '-s', '--status',
        type=str,
        choices=['draft', 'publish', 'future'],
        default='draft',
        help='Status of blog post upon upload.\n'
    )
    parser.add_argument(
        '-g', '--gpt',
        type=str,
        choices=['gpt-3.5-turbo-1106', 'gpt-4-1106-preview'],
        help='''Choose what GPT Model to use. Defaults -> outline=gpt-4-1106-preview
                                                       and content_writer=gpt-3.5-turbo-1106\n'''
    )
    parser.add_argument(
        '-o', '--output',
        action='store_true',
        help='Enabling local .md output file in the blog_posts dir\n'
    )

    args = parser.parse_args()

    config = {}

    config['input_file'] = args.input_file
    config['url'] = args.url
    config['numimages'] = args.numimages
    config['status'] = args.status
    config['gpt'] = args.gpt
    config['output'] = args.output
    config['time'] = None

    # Upload your files
    example_post_file_id = openai_api.upload_file(
        'assistant_files/example_blog.md',
        'assistants'
    )

    outline_file_id = openai_api.upload_file(
        'assistant_files/outline.md',
        'assistants'
    )

    model = "gpt-4-1106-preview"
    if config['gpt']:
        model = config['gpt']

    # Create an Assistant
    outline_assistant = openai_api.client.beta.assistants.create(
        name="Content Creation Assistant",
        model=f"{model}",
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
        model=f"{model}",
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
        config
    )


if __name__ == "__main__":
    main()
