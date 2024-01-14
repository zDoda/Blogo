### TODO

- Wordpress Integration
    - Upload post
    - schedule post to publish
    - have custom tables, quotes, and other wp blocks
    - upload media 

- Better Content writer
    - Better outlines (Outline Assistant, gpt-4)
    - Have assistant write paragraph by paragraph (Writer Assistant, gpt-3.5)
    - embed media

- Internal linking script
    - Python script, no AI
    - maybe AI for now???

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
- Frontend: Htmx
- Wordpress plugin?
