# Simple OCPP Client/Server Test Project

**TOC**
- [Target spec](#target-spec)
- [Project Structure](#project-structure)
- [How to run project](#how-to-run-project)
    - [Create Python venv](#create-python-venv)
    - [Start CSMS](#start-csms)
    - [Start Charge Point](#start-charge-point)
    - [Test REST End Point(s)](#test-rest-end-points)
      - [List registered CP(s)](#list-registered-cps)
      - [Reserve EVSE](#reserve-evse)


## Target spec

Scenario based on Open Charge Point Protocol (OCPP) version 2.0.1:

- Set up a client (the charging station) and a server (the CSMS) using WebSockets
- Have the client exchange two messages with the CSMS, one is the BootNotificationRequest and -Response, the other one is the StatusNotificationRequest and -Response. You’ll find more information about those two messages here (hint: have a look at part 2 of the OCPP 2.0.1 specification).
- Use the Call, CallResult, and CallError mechanism to send the two messages (hint: have a look at part 4 of the OCPP 2.0.1 specification)
- Use basic authentication (no TLS security) for the charging station to authenticate at the CSMS
- Make sure the integrity of each message received is validated. You can ignore the optional fields of the messages in your implementation. Hint: you can use the JSON schema files that are provided with the specification if you want.
- Make sure the messages will be received in the right order, or reply with an error
- Make sure the client won't send a message until it received a CallResult/CallError

Extension: Implement a reservation.

- Add a REST API layer to the CSMS to simulate an EV driver reserving a specific charging station.
- If the CSMS has an available charging station (CS) then it should send a ReserveNowRequest and the CS should respond accordingly. (hint: have a look at part 2 of the OCPP 2.0.1 specification)
- If there is no charging station available, then the API should return a 503 Service Unavailable.

## Project Structure

The project consists of two Python 3 applications:
- [csms](./csms/app.py)  Implements simple Charge Station Management System
- [charging_point](./charging_station/app.py) implements simple Charge Point

## How to run project

### Create Python venv

Run following command from the root of the project:

```shell
python3 -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
```

### Start CSMS

Run following command from the root of the project:
```shell
. ./.venv/bin/activate
cd cmsc
python app.py
```

Expected output:

```shell
$ python app.py 
INFO:root:WebSocket Server Started : 0.0.0.0:9000
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```

### Start Charge Point
Run following command from the root of the project (in new terminal):

```shell
. ./.venv/bin/activate
cd charging_point
python app.py CP_1
```

**NOTE** You can start as many CP as you wish, just make sure to provide different cp_id as a first parameter. 
For example, if you want to start CP with cp_id 'SupperCharger42', start the app with following command:

```shell
. ./.venv/bin/activate
cd charging_point
python app.py SupperCharger42
```

Expected output: 

In the CMSC terminal:

```text
INFO:root:Protocols Matched: ocpp2.0.1
INFO:ocpp:CP_1: receive message [2,"439fe236-edb6-40ea-9056-9ca8cdd40da8","BootNotification",{"chargingStation":{"model":"Wallbox XYZ","vendorName":"anewone"},"reason":"PowerUp"}]
INFO:root:CP_1: state transition : Off -> BootNotification -> PoweredUp
INFO:ocpp:CP_1: send [3,"439fe236-edb6-40ea-9056-9ca8cdd40da8",{"currentTime":"2021-07-11T03:52:53.938094","interval":10,"status":"Accepted"}]
INFO:ocpp:CP_1: receive message [2,"013adc17-31b3-4944-923f-9024789e85bd","StatusNotification",{"timestamp":"2021-07-11T03:52:53.941393","connectorStatus":"Available","evseId":1,"connectorId":1}]
INFO:root:CP_1: state transition : PoweredUp -> StatusNotification -> Ready
INFO:ocpp:CP_1: send [3,"013adc17-31b3-4944-923f-9024789e85bd",{}]
```

**NOTE** Actual UUID values will be different

In the Charging Point terminal:

```text
INFO:ocpp:CP_1: send [2,"439fe236-edb6-40ea-9056-9ca8cdd40da8","BootNotification",{"chargingStation":{"model":"Wallbox XYZ","vendorName":"anewone"},"reason":"PowerUp"}]
INFO:ocpp:CP_1: receive message [3,"439fe236-edb6-40ea-9056-9ca8cdd40da8",{"currentTime":"2021-07-11T03:52:53.938094","interval":10,"status":"Accepted"}]
INFO:ocpp:CP_1: send [2,"013adc17-31b3-4944-923f-9024789e85bd","StatusNotification",{"timestamp":"2021-07-11T03:52:53.941393","connectorStatus":"Available","evseId":1,"connectorId":1}]
INFO:ocpp:CP_1: receive message [3,"013adc17-31b3-4944-923f-9024789e85bd",{}]
```

### Test REST End Point(s)

#### List registered CP(s)

You can use following command to get list of all connected CP(s)

```shell
curl -s http://localhost:8080/list | jq .
```

Expected output:
```json
{
  "cp_ids": [
    "CP_1"
  ]
}
```

**NOTE** If you don't have [jq](https://stedolan.github.io/jq/download/) installed, you can omit `| jq .` part of the command

The output of `.../list` reflects current state. For example, if you start another Charge Point, you should see this CP id in the list.
And if you stop the CP, it's id should be removed from the list.

#### Reserve EVSE

To test `ReserveNow` run following command:

```shell
curl -s -X POST http://localhost:8080/reserve/CP_1 | jq .
```

Expected output:

... in case the 'CP_1' Charge Point is up and running:

```json
{
  "status": "Accepted"
}
```

... in case the 'CP_1' Charge Point is not up and running:
```json
{
  "error_code": 503,
  "message": "No such Charge Point. [CP_1]"
}
```
