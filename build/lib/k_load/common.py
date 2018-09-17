import re

def parse_url(url):
    ksong = re.compile(r'kg\.qq\.com')
    if re.search(ksong, url):
        from .downloaders import KSong
        return KSong(url)
    else:
       return None


def run(url):
    k_obj = parse_url(url)
    if not k_obj:
        raise ValueError('Cannot parse this url')
    k_obj.log_info()
    k_obj.download()
