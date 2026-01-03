import questionary
from datetime import datetime, timedelta
import random
from typing import List

# Importing models and database functions
from models import Habit, HabitCompletion, Periodicity
from db import HabitRepository
import analytics

def seed_data(repo: HabitRepository):
    """
    Populates the database with 5 predefined habits and 4 weeks of sample data,
    if the database is currently empty.
    """
    existing_habits = repo.list_habits()
    if existing_habits:
        return # Database already has data, skips seeding.
    print("Seeding database with sample data...")

    # 1. Define 5 sample habits:
    sample_habits = [
        Habit(name="Exercise", periodicity=Periodicity.DAILY, created_at=datetime.now()),
        Habit(name="Code Python for 30 Mins", periodicity=Periodicity.DAILY, created_at=datetime.now()),
        Habit(name="Read a Book", periodicity=Periodicity.DAILY, created_at=datetime.now()),
        Habit(name="Go for a Run", periodicity=Periodicity.WEEKLY, created_at=datetime.now()),
        Habit(name="Clean Apartment", periodicity=Periodicity.WEEKLY, created_at=datetime.now()),
    ]

    # 2. Add habits to the database and generate completion data:
    for habit in sample_habits:
        habit_id = repo.add_habit(habit)

        # Generate 4 weeks of completion data
        start_date = datetime.now() - timedelta(weeks=4)

        # Logic to randomly mark completions
        for day_offset in range(29): # 4 weeks + 1 day
            current_date = start_date + timedelta(days=day_offset)

            should_complete = False
            if habit.periodicity == Periodicity.DAILY:
                # 70% chance to complete daily habits
                should_complete = random.random() < 0.7
            
            elif habit.periodicity == Periodicity.WEEKLY:
                # Random chance everyday, but with lower 20 % probability
                should_complete = random.random() < 0.2
            
            elif habit.periodicity == Periodicity.MONTHLY:
                # Random chance everyday, but with lower 10 % probability
                should_complete = random.random() < 0.1
            
            if should_complete:
                repo.add_habit_completion(habit_id, current_date)

    print("Database seeded successfully.")

