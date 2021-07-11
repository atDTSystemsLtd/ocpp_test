from dataclasses import dataclass
from typing import Dict, Callable

import simplejson as json
from aiohttp import web


@dataclass
class MethodAndHandler:
    method: Callable
    handler: Callable


def json_response(body: any, http_status: int = 200) -> web.Response:
    return web.Response(
        content_type='application/json',
        body=json.dumps(body),
        status=http_status
    )


def error_response(message: str = 'error', http_status: int = 400) -> web.Response:
    return json_response({'error_code': http_status, 'message' : message}, http_status=http_status)


async def get_index(request: web.Request) -> web.Response:
    return json_response({"status": "running"})


def configure_rest_api(endpoints: Dict[str, MethodAndHandler]):
    app = web.Application()

    endpoints['/'] = MethodAndHandler(method=web.get, handler=get_index)

    app.add_routes(
        list(map(
            lambda x: x[1].method(x[0], x[1].handler),
            endpoints.items()
        )))

    return app
