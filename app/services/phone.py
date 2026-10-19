"""Phone calls and SMS belong to the hardware phase (GSM module / SIM).

These stubs keep the rest of the app wired up: when the hardware is ready,
implement the two functions below and nothing else needs to change.
"""

_NOT_READY = {
    "implemented": False,
    "status": "coming_soon",
    "message": "Phone calls and SMS are not implemented yet. Coming soon.",
}


def place_call(number):
    return dict(_NOT_READY, action="call", number=number)


def send_sms(number, text):
    return dict(_NOT_READY, action="sms", number=number)
