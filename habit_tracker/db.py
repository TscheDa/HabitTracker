import sqlite3
from datetime import datetime
from typing import List, Optional
from habit_tracker.models import Habit, HabitCompletion, Periodicity

class HabitRepository:
    """
    Handles all database operations for Habits and HabitCompletions.
    Implements the repository pattern to abstract SQL logic from the domain logic.
    """

    def __init__(self, db_path: str = "main.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Establishes a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        # Return rows as sqlite3.Row objects to access columns by name
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """Creates the necessary tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Create habits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    periodicity TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            # Create habit_completions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habit_completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def add_habit(self, habit: Habit) -> int:
        """Inserts a new habit into the database and returns its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO habits (name, periodicity, created_at)
                    VALUES (?, ?, ?)
                """, (habit.name, habit.periodicity.value, habit.created_at.isoformat()))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Habit with name '{habit.name}' already exists.") from e
    
    def delete_habit(self, habit_id: int):
        """Deletes a habit and its associated completions from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            conn.commit()
    
    def list_habits(self) -> List[Habit]:
        """Retrieves all habits from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits")
            rows = cursor.fetchall()

            habits = []
            for row in rows:
                habits.append(Habit(
                    id=row["id"],
                    name=row["name"],
                    periodicity=Periodicity(row["periodicity"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                ))
            return habits

    def add_habit_completion(self, habit_id: int, completed_at: datetime) -> int:
        """Inserts a new habit completion record into the database and returns its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO habit_completions (habit_id, completed_at)
                VALUES (?, ?)
            """, (habit_id, completed_at.isoformat()))
            conn.commit()
            return cursor.lastrowid

    def list_habit_completions(self, habit_id: int) -> List[HabitCompletion]:
        """Retrieves all completion records for a specific habit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM habit_completions
                WHERE habit_id = ?
                ORDER BY completed_at DESC
            """, (habit_id,))
            rows = cursor.fetchall()

            completions = []
            for row in rows:
                completions.append(HabitCompletion(
                    id=row["id"],
                    habit_id=row["habit_id"],
                    completed_at=datetime.fromisoformat(row["completed_at"])
                ))
            return completions
    
    def list_all_habit_completions(self) -> List[HabitCompletion]:
        """Retrieves all habit completion records from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM habit_completions
                ORDER BY completed_at DESC
            """)
            rows = cursor.fetchall()

            completions = []
            for row in rows:
                completions.append(HabitCompletion(
                    id=row["id"],
                    habit_id=row["habit_id"],
                    completed_at=datetime.fromisoformat(row["completed_at"])
                ))
            return completions


        