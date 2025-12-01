"""
ServerCounter - Count active servers during specific time windows.

Uses TimeEntries data to determine how many servers were working
during each 15-minute timeslot.
"""

from datetime import datetime, time, timedelta
from typing import List

from pipeline.models.time_entry_dto import TimeEntryDTO


class ServerCounter:
    """
    Counts active servers during specific time windows.

    Uses clock-in/out times from TimeEntries to determine staffing levels.
    """

    @classmethod
    def count_active_servers(
        cls,
        time_entries: List[TimeEntryDTO],
        window_start: datetime,
        window_end: datetime
    ) -> int:
        """
        Count servers actively clocked in during a time window.

        Args:
            time_entries: List of time entry DTOs for the day
            window_start: Start of time window (datetime)
            window_end: End of time window (datetime)

        Returns:
            Number of servers clocked in during this window
        """
        if not time_entries:
            return 0

        active_servers = [
            entry for entry in time_entries
            if entry.is_server and cls._is_working_during_window(entry, window_start, window_end)
        ]

        return len(active_servers)

    @classmethod
    def count_active_cooks(
        cls,
        time_entries: List[TimeEntryDTO],
        window_start: datetime,
        window_end: datetime
    ) -> int:
        """
        Count cooks actively clocked in during a time window.

        Args:
            time_entries: List of time entry DTOs for the day
            window_start: Start of time window (datetime)
            window_end: End of time window (datetime)

        Returns:
            Number of cooks clocked in during this window
        """
        if not time_entries:
            return 0

        active_cooks = [
            entry for entry in time_entries
            if entry.is_cook and cls._is_working_during_window(entry, window_start, window_end)
        ]

        return len(active_cooks)

    @classmethod
    def count_all_active_staff(
        cls,
        time_entries: List[TimeEntryDTO],
        window_start: datetime,
        window_end: datetime
    ) -> int:
        """
        Count all staff actively clocked in during a time window.

        Args:
            time_entries: List of time entry DTOs for the day
            window_start: Start of time window (datetime)
            window_end: End of time window (datetime)

        Returns:
            Number of staff members clocked in during this window
        """
        if not time_entries:
            return 0

        active_staff = [
            entry for entry in time_entries
            if cls._is_working_during_window(entry, window_start, window_end)
        ]

        return len(active_staff)

    @staticmethod
    def _is_working_during_window(
        entry: TimeEntryDTO,
        window_start: datetime,
        window_end: datetime
    ) -> bool:
        """
        Check if employee was working during the specified window.

        An employee is considered working if their shift overlaps with the window.

        Args:
            entry: Time entry DTO
            window_start: Start of time window
            window_end: End of time window

        Returns:
            True if employee's shift overlaps with the window
        """
        # Check if clock-in is before window ends
        if entry.clock_in_datetime >= window_end:
            return False

        # Check if clock-out (if exists) is after window starts
        if entry.clock_out_datetime is not None:
            if entry.clock_out_datetime <= window_start:
                return False

        # Shift overlaps with window
        return True

    @classmethod
    def get_staffing_summary(
        cls,
        time_entries: List[TimeEntryDTO],
        window_start: datetime,
        window_end: datetime
    ) -> dict:
        """
        Get detailed staffing breakdown for a time window.

        Args:
            time_entries: List of time entry DTOs for the day
            window_start: Start of time window
            window_end: End of time window

        Returns:
            Dict with server count, cook count, and total staff count
        """
        return {
            'servers': cls.count_active_servers(time_entries, window_start, window_end),
            'cooks': cls.count_active_cooks(time_entries, window_start, window_end),
            'total_staff': cls.count_all_active_staff(time_entries, window_start, window_end)
        }
