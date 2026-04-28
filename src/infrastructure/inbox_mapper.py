import logging
from dataclasses import fields

from src.application.dto import InboxEventCreateDTO


log = logging.getLogger(__name__)


def message_to_inbox_dto(message: dict) -> dict:
    fields_to_populate = {
        f.name
        for f in fields(InboxEventCreateDTO)
        if f.name not in ("id", "payload", "status")
    }
    result = {"payload": {}}
    for k, v in message.items():
        if k in fields_to_populate:
            if k == "event_type":
                result[k] = v.upper()
                continue
            result[k] = v
        else:
            result["payload"].update({k: v})
    return result
