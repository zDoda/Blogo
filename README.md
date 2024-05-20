# BLOGO - Assistant Autoblogger
Provide a csv and BLOGO parses, writes, and uploads article to wordpress with images!

## Why?
I have many clients from freelance Web/SEO, wanting a cheap content so their websites to start indexing for keywords

## Quick start
```bash
pip install -r requirements.txt
```
### How to use
```bash
usage: main.py [-h] [-n {0,1,2,3}] [-s {draft,publish,future}] [-g {gpt-3.5-turbo-1106,gpt-4-1106-preview}] [-o] input_file url

BLOGO a CLI Tool to turn your Topical Authority SEO maps into fully written articles that are uploaded to your site

positional arguments:
  input_file            Input file or parameter
  url                   URL of your WordPress site

optional arguments:
  -h, --help            show this help message and exit
  -n {0,1,2,3}, --numimages {0,1,2,3}
                        1 generated image per 0, 1, 2, or 3 <h2> headings.
  -s {draft,publish,future}, --status {draft,publish,future}
                        Status of blog post upon upload.
  -g {gpt-3.5-turbo-1106,gpt-4-1106-preview}, --gpt {gpt-3.5-turbo-1106,gpt-4-1106-preview}
                        Choose what GPT Model to use. Defaults -> outline=gpt-4-1106-preview and content_writer=gpt-3.5-turbo-1106
  -o, --output          Enabling local .md output file in the blog_posts dir

Example usage: main.py topical_authority_map.csv https://wordpress-site.com
```

## *Content Pipeline*
This is the process for creating one article (Articles are going to be written in parallel)

User input(csv)->Research Agent->Outline Writer->Content Writer(parallelized by section)->Internal linking -> Wordpress upload
               ->Media Pipeline->Media prompt creation->Media Queue->Wordpress Upload
               ->Create Title, Meta, and other blog items
                
## TODO
1. Ollama & Stability AI Integration
2. Database (PostegreSQL, to store Internal Linking Values)
3. Internal linking script -> https://jonathanboshoff.com/automate-internal-linking-with-python/
4. Groq API Integration
5. Koala.sh API Integration
6. Parallel compute
7. Redesign API architecture (using the same functions (w/ same functionality) for each of the different LLM APIs

## Future plans
- Frontend: Htmx? Svelte?
- Wordpress plugin?
- Amazon product review (different assistant)
- Research Agent (wikipedia, Amazon, and top articles)
    - Need more research
- Start collecting good blog urls to hopefully train my own AI
 
### First Run
Processing Blog Posts: 14it [1:04:47, 277.68s/it] 1hr for 14 items w/ pictures
