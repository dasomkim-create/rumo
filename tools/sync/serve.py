import http.server, os, sys
ROOT=sys.argv[1]; BL=sys.argv[2]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def do_GET(s):
        if s.path.startswith('/_blob/'):
            i=s.path.split('/')[-1]
            for ext,ct in (('.svg','image/svg+xml'),('.woff2','font/woff2')):
                f=os.path.join(BL,i+ext)
                if os.path.exists(f):
                    b=open(f,'rb').read(); s.send_response(200); s.send_header('Content-Type',ct); s.send_header('Content-Length',str(len(b))); s.end_headers(); s.wfile.write(b); return
            s.send_error(404); return
        return super().do_GET()
    def log_message(s,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',int(sys.argv[3]) if len(sys.argv)>3 else 8765),H).serve_forever()
