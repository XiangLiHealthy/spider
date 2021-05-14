from http_handler import HttpHandler
from sanic import Sanic
from sanic.response import text

async def handler(request):
    return text("hello world")

class HttpServer :
    def __init__(self, app):
        self.app_ = app

        return

    def start_server(self):
        # self.app_.run(host='0.0.0.0', port=8080, workers=4)

        return

    def stop(self):

        return

    def register_handler(self, http_handler):
        self.app_.add_route(handler, '/test', methods=['POST'])
        return
