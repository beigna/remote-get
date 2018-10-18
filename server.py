from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread, Event
from urllib.parse import parse_qsl
from time import sleep
import queue


class Handler(BaseHTTPRequestHandler):

    server_version = 'TuViejaServer/1.0'
    sys_version = ''

    def render(self, template):
        with open(template, 'r', encoding='utf-8') as fp:
            output = bytes(fp.read(), 'utf-8')

        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(output))

        return output

    def do_GET(self):
        self.send_response(200)
        res = self.render('index.html')
        self.end_headers()
        self.wfile.write(res)

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)

        # application/x-www-form-urlencoded
        data = dict(parse_qsl(body.decode('ascii')))

        print('POST {}'.format(data))
        q.put(data)

        self.send_response(200)
        res = self.render('index.html')
        self.end_headers()
        self.wfile.write(res)


def start_httpd():
    global httpd
    with ThreadingHTTPServer(('0.0.0.0', 8080), Handler) as httpd:
        try:
            httpd.serve_forever()

        except Exception as e:
            httpd.shutdown()


def worker():
    while True:
        item = q.get()
        if item is None:
            print('worker gone')
            break

        print('worker > {}'.format(item))
        q.task_done()


if __name__ == '__main__':
    _stop = Event()

    q = queue.Queue()

    threads = []
    threads.append(Thread(name='httpd', target=start_httpd))
    threads.append(Thread(name='worker', target=worker))

    [th.start() for th in threads]

    try:
        print('Server Ready!')
        while True:
            sleep(0.5)

    except KeyboardInterrupt:
        q.put(None)
        httpd.shutdown()
        [t.join() for t in threads]
