
def find_substring_indexes(main_string, substring):
    return [i for i in range(len(main_string)) if main_string.startswith(substring, i)]


def check_headers(article):
    h2_indexes = find_substring_indexes(article, "## ")
    for idx in h2_indexes:
        print(idx)
        print(f'Check: {article[idx]}\n\n')
        if article[idx-1] != '\n' and article[idx-1] != '#':
            article = article[:idx] + '\n\n' + article[idx:]
    h3_indexes = find_substring_indexes(article, "### ")
    for idx in h3_indexes:
        if article[idx-1] != '\n' and article[idx-1] != '#':
            article = article[:idx] + '\n\n' + article[idx:]
    return article

line = 'In the next sections, we will explore the prerequisites for learning AI/ML, essential tools and frameworks, setting up your development environment, building a strong theoretical foundation, hands-on practice through projects, networking and community involvement, staying updated with AI/ML trends and advances, and relevant FAQs to help you navigate the AI/ML learning journey## Prerequisites for Learning AI/ML'
print(check_headers(line))