def cli():
    """
    Main entry point for the Command Line Interface (CLI) of the Habit Tracker application.
    """
    repo = HabitRepository()
    repo.create_tables()
    seed_data(repo)

    print("Welcome to the Habit Tracker CLI!")

    while True:
        # Main menu options
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Create a new Habit",
                "Check off a Habit as completed",
                "Analyze Habits",
                "Delete a Habit",
                "Exit"
            ]
        ).ask()

        if choice == "Create a new Habit":
            name = questionary.text("What habit would you like to create?").ask()
            if not name:
                print("Habit name cannot be empty.")
                continue
            periodicity_str = questionary.select(
                "How often do you want to perform this habit?",
                choices=["DAILY", "WEEKLY", "MONTHLY"]
            ).ask()

            periodicity = Periodicity(periodicity_str)
            new_habit = Habit(name=name, periodicity=periodicity, created_at=datetime.now())

            try:
                repo.add_habit(new_habit)
                print(f"Habit '|{name}|' created successfully!")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "Check off a Habit as completed":
            habits = repo.list_habits()
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

            # Create a list of habit names for selection
            habit_names = [habit.name for habit in habits]
            selected_habit_name = questionary.select(
                "Which habit did you complete?",
                choices=habit_names
            ).ask()

            # Find the selected habit with next() for efficiency
            # next() ensures we get the first match or None combined with a generator expression
            selected_habit = next((h for h in habits if h.name == selected_habit_name), None)
            
            if selected_habit:
                repo.add_habit_completion(selected_habit.id, datetime.now())
                print(f"Habit '|{selected_habit.name}|' marked as completed for today.")
        
        elif choice == "Analyze Habits":
            analysis_choice = questionary.select(
                "What would you like to analyze?",
                choices=[
                    "Return a list with all currently tracked habits",
                    "Return a list of all habits with the same periodicity",
                    "Return a list of all habit completions", # Added for debugging/conpleteness
                    "Return the longest run streak for a given habit",
                    "Return the longest run streak of all defined habits",
                    "Return the all-time longest streak for each habit", # New option
                    "Back"
                ]
            ).ask()

            if analysis_choice == "Return a list with all currently tracked habits":
                habits = repo.list_habits()
                if not habits:
                    print("No habits found.")
                else:
                    print("Currently tracked habits:")
                    for habit in habits:
                        print(f"- {habit.name} (Periodicity: {habit.periodicity.value}, Created At: {habit.created_at.date()})")
            
            elif analysis_choice == "Return a list of all habits with the same periodicity":
                periodicity_str = questionary.select(
                    "Select periodicity to filter habits:",
                    choices=["DAILY", "WEEKLY", "MONTHLY"]
                ).ask()
                periodicity = Periodicity(periodicity_str)
                habits = repo.list_habits()
                filtered_habits = [h for h in habits if h.periodicity == periodicity]
                if not filtered_habits:
                    print(f"No habits found with periodicity '{periodicity.value}'.")
                else:
                    print(f"Habits with periodicity {periodicity.value}:")
                    for habit in filtered_habits:
                        print(f"- {habit.name} (Created At: {habit.created_at.date()})")
            
            elif analysis_choice == "Return a list of all habit completions":
                completions = repo.list_all_habit_completions()
                if not completions:
                    print("No habit completions found.")
                else:
                    print("All habit completions:")
                    for completion in completions:
                        print(f"- Habit ID: {completion.habit_id}, Completed At: {completion.completed_at}")
            
            elif analysis_choice == "Return the longest run streak for a given habit":
                habits = repo.list_habits()
                if not habits:
                    print("No habits found. Please create a habit first.")
                    continue

                habit_names = [habit.name for habit in habits]
                selected_habit_name = questionary.select(
                    "Select a habit to analyze its longest streak:",
                    choices=habit_names
                ).ask()

                selected_habit = next((h for h in habits if h.name == selected_habit_name), None)
                
                if selected_habit:
                    completions = repo.list_habit_completions(selected_habit.id)
                    longest_streak = analytics.longest_ongoing_streak_for_habit(selected_habit, completions)
                    print(f"The longest streak for habit '|{selected_habit.name}|' is {longest_streak}.")
            
            elif analysis_choice == "Return the longest run streak of all defined habits":
                habits = repo.list_habits()
                if not habits:
                    print("No habits found. Please create a habit first.")
                    continue

                print("Longest run streak of all defined habits:")
                for habit in habits:
                    completions = repo.list_habit_completions(habit.id)
                    longest_streak = analytics.longest_ongoing_streak_for_habit(habit, completions)
                    print(f"- {habit.name}: {longest_streak} - {habit.periodicity.value}")
            
            elif analysis_choice == "Return the all-time longest streak for each habit":
                habits = repo.list_habits()
                if not habits:
                    print("No habits found.")
                    continue

                print("\nAll-time longest streaks for each habit:")
                for habit in habits:
                    completions = repo.list_habit_completions(habit.id)
                    streak, start, end = analytics.get_streak_details(completions, habit.periodicity)
                    
                    if streak > 0:
                        start_str = start.strftime("%Y-%m-%d") if start else "N/A"
                        end_str = end.strftime("%Y-%m-%d") if end else "N/A"
                        print(f"- {habit.name}: {streak} (from {start_str} to {end_str}) - {habit.periodicity.value}")
                    else:
                        print(f"- {habit.name}: No streak yet")
                print("") # Add a blank line for readability

            elif analysis_choice == "Back":
                continue

        elif choice == "Delete a Habit":
            habits = repo.list_habits()
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

            habit_names = [habit.name for habit in habits]
            selected_habit_name = questionary.select(
                "Select a habit to delete:",
                choices=habit_names
            ).ask()

            selected_habit = next((h for h in habits if h.name == selected_habit_name), None)
            
            if selected_habit:
                repo.delete_habit(selected_habit.id)
                print(f"Habit '|{selected_habit.name}|' and its completions have been deleted.")

        elif choice == "Exit":
            print("Exiting Habit Tracker CLI. Goodbye!")
            break

if __name__ == "__main__":
    cli()

