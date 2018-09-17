from urllib import request
import datetime
import hashlib
import json
import os
import re
from io import BytesIO
import gzip

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  # noqa
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',  # noqa
}


def safe_filename(filename):
    filename = re.sub(r'[\\\/:\*\?"<>|]', '_', filename)
    return filename


class Downloadable:
    def __init__(self, **kwargs):
        self.buffer_size = 2**18
        self.url = kwargs.get('url')
        self.save_dir = kwargs.get('save_dir') if kwargs.get('save_dir') else ''
        self.downloaded_size = 0

    def __repr__(self):
        return '<Downloadable Object name="%s">' % self.name

    def parse(self):
        print('[K-Load] Gathering Information...')
    
    def _log_parse_info(self):
        print('='*48)
        print(' - Site:\t%s' % self.site)
        print(' - Name:\t%s' % self.name)
        print(' - Type:\t%s' % self.type)
        print(' - Format:\t%s' % self.format)
        print(' - Size:\t%d b' % self.size)
        print('='*48)
    
    def download(self):
        print('[K-Load] Downloading...')

    def _log_progress(self):
        percent = (self.downloaded_size/self.size)*100
        print('%.2f%% downloaded' % percent, end='\r')

    def _log_download_info(self):
        print('[K-Load] Download Finished.')
        print('\t File stored at "%s"'%(self.filepath))

class Bilibili(Downloadable):
    site = '哔哩哔哩动画'

    SEC1 = '94aba54af9065f71de72f5508f1cd42e'
    api_url = 'http://interface.bilibili.com/v2/playurl?'
    
    def _get_cid(self, respond_obj):
        buffer = BytesIO(respond_obj.read())
        f = gzip.GzipFile(fileobj=buffer)
        data = f.read()
        data = data.decode('utf-8', 'ignore')
        cid = re.search('(?<="cid":)(\d+)', data).group()
        title = re.search(r'(?<=<title data-vue-meta="true">).+(?=_哔哩哔哩 \(゜-゜\)つロ 干杯~-bilibili</title>)', data).group()
        return cid, title

    def _get_xml(self, cid, quality=15):
        params_str = 'appkey=84956560bc028eb7&cid={}&otype=xml&qn={}&quality={}&type='.format(cid, quality, quality)
        chksum = hashlib.md5(bytes(params_str + self.SEC1, 'utf8')).hexdigest()
        api_url = self.api_url + params_str + '&sign=' + chksum
        res = request.urlopen(request.Request(api_url, headers={'referer': self.url, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}))
        data = res.read()
        content_encoding = res.getheader('Content-Encoding')
        xml_str = data.decode('utf-8', 'ignore')
        return xml_str

    def parse(self):
        super().parse()
        self.format = '.flv'
        req = request.Request(self.url, headers=HEADERS)
        res = request.urlopen(req)

        cid, self.name = self._get_cid(res)
        self.filepath = os.path.join(os.getcwd(), self.save_dir, '%s%s'%(safe_filename(self.name), self.format))
        
        xml_data = self._get_xml(cid)

        self.resource_url = re.search(r'(?<=<url><!\[CDATA\[).+(?=\]\]></url>)', xml_data).group()

        self.resource_res = request.urlopen(request.Request(self.resource_url, headers={'referer': self.url, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}))
        self.type = self.resource_res.getheader('Content-Type')
        self.size = int(self.resource_res.getheader('content-length'))
        
        self._log_parse_info()

    def download(self):
        super().download()
        with open(self.filepath, 'wb') as f:
            while True:
                buffer = self.resource_res.read(self.buffer_size)
                if not buffer:
                    f.write(buffer)
                    break
                f.write(buffer)
                self.downloaded_size += self.buffer_size
                self._log_progress()
        self._log_download_info()
        


class KSong(Downloadable):
    site = '全民K歌'

    def parse(self):
        super().parse()
        self.format = '.m4a'
        req = request.Request(self.url)
        res = request.urlopen(req)
        json_re = re.compile(r'(?<=window\.__DATA__ = ).+(?=;.+</script>)')
        res = re.search(json_re, res.read().decode()).group()

        self.info = json.loads(res)
        self.info.update(self.info['detail'])
        
        self.name = '%s-%s' % (self.info['song_name'], self.info['nick'])
        self.resource_url = self.info['playurl']
        self.filepath = os.path.join(os.getcwd(), self.save_dir, '%s%s'%(safe_filename(self.name), self.format))

        req = request.Request(self.resource_url)
        self.resource_res = request.urlopen(req)
        self.type = self.resource_res.getheader('Content-Type')
        self.size = int(self.resource_res.getheader('Content-Length'))
        
        self.pub_time = datetime.datetime.fromtimestamp(int(self.info['ctime'])).strftime("%Y-%m-%d %H:%M:%S")

        self._log_parse_info()

    def download(self):
        super().download()
        with open(self.filepath, 'wb') as f:
            while True:
                buffer = self.resource_res.read(self.buffer_size)
                if not buffer:
                    f.write(buffer)
                    break
                f.write(buffer)
                self.downloaded_size += self.buffer_size
                self._log_progress()
        self._log_download_info()

        
