import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Tuple
from uuid import uuid4

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call
from ocpp.v201 import call_result as result
from ocpp.v201.enums import RegistrationStatusType, IdTokenType


class Ocpp201CPState(str, Enum):
    Off = 'Off'
    PoweredUp = 'PoweredUp'
    Ready = 'Ready'


class Ocpp201Messages(str, Enum):
    BootNotification = 'BootNotification'
    StatusNotification = 'StatusNotification'
    ReserveNow = 'ReserveNow'


OCPP_V201_STATE_MACHINE: Dict[Ocpp201CPState, Dict[Ocpp201Messages, Ocpp201CPState]] = {
    Ocpp201CPState.Off: {
        Ocpp201Messages.BootNotification: Ocpp201CPState.PoweredUp
    },
    Ocpp201CPState.PoweredUp: {
        Ocpp201Messages.StatusNotification: Ocpp201CPState.Ready
    },
    Ocpp201CPState.Ready: {
        Ocpp201Messages.StatusNotification: Ocpp201CPState.Ready
    }
}


RESERVATION_ID: int = 0


def validate_message(cp_id: str, current_state: Ocpp201CPState, message: Ocpp201Messages) -> Tuple[bool, Ocpp201CPState]:
    if current_state not in OCPP_V201_STATE_MACHINE:
        logging.error(f'{cp_id}: unsupported state : {current_state}')
        return False, current_state

    state_definition = OCPP_V201_STATE_MACHINE[current_state]

    if message not in state_definition:
        logging.error(f'{cp_id}: unsupported message : {current_state} -> {message}')
        return False, current_state

    new_state = state_definition[message]
    logging.info(f'{cp_id}: state transition : {current_state} -> {message} -> {new_state}')
    return True, new_state


class ChargePoint(cp):
    def __init__(self, *pargs, **kwargs):
        super(ChargePoint, self).__init__(*pargs, **kwargs)
        self._current_state = Ocpp201CPState.Off

    @on(Ocpp201Messages.BootNotification)
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        (valid_message, self._current_state) = validate_message(self.id, self._current_state, Ocpp201Messages.BootNotification)

        return result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatusType.accepted if valid_message else RegistrationStatusType.rejected
        )

    @on(Ocpp201Messages.StatusNotification)
    async def on_status_notification(self, evse_id: int, connector_id: int, connector_status: str, **kwargs):
        (valid_message, self._current_state) = validate_message(self.id, self._current_state, Ocpp201Messages.StatusNotification)

        return result.StatusNotificationPayload()

    async def send_reserve_now(self):
        global RESERVATION_ID
        RESERVATION_ID = RESERVATION_ID + 1
        request = call.ReserveNowPayload(
            id=RESERVATION_ID,
            expiry_date_time=(datetime.utcnow() + timedelta(minutes=15)).isoformat(),
            evse_id=1,
            id_token={
                'idToken': str(uuid4()),
                'type': IdTokenType.central,
            }
        )

        response: result.ReserveNowPayload = await self.call(request)

        return response.status
