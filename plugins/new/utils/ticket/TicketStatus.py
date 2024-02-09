from enum import Enum


class TicketStatus(Enum):
    WAITING = "WAITING"
    SERVING = "SERVING"
    COMPLETED = "COMPLETED"
