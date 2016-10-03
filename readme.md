## quickscraper

A quick and dirty Python HTML scraper.

    import requests
    html = requests.get('https://github.com/matthaldeman95/quickscraper').content
    tree = create_tree(html)
    subtree = tree.find_tag_with_attrs('article', {'class': "markdown-body entry-content", 'itemprop': "text"})
    text = subtree.get_by_address('h2[0]/@text')
    print text
    # quickscraper
    text = subtree.get_by_address('p[0]/@text')
    print text
    # A quick and dirty Python HTML scraper.

### Element class

  The fundamental building block for the element tree.  Create an Element instance for every HTML element in body of file using create_tree(html_file).  Each Element has its tag, attributes, text, and children Element objects

  Attributes are held in a dictionary of strings.
