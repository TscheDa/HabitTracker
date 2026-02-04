import pytest
import os
from datetime import datetime
from habit_tracker.models import Habit, Periodicity
from habit_tracker.db import HabitRepository


# Fixture to set up and tear down a temporary database for testing
@pytest.fixture
def test_repo():
    db_name = "test_habits.db"
    # Ensure we start fresh
    if os.path.exists(db_name):
        os.remove(db_name)

    repo = HabitRepository(db_path=db_name)
    repo.create_tables()

    yield repo

    # Cleanup after test
    if os.path.exists(db_name):
        os.remove(db_name)


def test_add_habit(test_repo):
    """Test that a habit can be correctly added to the database."""
    habit = Habit(
        name="Test Habit", periodicity=Periodicity.DAILY, created_at=datetime.now()
    )
    habit_id = test_repo.add_habit(habit)

    assert habit_id is not None
    habits = test_repo.list_habits()
    assert len(habits) == 1
    assert habits[0].name == "Test Habit"
    assert habits[0].periodicity == Periodicity.DAILY


def test_add_duplicate_habit_error(test_repo):
    """Test that adding a habit with a duplicate name raises a ValueError."""
    habit = Habit(
        name="Unique Habit", periodicity=Periodicity.DAILY, created_at=datetime.now()
    )
    test_repo.add_habit(habit)

    # Try adding the exact same habit again
    with pytest.raises(ValueError):
        test_repo.add_habit(habit)


def test_update_habit_name(test_repo):
    """Test updating a habit's name."""
    habit = Habit(
        name="Old Name", periodicity=Periodicity.DAILY, created_at=datetime.now()
    )
    habit_id = test_repo.add_habit(habit)

    test_repo.update_habit(habit_id, new_name="New Name")

    updated_habit = test_repo.list_habits()[0]
    assert updated_habit.name == "New Name"
    # Periodicity should remain unchanged
    assert updated_habit.periodicity == Periodicity.DAILY


def test_update_habit_periodicity(test_repo):
    """Test updating a habit's periodicity."""
    habit = Habit(name="Gym", periodicity=Periodicity.WEEKLY, created_at=datetime.now())
    habit_id = test_repo.add_habit(habit)

    test_repo.update_habit(habit_id, new_periodicity=Periodicity.DAILY)

    updated_habit = test_repo.list_habits()[0]
    assert updated_habit.periodicity == Periodicity.DAILY


def test_update_non_existent_habit(test_repo):
    """Test updating a habit that does not exist raises ValueError."""
    with pytest.raises(ValueError):
        test_repo.update_habit(999, new_name="Ghost Habit")


def test_delete_habit(test_repo):
    """Test that a habit can be deleted."""
    habit = Habit(
        name="To Delete", periodicity=Periodicity.WEEKLY, created_at=datetime.now()
    )
    habit_id = test_repo.add_habit(habit)

    # Verify it's there
    assert len(test_repo.list_habits()) == 1

    # Delete
    test_repo.delete_habit(habit_id)

    # Verify it's gone
    assert len(test_repo.list_habits()) == 0
