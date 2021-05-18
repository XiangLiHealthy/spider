from http_server import HttpServer
from sanic import Sanic
from sanic.response import text
import ssl
from http_handler import SetActionHandlerImp
from http_handler import UploadLandmarksHandler
from http_handler import FinishHandlerImp
from uri_def import *


g_http_handlers = {
    URI_SET_ACTION : SetActionHandlerImp() ,
    URI_UPLOAD_LANDMARKS : UploadLandmarksHandler() ,
    URI_FINISH : FinishHandlerImp() ,
}

app = Sanic("My Hello, world app")

################# add interface #########################################
@app.get("/")
async def hello_world(request):
    surpport_uri = 'surpport post uri: \n'
    try:
        handlers = list(g_http_handlers)
        for item in handlers:
            surpport_uri += item + '\n'
    except Exception as e:
        surpport_uri = e

    return text(surpport_uri)

@app.post("/test_post")
async def test_post(request):
    surpport_uri = 'surpport post uri: \n'
    for key, value in g_http_handlers :
        surpport_uri += key + '\n'

    return text(surpport_uri)

@app.post(URI_SET_ACTION)
async def set_action(request) :
    response = text('')
    try:
        response = g_http_handlers[URI_SET_ACTION].perform(request)
    except Exception as e :
        response.body = e

    return response

@app.post(URI_UPLOAD_LANDMARKS)
async def upload_landmarks(request) :
    response = text('')
    try:
        response = g_http_handlers[URI_UPLOAD_LANDMARKS].perform(request)
    except Exception as e:
        response.body = e

    return response

@app.post(URI_FINISH)
async def finish_train(request) :
    response = text('')
    try:
        response = g_http_handlers[URI_FINISH].perform(request)
    except Exception as e:
        response.body = e

    return response


##################set server config####################################
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

context = None
app.run(host='0.0.0.0', port=9999, workers=4)

