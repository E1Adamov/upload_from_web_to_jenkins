import os
import logging
from aiohttp import web

import config
from python import global_objects, helper

routes = web.RouteTableDef()


async def __get_response_args(request, folder_name, mime_type, override_path=None):
    file_name = override_path or request.path[1:]
    file_path = os.path.join(folder_name, file_name)
    status = 200 if os.path.isfile(file_path) else 404
    read_method = 'rb' if 'image' in mime_type else 'r'

    if status == 200:
        headers = {'content-type': mime_type}
        with open(file_path, read_method) as f:
            body = f.read()
    else:
        headers = {'content-type': 'text/html'}
        body = '404 Not found'

    return status, headers, body


@routes.get('/')
async def home(request):
    status, headers, body = await __get_response_args(request, 'html', 'text/html', 'alt_d_upload.html')
    return web.Response(status=status, headers=headers, body=body)


@routes.get('/{name}.css')
async def css(request):
    status, headers, body = await __get_response_args(request, 'css', 'text/css')
    return web.Response(status=status, headers=headers, body=body)


@routes.get('/{name}.js')
async def js(request):
    status, headers, body = await __get_response_args(request, 'js', 'application/javascript')
    return web.Response(status=status, headers=headers, body=body)


@routes.get('/{name}.ico')
async def ico(request):
    status, headers, body = await __get_response_args(request, 'img', 'image/x-icon')
    return web.Response(status=status, headers=headers, body=body)


@routes.get('/{name}.html')
async def html(request):
    status, headers, body = await __get_response_args(request, 'html', 'text/html')
    return web.Response(status=status, headers=headers, body=body)


@routes.post('/upload_form')
async def handle_alt_d_form(request):

    if request.content_type == 'multipart/form-data':
        fields = helper.parse_multipart(request)
        global_objects.q.put(fields)
        status = 200
        body = 'Submit successfully'
    else:
        status = 400
        body = 'Invalid request'

    return web.Response(body=body, status=status)


def run():
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=config.HOST, port=config.PORT)
