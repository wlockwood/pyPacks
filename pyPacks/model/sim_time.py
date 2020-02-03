from enum import Enum
from typing import List


class EventTypes(Enum):
    TRUCK_ARRIVAL = "Truck arrived"
    REQ_STATUS_CHECK = "Mandatory check time hit"
    REQ_ADDRESS_CHANGE = "Mandatory address change time hit"
    DELAYED_PACKAGES_ARRIVED = "Delayed packages have arrived"
    DEPART_ASAP = "Depart when ready"


class SimEvent(object):
    def __init__(self, event_type: EventTypes, time: float, related_to_truck_num: int = None):
        self.event_type = event_type
        self.time = time
        self.related_to_truck_num = related_to_truck_num  # For truck arrival events

    def __repr__(self):
        return f"SimEvent: {self.event_type.value} @ {self.time:.1f}"

    def __str__(self):
        return f"{self.event_type.value} @ {self.time:.1f}"


class SimTime(object):
    """Tracks current time in simulation.
    Floats are a immutable, and thus can't be passed by reference."""

    def __init__(self, initial_time: float, end_of_day: float):
        self.current = initial_time
        self.initial_time = initial_time
        self.end_of_day = end_of_day
        self.active_events: List[SimEvent] = []

    def get_now(self):
        return self.current

    def get_min(self):
        return self.current // 100

    def increment(self):
        self.current += .1
        if (self.current % 100) == 60:
            self.current += 40
        # Triggered events
        triggered = [e for e in self.active_events if self.current >= e.time]
        for e in triggered:
            self.active_events.remove(e)
        return triggered

    def add_event(self, event_type: EventTypes, time: float, related_to_truck_num=None):
        # Convert event time in case other code isn't aware of convention
        whole_hours = time // 100
        minutes = time - whole_hours * 100
        extra_hours = minutes // 60
        new_minutes = minutes % 60
        converted_time = (whole_hours + extra_hours) * 100 + new_minutes
        self.active_events.append(SimEvent(event_type, converted_time, related_to_truck_num))

    def in_business_hours(self):
        return self.initial_time <= self.current < self.end_of_day

    def __repr__(self):
        return f"SimTime: {self.current:1f}"

    def __str__(self):
        return f"ST: {self.current:1f}"


class EventAdder(object):
    @staticmethod
    def add_required_events(sim_time: SimTime):
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 900)
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 1000)
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 1300)
        sim_time.add_event(EventTypes.DELAYED_PACKAGES_ARRIVED, 905)
        sim_time.add_event(EventTypes.DELAYED_PACKAGES_ARRIVED, 1020)
        sim_time.add_event(EventTypes.REQ_STATUS_CHECK, 1030)
        sim_time.add_event(EventTypes.REQ_ADDRESS_CHANGE, 1020)


def parse_time(time_string) -> float:
    if time_string == "EOD":
        return 1700
    meridian_string = time_string[-2:].lower()  # Last two characters will be am/pm
    time = float(time_string[:-3].replace(":", "")) + 12 * (meridian_string.__contains__("pm"))
    return time
