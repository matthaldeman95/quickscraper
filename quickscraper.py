
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

    def print_tree(self):
        """
        Prints the full html element tree
        """
        print "<%s" % self.tag,
        keys = self.attributes.keys()
        for k in keys:
            print '%s="%s"' % (k, self.attributes[k]),
        print ">%s" % self.text.strip()
        for child_element in self.children:
            child_element.print_tree()
        if not is_empty_element_tag(self.tag):
            print "</%s" % self.tag+">"

    def find_tag_with_attrs(self, tag, attrs, results=None):
        """
        Recursively search specifed element tree for particular tag and attributes
        Returns matching elements if tag matches and all attributes specified are found in
            that element's attribute dictionary.
        Returns a list of matching instances if there are multiple, otherwise returns only
        the one matching element.  If none, returns None.
        :param tag:     Desired html tag
        :param attrs:   List of desired html attributes, not all expected attrs are required
        :param results: Current list of results, used to continue appending results together during recursion
        :return:        List of matching instances, or one matching instance, or None if none
        """
        all_attrs_found = True
        if results is None:
            results = []
        """
        If tags match, attempts to match all given attributes.
        If successful, append matching element to results list.
        Continues recursively through all children of given element
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
            results.append(self)
        for child in self.children:
            child.find_tag_with_attrs(tag, attrs, results)

        if not results:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            return results


def is_empty_element_tag(tag):
    """
    Determines if an element is an empty HTML element, will not have closing tag
    :param tag:     HTML tag
    :return:        True if empty element, false if not
    """
    empty_elements = ['area', 'base', 'br', 'col', 'colgroup', 'command', 'embed', 'hr',
                      'img', 'input', 'keygen', 'link', 'meta', 'param', 'source',
                      'track', 'wbr', 'html']
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


def create_tree(html_file, debug=False):
    """
    Create an element tree of the body of an HTML string
    :param html_file:   HTML string
    :param debug:       Optionally print process of creating tree for debugging
    :return:            Body element of the element tree created
    """
    body_elements = html_file.split("<")

    # Create empty body element
    tree = Element("tree", None, "", "")
    current_element = tree

    # in_script used to throw away scripts
    in_script = False

    for el in range(1, len(body_elements)):
        if debug:
            print body_elements[el]

        # Ignore comments
        if body_elements[el][0] == "!":
            continue

        # If we are currently inside of a script, skip the current line unless it is the end
        # of the script
        if in_script:
            if "/script" in body_elements[el] or "/noscript" in body_elements[el]:
                in_script = False
            continue
        # If the current line is the beginning of a script, start ignoring script lines
        elif "script" in body_elements[el]:
            in_script = True
            continue
        # Isolate the text contained in the HTML element, get tag and attributes
        try:
            text = body_elements[el].split(">")[1]
        except IndexError:
            print "Index error: ", body_elements[el]
            pass

        tag, attrs = parse_element(body_elements[el])

        # If element tag is a closing tag, close element and set current element to its parent element
        if "/%s" % current_element.tag == tag:
            if debug:
                print "Ending element: %s" % tag
            current_element = current_element.parent
            current_element.text += text
            if debug:
                print "Current element: ", current_element.tag, current_element.attributes

        # If the element actually survived all those "ifs", create an Element object instance as a
        # child of the current element

        else:
            el = Element(tag, current_element, text, attrs)
            current_element.children.append(el)
            current_element = el
            if debug:
                print "Created element:  %s" % tag, attrs, text
                print "with parent: ", current_element.parent.tag, current_element.parent.attributes

            # If element tag is the tag of an empty HTML element, it will not have a closing tag,
            # so automatically close that element and go back to its parent
            if is_empty_element_tag(tag):
                current_element = current_element.parent
            if debug:
                print "Current element: ", current_element.tag, current_element.attributes

    return tree
