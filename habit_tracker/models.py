from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Periodicity(Enum):
    """
    Enumeration for habit periodicity to prevent string errors.
    """
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

@dataclass
class Habit:
    """
    Data class representing a habit with its attributes.

    Attributes:
        name (str): The name of the habit.
        periodicity (Periodicity): The frequency of the habit.
        created_at (datetime): Timestamp when the habit was created.
        id (int): Database ID (optional, None if not yet saved).
    """
    name: str
    periodicity: Periodicity
    created_at: datetime
    id: int = None

@dataclass
class HabitCompletion:
    """
    Data class representing a habit completion record.

    Attributes:
        habit_id (int): The ID of the habit that was completed.
        completed_at (datetime): The date when the habit was completed.
        id (int): Database ID (optional, None if not yet saved).
    """
    habit_id: int
    completed_at: datetime
    id: int = None