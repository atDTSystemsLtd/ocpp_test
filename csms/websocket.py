import logging
from typing import Callable

import websockets

WS_BIND_ADDRESS: str = '0.0.0.0'
WS_BIND_PORT: int = 9000


async def validate_ws_connection(websocket) -> bool:
    requested_protocols = websocket.request_headers.get('Sec-WebSocket-Protocol')

    if requested_protocols is None:
        logging.info("Client hasn't requested any Subprotocol. Closing Connection")
        await websocket.close()
        return False

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        await websocket.close()
        return False

    return True


def extract_cp_id(path: str) -> str:
    return path.strip('/')


async def run_ocpp_server(on_connect_charge_point: Callable, on_disconnect_charge_point: Callable):
    async def on_connect(websocket, path):
        if await validate_ws_connection(websocket):
            try:
                await on_connect_charge_point(extract_cp_id(path), websocket)
            finally:
                await on_disconnect_charge_point(extract_cp_id(path))

    server = await websockets.serve(
        on_connect,
        WS_BIND_ADDRESS,
        WS_BIND_PORT,
        subprotocols=['ocpp2.0.1']
    )

    logging.info(f'WebSocket Server Started : {WS_BIND_ADDRESS}:{WS_BIND_PORT}')

    return server
