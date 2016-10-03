

class Element:
    """
    Building block for an HTML tree
    """

    def __init__(self, tag, parent, text, attrs):
        """
        Initializes each HTML element
        :param tag:     HTML tag
        :param parent:  Parent HTML element
        :param text:    Text contained in the HTML element
        :param attrs:   HTML attributes
        """
        self.tag = tag
        self.parent = parent
        self.children = []
        self.text = text
        self.attributes = {}

        # Create an attribute dictionary for each element from the list of attributes
        for a in attrs:
            try:
                key = a.split('=')[0].strip()
                value = a.replace(key+"=", "", 1)
                self.attributes[key] = value.split('"')[1]
            except ValueError:
                print "Value error:",  self.tag, attrs
                print self.attributes

    def get_by_address(self, address):
        """
        Starting from the element object called, searches for the given xpath-like address
            using the tag of the desired elements and an index.
            If no index provided, 0 is assumed
        :param address: The address as described above, ex:  'body/div[0]/div[3]/@element'
        :return: The element specified if last address bit is '@element'
            or text contained in element if last address bit is '@text'
        """
        # TODO make this compliant with actual xpaths.  I made my own version because I was too lazy to learn...
        addrs = address.split('/')
        current = self
        for a in addrs:

            # If in the last address bit, @text or @element should be specified and returned
            if "@" in a:
                if "text" in a:
                    return current.text
                elif "element" in a:
                    return current

            # If an index is provided, list all matching HTML tags in children and find that index
            elif "[" in a:
                tag = a.split("[")[0]
                index = int((a.split("[")[1]).split("]")[0])
                matching_tags = []
                for el in current.children:
                    if el.tag == tag:
                        matching_tags.append(el)
                try:
                    current = matching_tags[index]
                except IndexError:
                    print "Invalid index"
            else:
                for el in current.children:
                    if el.tag == a:
                        current = el
                        break
            # TODO add some error handling to this.  What if element is not found?

    def print_tree(self):
        """
        Prints the full html element tree as as html file, mostly for debugging
        """
        print "<%s" % self.tag, self.attributes, ">%s" % self.text
        # TODO fix print attributes
        for child_element in self.children:
            child_element.printTree()
        print "</%s" % self.tag+">"

    def find_tag_with_attrs(self, tag, attrs):
        """
        Recursively search specifed element tree for particular tag and attributes
        Returns matching element if tag matches and all attributes specified are found in
            that element's attribute dictionary.
        Returns first matching element if many exist.
        :param tag:     Desired html tag
        :param attrs:   List of desired html attributes, not all expected attrs are required
        :return:        First matching element in specified element tree
        """
        # TODO Return indexable list of matching elements!
        all_attrs_found = True

        """
        If tag matches, try to match all attributes to attribute dictionary
        If a match is found, return that element
        If not, recursively search all children contained in the tree
        """
        if self.tag == tag:
            for search_key in attrs:
                attr_found = False
                for key in self.attributes:
                    if search_key == key and attrs[search_key] == self.attributes[key]:
                        attr_found = True
                if not attr_found:
                    all_attrs_found = False
                    break
        else:
            all_attrs_found = False
        if all_attrs_found:
            return self
        else:
            for child in self.children:
                result = child.find_tag_with_attrs(tag, attrs)
                if result is not None:
                    return result


def is_empty_element_tag(tag):
    """
    Determines if an element is an empty HTML element
    :param tag:     HTML tag
    :return:        True if empty element, false if not
    """
    empty_elements = ['area', 'base', 'br', 'col', 'colgroup', 'command', 'embed', 'hr',
                      'img', 'input', 'keygen', 'link', 'meta', 'param', 'source',
                      'track', 'wbr']
    is_empty = False
    for el in empty_elements:
        if tag == el:
            is_empty = True
            break
    return is_empty


