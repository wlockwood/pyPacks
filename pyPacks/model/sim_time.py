class SimTime(object):
    """Tracks current time in simulation.
    Floats are a immutable, and thus can't be passed by reference."""

    def __init__(self, initial_time: float, end_of_day: float):
        self.current = initial_time
        self.end_of_day = end_of_day

    def get_now(self):
        return self.current

    def increment(self, amount: float = 1):
        self.current += amount
