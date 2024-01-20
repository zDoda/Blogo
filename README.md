# OpenAI's Assistant API Autoblogger
I am trying to make a bulk autoblogger that takes in my keyword research csv and write SEO optimized articiles

Read TODO.md to see the full scope of the project

## TODO

- Wordpress Integration
    - schedule post to publish
    - have custom tables, quotes, and other wp blocks

- Better Content Writer
    - Async/Parallelize the writer

- Internal linking script
    - Python script, no AI

- Research Agent (wikipedia, Amazon, and top articles)
    - Need more research

- Database (PostegreSQL)

- Amazon product review (different assistant)

- Start collecting good blog urls to hopefully train my own AI

- Media Queue

## *Content Pipeline*
This is the process for creating one article (Articles are going to be written in parallel)
User input(csv?)->Research Agent->Outline Writer->Content Writer(parallelized by section)->Internal linking -> Wordpress upload
                ->Media Pipeline->Media prompt creation->Media Queue->Wordpress Upload
                ->Create Title, Meta, and other blog items
                
## Tech Stack
- Backend: Flask
- Database: PostgreSQL

## Future plans
- Frontend: Htmx? Svelte?
- Wordpress plugin?
