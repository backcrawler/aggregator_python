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


class ResponceCodeError(BaseException):
    '''Used to signify an invalid responce code while parsing data from an external resource'''
    def __init__(self, responce_code, *args, **kwargs):
        self.code = responce_code
        super().__init__(*args, **kwargs)
