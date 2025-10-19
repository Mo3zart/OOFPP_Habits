from datetime import datetime

class Habit:
    def __init__(self, name, periodicity, created_at=None):
        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()
        self.completions = []

    def complete(self):
        """Mark this habit as completed."""
        self.completions.append(datetime.now())

    def __repr__(self):
        return f"<Habit {self.name} ({self.periodicity})>"
