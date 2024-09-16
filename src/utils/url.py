import re

def sanitize_url(url):
    url_split = url.split('/')
    tail_split = url_split[-1].split('.')
    tail_remove = ['php','aspx','asp','htm','html','cfm']
    if tail_split[-1].strip() in tail_remove:
        url_split[-1] = ''
        return '/'.join(url_split)
    return url

def remove_protocol_and_www(url):
    regex = re.compile(r"https?://(www\.)?")
    return regex.sub('', url).strip().strip('/')