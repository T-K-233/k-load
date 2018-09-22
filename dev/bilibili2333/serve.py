import socket
import re
import threading

from k_load.extractors import Bilibili


class DownloadSite:
    '''
    A website for downloading Bilibili videos.
    '''
    
    def _establish_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
        self.sock.bind(('0.0.0.0', 80))
        self.sock.listen(10)
        self.client_pool = []

        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(target=Worker, args=(conn, ))
            thread.setDaemon(True)
            thread.start()
            self.client_pool.append(thread)

    def run(self):
        '''
        entry point
        '''
        self._establish_socket()

class Worker:
    base_url = 'https://www.bilibili.com'
    
    def __init__(self, conn):
        self.conn = conn
        self._process()
    
    def _send_header(self, params):
        head = 'HTTP/1.1 200 OK\r\n'
        for p in params:
            head += '%s: %s\r\n' % (p, str(params[p]))
        head += '\r\n'
        self.conn.send(head.encode())
        
    def _process(self):
        buffer = b''
        while True:
            pack = self.conn.recv(1024)
            if pack is None or len(pack) < 1024:
                buffer += pack
                break
            buffer += pack
        req_header = buffer.decode()

        re_url = self._parse_url(req_header)
        if not re_url:
            error_msg = 'params error'
            res_header = self._send_header({'Content-Length': len(error_msg)})
            self.conn.send(error_msg.encode())
        else:
            obj = self._get_k_load_res(re_url.group())
            res_header = self._send_header({'Access-Control-Allow-Origin': '*',
                                            'Content-Range': 'bytes',
                                            'Content-Type': 'video/x-flv',
                                            'Content-Length': obj.size,
                                            'Content-Disposition': 'attachment; filename="%s.flv"' % obj.name})
            self._send_file(obj)
        self.conn.close()
            
    def _parse_url(self, req_header):
        try:
            aid = req_header.split('\r\n')[0].split(' ')[1]
        except:
            return False
        return re.match(r'\/video\/av\d+', aid)

    def _get_k_load_res(self, url):
        obj = Bilibili(**{'url': self.base_url+url})
        obj.parse()
        return obj

    def _send_file(self, vid_obj):
        pack_size = 2**18
        while True:
            buffer = vid_obj.resource_res.read(pack_size)
            if not buffer:
                try:
                    self.conn.send(buffer)
                except:
                    pass
                break
            try:
                self.conn.send(buffer)
            except:
                pass


app = DownloadSite()

app.run()
