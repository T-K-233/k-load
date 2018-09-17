import re
import json
import datetime

import requests

class Downloader:
    def log_info(self):
        print('='*36)
        print('=  K-Load ')
        print('='*36)
        print('= Name:\t', self.name)
        print('= Type:\t', self.platform)
        print('= URL:\t', self.url)
        print('= Format:\t', self.format)
        print('='*36)
    
    def __repr__(self):
	    return '<object \'%s\' name=\'%s\'>' % (self.__class__.__name__, self.name)

class KSong(Downloader):
    platform = '全民K歌'
    def __init__(self, url):
        self.url = url
        res = requests.get(self.url)
        pattern = re.compile(r'(?<=window\.__DATA__ = ).+(?=;.+</script>)')
        json_str = re.search(pattern, res.text).group()
        self.info = json.loads(json_str)
        self.info.update(self.info['detail'])
        self.info['ctime'] = datetime.datetime.fromtimestamp(int(self.info['ctime'])).strftime("%Y-%m-%d %H:%M:%S")
        self.download_url = self.info['playurl']
        self.name = '%s-%s' % (self.info['song_name'], self.info['nick'])
        self.format = '.m4a'

    def download(self):
        print('Downloading...')
        res = requests.get(self.download_url)
        filename = '.\\%s_k-load%s' % (self.name, self.format)
        with open(filename, 'wb') as f:
            f.write(res.content)
        print('Finished.')
        print('Saved as %s' % filename)
