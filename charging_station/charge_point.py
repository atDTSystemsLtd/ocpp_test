from typing import Dict

from ocpp.routing import on
from datetime import datetime

from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call
from ocpp.v201 import call_result as result
from ocpp.v201.enums import ConnectorStatusType, ReserveNowStatusType

EVSE_1_ID: int = 1
CONNECTOR_1_ID: int = 1


class ChargePoint(cp):
    @on('ReserveNow')
    async def on_reserve_now(self, id: int, expiry_date_time: str, evse_id:int, id_token: Dict[str, str]):
        response = result.ReserveNowPayload(
            status=ReserveNowStatusType.accepted
        )

        return response

    async def send_boot_notification(self) -> result.BootNotificationPayload:
        request = call.BootNotificationPayload(
            charging_station={
                'model': 'Wallbox XYZ',
                'vendor_name': 'anewone'
            },
            reason="PowerUp"
        )
        return await self.call(request)

    async def send_status_notification_request(self) -> result.StatusNotificationPayload:
        request = call.StatusNotificationPayload(
            timestamp=datetime.utcnow().isoformat(),
            evse_id=EVSE_1_ID,
            connector_id=CONNECTOR_1_ID,
            connector_status=ConnectorStatusType.available
        )

        return await self.call(request)
