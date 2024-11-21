import ollama
import openai_api

blog_idea = 'coding for a living'

result = ollama.generate(
    model='llama2',
    prompt=f'''
You are a Blog Outline Assisant that creates all of the headers for a blog.
Create a header outline for a blog post about {blog_idea}.
Write in Markdown. Write only the headers. Follow the Example
Example:
# Programming Side Hustles: Turning Code into Cash

## Introduction
### Understanding the Side Hustle Culture
### Why Programming Skills Are an Asset in the Gig Economy
### Overview of Side Hustle Opportunities for Programmers

## Developing Mobile Apps
### Identifying Market Needs
### Building Your First App
### Monetization Strategies
### Publishing and Marketing Tips

## Freelancing and Remote Contract Work
### Platforms for Finding Freelance Programming Work
### Setting Up a Winning Profile
### Best Practices for Managing Freelance Projects
### Navigating Taxes and Legal Aspects of Freelancing

## Open Source Contributions and Paid Support
### Finding Projects that Offer Bounties
### Establishing Credibility in the Open Source Community
### Offering Paid Support for Popular Open Source Tools

## Creating Educational Content
### Blogging and Writing Technical Articles
### Developing Online Courses and Tutorials
### Streaming and Video Content Creation

## Selling Software Tools and Libraries
### Identifying Gaps in the Tooling Market
### Developing and Packaging Your Software
### Licensing and Selling Your Work
### Building and Supporting a User Community

## Tech-Driven Content Creation
### Developing Programming-Related Podcasts
### Creating and Managing Tech-Focused Websites
### Leveraging Social Media to Promote Your Content

## Niche Consulting and Advising
### Positioning Yourself as an Industry Expert
### Types of Consulting Services You Can Offer
### Networking and Finding Consulting Opportunities

## Conclusion
### Balancing a Side Hustle with a Full-Time Job
### Tips for Long-Term Success in Side Hustling
### Continuing to Learn and Grow as a Programmer
'''
)
response = openai_api.list_headers(openai_api.find_substring_indexes(result['response'], "\n## "), result['response'])

for header in response:
    print(header)
    prompt_str=f'''
        You are a Software Engineer blog writer, you talk about many topics
        in software engineering. Be opinionated, concise, and descriptive.
        write the section labeled {header} in a blog about {blog_idea}
    '''
    body = ollama.generate(
        model='llama2',
        prompt=prompt_str
    )
    print(body['response'])

