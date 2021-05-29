import http.server
import socketserver
import io
import cgi
from twilio.rest import Client
import yaml

# Set these yourself
TWILIO_ACC_SID = ""
TWILIO_AUTH_TOKEN = ""
PORT = 6968

class LinkYeeter:

    def __init__(self):
        self.cfg_dict = self.read_cfg()
        self.client = Client(self.cfg_dict["twilio_acc_sid"], self.cfg_dict["twilio_auth_key"])

    def read_cfg(self):
        with open('config.yml') as file:
            cfg_dict = yaml.load(file, Loader=yaml.FullLoader)
        return cfg_dict

    def yeetit(self, filename):
        print("test")

class YeetRequestHandler(http.server.SimpleHTTPRequestHandler):

    yeet_link = LinkYeeter()

    def do_POST(self):

        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = io.BytesIO()
        if r:
            f.write(b"Success\n")
        else:
            f.write(b"Failed\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers();
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
            print(type(form))
            try:
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        print(record.file.read())
                else:
                    open("./files/%s"%form["file"].filename, "wb").write(form["file"].file.read())
                    print(form["file"].filename)
            except IOError:
                return (False, "Can't create file to write, do you have write perms?")
        return (True, "Files Uploaded")

Handler = YeetRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port: ", PORT)
    httpd.serve_forever()