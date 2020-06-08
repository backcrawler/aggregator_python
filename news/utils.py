def listify(string):
    '''Turn a "list-string" representation into a complete list; used for cookie handeling'''
    if not string:
        return []
    return string.replace("'", "").strip("[").strip("]").split(', ')


def append_slash(url):
    '''Makes sure the slash is applied at the end'''
    if url[-1] != "/":
        return url + "/"
    return url


def compose_name(name):
    '''Proper name, shown for users'''
    return name.replace('_', ' ').title()
