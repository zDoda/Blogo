# BLOGO - Assistant Autoblogger
Provide a csv and BLOGO parses, writes, and uploads article to wordpress with images!

## Why?
I have many clients from freelance Web/SEO, wanting a cheap content so their websites to start indexing for keywords

## Quick start
```bash
pip install -r requirements.txt
```
### How to use - TODO (less hardcoding in python files)
```bash
python main.py
```

## *Content Pipeline*
This is the process for creating one article (Articles are going to be written in parallel)
User input(csv)->Research Agent->Outline Writer->Content Writer(parallelized by section)->Internal linking -> Wordpress upload
               ->Media Pipeline->Media prompt creation->Media Queue->Wordpress Upload
               ->Create Title, Meta, and other blog items
                
## Tech Stack
- Backend: Flask
- Database: PostgreSQL

## TODO

- Wordpress Integration
    - schedule post to publish
    - have custom tables, quotes, and other wp blocks

- Better Content Writer
    - Async/Parallelize the writer
    - Enable/Disable images
    - gen images every n headers
    - fix '### header' in paragraphes
    - Add Categories and tags to post
    - Add better logging for errors
    - Add a double check on JSON parse that we generated

- CLI app
    - gen images every n headers option

- Internal linking script
    - Python script, no AI

- Research Agent (wikipedia, Amazon, and top articles)
    - Need more research

- Database (PostegreSQL)

- Amazon product review (different assistant)

- Start collecting good blog urls to hopefully train my own AI

- Media Queue


## Future plans
- Frontend: Htmx? Svelte?
- Wordpress plugin?
 
### First Run
Processing Blog Posts: 14it [1:04:47, 277.68s/it] 1hr for 14 items w/ pictures
