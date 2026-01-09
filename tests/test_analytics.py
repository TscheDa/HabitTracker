import pytest
from datetime import datetime, timedelta
from habit_tracker.models import HabitCompletion, Periodicity
from habit_tracker.analytics import calculate_streak, get_streak_details

# Helper function to generate completion objects quickly
def create_completions(dates):
    return [HabitCompletion(habit_id=1, completed_at=date) for date in dates]

class TestDailyStreaks:
    def test_empty_list(self):
        assert calculate_streak([], Periodicity.DAILY) == 0

    def test_single_day_today(self):
        dates = [datetime.now()]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.DAILY) == 1
    
    def test_streak_3_consecutive_days(self):
        # Today, Yesterday, Day before Yesterday
        dates = [datetime.now() - timedelta(days=i) for i in range(3)]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.DAILY) == 3

    def test_streak_broken(self):
        # Today, Day before Yesterday (missing Yesterday)
        dates = [datetime.now(), datetime.now() - timedelta(days=2)]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.DAILY) == 1
    
    def test_streak_continues_if_today_missing_but_yesterday_done(self):
        # Yesterday, Day before Yesterday
        dates = [datetime.now() - timedelta(days=i) for i in range(1, 3)]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.DAILY) == 2
    
class TestWeeklyStreaks:
    def test_empty_list(self):
        assert calculate_streak([], Periodicity.WEEKLY) == 0
    
    def test_weekly_consecutive_simple(self):
        # This week and last week
        now = datetime.now()
        last_week = now - timedelta(weeks=1)
        dates = [now, last_week]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.WEEKLY) == 2

    def test_weekly_multiple_in_same_week(self):
        # Multiple completions in the same week should count as one
        # Ensure dates are actually same ISO week for the logic to hold
        now = datetime.now()
        d1 = now # e.g. Friday
        d2 = now - timedelta(days=1) # e.g. Thursday
        d3 = now - timedelta(weeks=1) # e.g. Friday last week

        # Edge case: If 'now' is Monday and '1 day ago' is Sunday, they fall in different weeks.
        # But now d2 and d3 are within the same week, so the test still holds.
        
        dates = [d1, d2, d3]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.WEEKLY) == 2
    
    def test_weekly_streak_broken(self):
        # This week and two weeks ago (missing last week)
        now = datetime.now()
        two_weeks_ago = now - timedelta(weeks=2)
        dates = [now, two_weeks_ago]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.WEEKLY) == 1

    def test_streak_over_new_year(self):
        # Last week of previous year and first week of current year
        d1 = datetime(2023, 12, 31)  # Sunday, last week of 2023
        d2 = datetime(2024, 1, 1)    # Monday, first week of 2024
        dates = [d1, d2]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.WEEKLY, datetime(2024, 1, 2)) == 2
    
class TestMonthlyStreaks:
    def test_empty_list(self):
        assert calculate_streak([], Periodicity.MONTHLY) == 0
    
    def test_monthly_consecutive_simple(self):
        # This month and last month
        now = datetime.now()
        last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=15)  # 15th of last month
        dates = [now, last_month]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.MONTHLY) == 2

    def test_monthly_multiple_in_same_month(self):
        # Multiple completions in the same month should count as one
        d1 = datetime(2024, 6, 5)
        d2 = datetime(2024, 6, 15)
        d3 = datetime(2024, 6, 25)
        dates = [d1, d2, d3]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.MONTHLY, datetime(2024, 6, 26)) == 1
    
    def test_monthly_streak_broken(self):
        # This month and two months ago (missing last month)
        now = datetime.now()
        two_months_ago = (now.replace(day=1) - timedelta(days=32)).replace(day=15)  # 15th of two months ago
        dates = [now, two_months_ago]
        completions = create_completions(dates)
        assert calculate_streak(completions, Periodicity.MONTHLY) == 1

class TestStreakDetails:
    def test_daily_streak_details(self):
        now = datetime.now()
        dates = [now - timedelta(days=i) for i in range(3)]  # 3-day streak
        completions = create_completions(dates)
        streak, start, end = get_streak_details(completions, Periodicity.DAILY)
        assert streak == 3
        assert start == (now - timedelta(days=2)).date()
        assert end == now.date()

    def test_weekly_streak_details(self):
        now = datetime.now()
        last_week = now - timedelta(weeks=1)
        dates = [now, last_week]  # 2-week streak
        completions = create_completions(dates)
        streak, start, end = get_streak_details(completions, Periodicity.WEEKLY)
        assert streak == 2
        assert start.isocalendar()[:2] == (last_week.isocalendar()[0], last_week.isocalendar()[1])
        assert end.isocalendar()[:2] == (now.isocalendar()[0], now.isocalendar()[1])
    
    def test_monthly_streak_details(self):
        now = datetime.now()
        last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=15)
        dates = [now, last_month]  # 2-month streak
        completions = create_completions(dates)
        streak, start, end = get_streak_details(completions, Periodicity.MONTHLY)
        assert streak == 2
        assert (start.year, start.month) == (last_month.year, last_month.month)
        assert (end.year, end.month) == (now.year, now.month)

    def test_get_streak_details_history_gap(self):
        # 42 days streak in the past, then a break, then 1 day today.
        # Max streak should be 42.
        base = datetime(2023, 1, 1)
        dates = [base + timedelta(days=i) for i in range (42)]
        dates.append(datetime.now())  # Today's completion
        completions = create_completions(dates)
        
        count, start, end = get_streak_details(completions, Periodicity.DAILY)
        assert count == 42
        assert start == base.date()
        assert end == (base + timedelta(days=41)).date()