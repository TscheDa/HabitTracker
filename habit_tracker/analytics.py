from datetime import datetime, timedelta
from typing import List
from models import Habit, HabitCompletion, Periodicity

def calculate_streak(completions: List[HabitCompletion], periodicity: Periodicity) -> int:
    """
    Calculates the current streak for a given list of completions.
    
    Logic:
    1. Identify 'current' period (today, this week, this month).
    2. If the current period is not completed, check the previous period.
       (A streak isn't broken just because I haven't done it *yet*).
    3. Count backwards in consecutive periods.

    Args:
        completions: A list of HabitCompletion objects.
        periodicity: The periodicity of the habit.

    Returns:
        int: The length of the streak.
    """
    
    if not completions:
        return 0 # No completions means no streak

    now = datetime.now()
    
    if periodicity == Periodicity.DAILY:
        # Create a set of unique completion dates via set comprehension.
        completed_dates = {c.completed_at.date() for c in completions}
        
        streak = 0
        check_date = now.date()

        # If we haven't done it today, check if we did it yesterday.
        # If we didn't do it yesterday, the streak is 0.
        if check_date not in completed_dates:
            check_date -= timedelta(days=1)
            if check_date not in completed_dates:
                return 0

        while check_date in completed_dates:
            streak += 1
            check_date -= timedelta(days=1)
        return streak
    
    elif periodicity == Periodicity.WEEKLY:
        # Create a set of (year, week) tuples and ignore (_) the weekday of isocalendar().
        completed_weeks = set()
        for c in completions:
            year, week, _ = c.completed_at.isocalendar()
            completed_weeks.add((year, week))
        
        streak = 0
        # Start checking from current date.
        check_date = now.date()
        current_year, current_week, _ = check_date.isocalendar()

        # Same logic: if not done this week, check last week
        if (current_year, current_week) not in completed_weeks:
            # Move back one week to safely get the previous ISO week
            check_date -= timedelta(weeks=1)
            current_year, current_week, _ = check_date.isocalendar()
            if (current_year, current_week) not in completed_weeks:
                return 0

        while (current_year, current_week) in completed_weeks:
            streak += 1
            # Safely move to previous week using datetime subtraction
            check_date -= timedelta(weeks=1)
            current_year, current_week, _ = check_date.isocalendar()
        return streak
    
    elif periodicity == Periodicity.MONTHLY:
        # Create set of (year, month) tuples.
        completed_months = {(c.completed_at.year, c.completed_at.month) for c in completions}
        
        streak = 0
        check_date = now.date()
        current_pair = (check_date.year, check_date.month)

        if current_pair not in completed_months:
            # Move to previous month safely (replace day with 1, subtract 1 day)
            check_date = check_date.replace(day=1) - timedelta(days=1)
            current_pair = (check_date.year, check_date.month)
            if current_pair not in completed_months:
                return 0

        while current_pair in completed_months:
            streak += 1
            # Move to previous month
            # Go to first day of current month, then subtract 1 day to get end of prev month
            check_date = check_date.replace(day=1) - timedelta(days=1)
            current_pair = (check_date.year, check_date.month)
        return streak
    
    else:
        raise ValueError("Invalid periodicity")

def longest_ongoing_streak_for_habit(habit: Habit, completions: List[HabitCompletion]) -> int:
    """Wrapper to calculate streak for a specific habit object."""
    return calculate_streak(completions, habit.periodicity)

def longest_ongoing_streak_overall(habits: List[Habit], all_completions: List[HabitCompletion]) -> int:
    """
    Higher-order function to find the max streak across all habits.
    """
    max_streak = 0
    for habit in habits:
        # Filter completions for this specific habit
        habit_completions = [c for c in all_completions if c.habit_id == habit.id]
        streak = calculate_streak(habit_completions, habit.periodicity)
        if streak > max_streak:
            max_streak = streak
    return max_streak