def parse_element(element):
    """
    Parses a given HTML element to get that tag, then extract each attribute to a list
    :param element:     Full string of HTML element
    :return:            tag string and list of attributes
    """

    element = element.split(">")[0]
    tag = element.split(" ")[0]
    number_attrs = element.count('=')
    attr_names = []
    attr_vals = []
    element = element.replace(tag.strip(), "", 1).strip()
    w = 0
    while w < number_attrs:
        try:
            attr_names.append(element.split("=")[0])
            element = element.replace(attr_names[w].strip()+"=", "", 1).strip()
            if element[0] == '"':
                attr_vals.append(element.split('"')[1])
                element = element.replace('"'+attr_vals[w].strip()+'"', "", 1).strip()
            elif element[0] == "'":
                attr_vals.append(element.split("'")[1])
                element = element.replace("'"+attr_vals[w].strip()+"'", "", 1).strip()
            w += 1
        except IndexError:
            break
    attrs = []
    i = 0
    while i < len(attr_names) and i < len(attr_vals):
        attr_string = attr_names[i]+'="'+attr_vals[i]+'"'
        attrs.append(attr_string)
        i += 1
    return tag, attrs


def skip_header_list(html_file):
    """
    Ignore all lines of file until <body> begins, then ignore everything after </body>
    Splits string up using opening brace "<" and returns a list of all elements in body
    :param html_file:   String containing entire HTML file to be parsed
    :return:            List of elements in body of file
    """
    elements = html_file.split("<")

    body_list = []
    header_skipped = False
    footer_reached = False
    for e in elements:
        if not header_skipped:
            # TODO other body attributes may appear??? this is a very hacky solution...
            if "body class" in e or "body id" in e:
                header_skipped = True
        if header_skipped:
            if not footer_reached:
                body_list.append(e)
            else:
                break
            if "/body" in e:
                footer_reached = True

    return body_list


def create_tree(html_file):
    """
    Create an element tree of the body of an HTML string
    :param html_file:   HTML string
    :return:            Body element of the element tree created
    """
    body_elements = skip_header_list(html_file)
    text = body_elements[0].split(">")[1]

    # Get tag and attributes from the element
    tag, attrs = parse_element(body_elements[0])

    # Create empty body element
    body = Element(tag, None, text, attrs)
    current_element = body

    # In_script used to throw away those pesky scripts that I don't really want anyway..
    in_script = False

    for el in range(1, len(body_elements)):
        # print body_elements[el]

        # Ignore comments completely
        if body_elements[el][0] == "!":
            continue

        # If we are currently inside of a pesky script, skip the current line unless it is the end
        # of the script
        if in_script:
            if "/script" in body_elements[el] or "/noscript" in body_elements[el]:
                in_script = False
                continue
            else:
                continue
        # If the current line is the beginning of a script, start ignoring script lines
        elif "script" in body_elements[el]:
            in_script = True
            continue
        # Isolate the text contained in the HTML element, get tag and attributes
        try:
            text = body_elements[el].split(">")[1]
        except IndexError:
            # print "Index error: ", body_elements[el]
            pass

        tag, attrs = parse_element(body_elements[el])

        # If element tag is a closing tag, close that element and set current element to its parent element
        if "/%s" % current_element.tag == tag:
            if "/body" == tag:
                continue
            # print "Ending element: %s" % tag
            current_element = current_element.parent
            # print "Current element: ", current_element.tag, current_element.attributes

        # If the element actually survived all those "ifs", create an Element object instance as a
        # child of the current element

        else:
            el = Element(tag, current_element, text, attrs)
            current_element.children.append(el)
            current_element = el
            # print "Created element:  %s" % tag, attrs, text
            # print "with parent: ", current_element.parent.tag, current_element.parent.attributes

            # If element tag is the tag of an empty HTML element, it will not have a closer tag,
            # so automatically close that element and go back to its parent
            if is_empty_element_tag(tag):
                current_element = current_element.parent
            # print "Current element: ", current_element.tag, current_element.attributes

    return body

if __name__ == "__main__":
    import requests
    html = requests.get('https://www.github.com').content
    tree = create_tree(html)
    subtree = tree.find_tag_with_attrs('h2', {'class': "featurette-heading display-heading-2 mt-3 text-center"})
    print subtree.text


