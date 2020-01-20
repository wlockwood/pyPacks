class SimTime(object):
    """Tracks current time in simulation.
    Floats are a immutable, and thus can't be passed by reference."""

    def __init__(self, initial_time: float):
        self.current = initial_time

    def get_now(self):
        return self.current

    def increment(self, amount: float = 1):
        self.current += amount
