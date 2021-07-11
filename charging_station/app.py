import asyncio
import logging
import sys

import websockets

from charge_point import ChargePoint

logging.basicConfig(level=logging.INFO)


async def start_up_sequence(cp: ChargePoint):
    await cp.send_boot_notification()

    await cp.send_status_notification_request()


async def main():
    cp_id = sys.argv[1] if len(sys.argv) > 1 else 'CP_1'

    async with websockets.connect(
            f'ws://localhost:9000/{cp_id}',
            subprotocols=['ocpp2.0.1']
    ) as ws:

        cp = ChargePoint(cp_id, ws)

        await asyncio.gather(
            cp.start(),
            start_up_sequence(cp)
        )


if __name__ == '__main__':
    asyncio.run(main())
