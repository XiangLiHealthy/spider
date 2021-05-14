from http_server import HttpServer
from sanic import Sanic
from sanic.response import text
import ssl

app = Sanic("My Hello, world app")

@app.get("/")
async def hello_world(request):
    print (request)
    return text("Hello, world.")

@app.post("/test_post")
async def test_post(request):
    print (request)
    return text("Hello, world.")

context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH,
)
context.options &= ~ssl.OP_NO_SSLv3

#ssl = {"cert": "./server.crt", "key": "./server.key"}
# DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH
)
context.load_cert_chain(
    "./server.crt", keyfile="./server.key"
)

app.run(host='0.0.0.0', port=9999, workers=4, ssl=context)

