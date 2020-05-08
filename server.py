import socketserver
from http.server import BaseHTTPRequestHandler
import os.path
from mongo_connection import Connector
from workout_table_parser import WorkoutPageParser

APP_NAME = 'excersize-db-app'

# Utility class for handling the string from the form input and other common methods
class RequestHandlerUtils:
    # gets the string from the form input and returns the workout name and link value as
    # a pair
    def parse_string(self, form_input):
        split_data = form_input.split("&")
        ex_name = split_data[0].split("=")
        ex_name = ex_name[1]
        ex_link = split_data[1].split("=")
        ex_link = ex_link[1]
        return ex_name, ex_link

    # returns the html header values according to the file name input
    def parse_header(self, file_name):
        if file_name[-4:] == '.css':
            return 'Content-type', 'text/css'
        elif file_name[-5:] == '.json':
            return 'Content-type', 'application/javascript'
        elif file_name[-3:] == '.js':
            return 'Content-type', 'application/javascript'
        elif file_name[-4:] == '.ico':
            return 'Content-type', 'image/x-icon'
        return 'Content-type', 'text/html'


# Handles the get and post requests for the index html page
class WorkoutLinkHandler(BaseHTTPRequestHandler):

    request_handler = RequestHandlerUtils()
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), APP_NAME)
    mongo_connector = Connector()

    def insert_workout_links(self, html):
        # get all the workouts and save them for now.
        # This is not sustainable yet for my case it might work initially
        parser = WorkoutPageParser(html, self.mongo_connector.get_workouts())
        html = parser.insert_into_html()
        return html

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # get the string from the form input
        post_data = str(post_data)
        # parse the links
        ex_name, ex_link = self.request_handler.parse_string(post_data)
        # insert them to the MongoDB
        self.mongo_connector.insert_workout(ex_name, ex_link)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(self.root + '/index.html', 'rb') as fh:
            html = fh.read()
            # re parse the page with the new table values
            self.wfile.write(bytes(self.insert_workout_links(html), 'utf-8'))

    def do_GET(self):
        is_index_val = False
        if self.path == '/css/style.css':
            filename = self.root + '/css/style.css'
        else:
            filename = self.root + '/index.html'
            is_index_val = True
        self.send_response(200)
        headers = self.request_handler.parse_header(filename)
        self.send_header(headers[0], headers[1])
        self.end_headers()
        with open(filename, 'rb') as fh:
            html = fh.read()
            if is_index_val:
                self.wfile.write(bytes(self.insert_workout_links(html), 'utf-8'))
            else:
                self.wfile.write(html)

# main method, sort of, that starts the server and starts listening
try:
    PORT = 8080
    server = socketserver.TCPServer(("", PORT), WorkoutLinkHandler)
    server.serve_forever()
except KeyboardInterrupt:
    server.socket.close()
