from enum import Enum
from typing import List

class EventTypes(Enum):
    TRUCK_ARRIVAL = "Truck arrived"
    REQ_STATUS_CHECK = "Mandatory check time hit"
    REQ_ADDRESS_CHANGE = "Mandatory address change time hit"
    DELAYED_PACKAGES_ARRIVED = "Delayed packages have arrived"



class SimEvent(object):
    def __init__(self, event_type: EventTypes, time: float):
        self.event_type = event_type
        self.time = time

    def __str__(self):
        return self.event_type.value


class SimTime(object):
    """Tracks current time in simulation.
    Floats are a immutable, and thus can't be passed by reference."""

    def __init__(self, initial_time: float, end_of_day: float):
        self.current = initial_time
        self.initial_time = initial_time
        self.end_of_day = end_of_day
        self.events: List[SimEvent] = []

    def get_now(self):
        return self.current

    def get_min(self):
        self.current//100

    def increment(self):
        self.current += 1
        if (self.current % 100) == 60:
            self.current += 40
        # Triggered events
        return [e for e in self.events if self.current == e.time]

    def add_event(self, event_type: EventTypes, time: float):
        self.events.append(SimEvent(event_type, time))

    def in_business_hours(self):
        return self.initial_time <= self.current < self.end_of_day

class EventAdder(object):
    @staticmethod
    def add_events(sim_time: SimTime):
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 900)
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 1000)
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 1300)
        sim_time.add_event(EventTypes.DELAYED_PACKAGES_ARRIVED, 905)
        sim_time.add_event(EventTypes.REQ_ADDRESS_CHANGE, 1020)
