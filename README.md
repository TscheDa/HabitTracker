# HabitTracker

A command-line interface (CLI) application for tracking personal habits, built with Python 3.12, SQLite, and Questionary. It allows users to create, manage, and analyze habits with different periodicities (daily, weekly, monthly), track completions, and calculate streaks.

## Features

- **Habit Management**: Create, list, and delete habits with customizable periodicities (daily, weekly, monthly).
- **Completion Tracking**: Mark habits as completed on specific dates.
- **Streak Analysis**:
  - Calculate current streaks (ongoing from today backwards).
  - Find all-time longest streaks for each habit.
- **Data Persistence**: Uses SQLite database for storing habits and completions.
- **CLI Interface**: Interactive menu-driven interface using `questionary` for user input.
- **Sample Data**: Automatically seeds the database with sample habits and completions on first run.
- **Comprehensive Testing**: Unit tests for analytics functions.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/TscheDa/HabitTracker.git
   cd HabitTracker
   ```

2. **Install Dependencies**:
   The project uses Python's standard library and `questionary` for the CLI. Install via pip:
   ```bash
   pip install questionary
   ```
   Or, if using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install questionary
   ```

3. **Run the Application**:
   From the project root:
   ```bash
   python -m habit_tracker.main
   ```
   This will seed the database with sample data on the first run and launch the CLI.

## Usage

The application provides an interactive CLI menu with the following options:

- **Create a Habit**: Add a new habit by specifying name and periodicity.
- **Complete a Habit**: Mark a habit as completed for today.
- **Analyze Habits**: View various analytics, including:
  - List all habits.
  - List habits by periodicity.
  - List all completions.
  - View current streaks for each habit.
  - View all-time longest streaks for each habit.
- **Edit a Habit**: Update the name and/or periodicity of a habit.
- **Delete a Habit**: Remove a habit and its associated completions.
- **Exit**: Quit the application.

### Example Workflow
1. Run the app: `python -m habit_tracker.main`
2. Choose "Create a Habit" and add "Exercise" as daily.
3. Choose "Complete a Habit" and select "Exercise".
4. Choose "Analyze Habits" > "Return the current streak for each habit" to see your streak.

## Project Structure

```
HabitTracker/
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── habit_tracker/
│   ├── __init__.py
│   ├── analytics.py       # Streak calculation functions
│   ├── db.py              # Database operations (HabitRepository)
│   ├── main.py            # CLI interface and main logic
│   └── models.py          # Data models (Habit, HabitCompletion, Periodicity)
└── tests/
    ├── __init__.py
    ├── test_analytics.py  # Unit tests for analytics
    ├── test_db.py  # Unit tests for database operations
```

- **models.py**: Defines data classes for `Habit`, `HabitCompletion`, and `Periodicity` enum.
- **db.py**: `HabitRepository` class handles SQLite database interactions, including CRUD operations.
- **analytics.py**: Functions to calculate streaks (`calculate_streak` for current, `get_streak_details` for longest).
- **main.py**: Entry point with CLI logic, using `questionary` for prompts.
- **tests/**: Unit tests using pytest.

## Database Schema

- **habits** table: Stores habit details (id, name, periodicity, created_at).
- **habit_completions** table: Stores completion records (id, habit_id, completed_at), with foreign key to habits.

The database file (`main.db`) is created automatically in the project root.

## Testing

Run tests with pytest:
```bash
pytest
```

Tests cover:
- Streak calculations for daily, weekly, and monthly habits.
- Database operations.
- Edge cases like empty data or multiple completions in the same period.

## Dependencies

- Python 3.12+
- `questionary` (for CLI prompts)
- SQLite (built-in with Python)
