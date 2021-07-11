import logging
from typing import Dict

import logging
from typing import Dict

import asyncio
from aiohttp import web

from charge_point_csms import ChargePoint
from webserver import configure_rest_api, MethodAndHandler, json_response, error_response
from websocket import run_ocpp_server

logging.basicConfig(level=logging.INFO)

CHARGE_POINTS: Dict[str, ChargePoint] = {}


async def on_connect_charge_point(cp_id: str, websocket):
    global CHARGE_POINTS

    new_charge_point = ChargePoint(cp_id, websocket)
    CHARGE_POINTS[cp_id] = new_charge_point

    await new_charge_point.start()


async def on_disconnect_charge_point(cp_id: str):
    global CHARGE_POINTS

    if cp_id in CHARGE_POINTS:
        del CHARGE_POINTS[cp_id]


async def get_list_rest_handler(request: web.Request):
    global CHARGE_POINTS
    return json_response({"cp_ids": list(CHARGE_POINTS.keys())})


async def reserve_cp_now_rest_handler(request: web.Request):
    global CHARGE_POINTS

    cp_id = request.match_info.get('cp_id')

    cp = CHARGE_POINTS.get(cp_id)

    if cp is None:
        return error_response(f'No such Charge Point. [{cp_id}]', 503)

    status = await cp.send_reserve_now()

    return json_response({'status': status})


def main():
    asyncio.get_event_loop().create_task(
        run_ocpp_server(on_connect_charge_point, on_disconnect_charge_point))

    web.run_app(
        configure_rest_api({
            '/list': MethodAndHandler(handler=get_list_rest_handler, method=web.get),
            '/reserve/{cp_id}': MethodAndHandler(handler=reserve_cp_now_rest_handler, method=web.post)}))


if __name__ == '__main__':
    main()
