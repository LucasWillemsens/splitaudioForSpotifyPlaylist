"""Unit tests for src/formatters.py module."""

import pytest
from datetime import timedelta
from src.formatters import strfdelta


class TestStrfdelta:
    """Tests for strfdelta function."""

    def test_strfdelta_days_hours_minutes_seconds(self):
        """Test formatting timedelta with all components."""
        td = timedelta(days=5, hours=3, minutes=30, seconds=45)
        result = strfdelta(td, '$D days $H hours $M minutes $S seconds')
        assert result == '5 days 3 hours 30 minutes 45 seconds'

    def test_strfdelta_zero_timedelta(self):
        """Test formatting zero timedelta."""
        td = timedelta()
        result = strfdelta(td, '$D:$H:$M:$S')
        assert result == '0:0:0:0'

    def test_strfdelta_only_seconds(self):
        """Test formatting timedelta with only seconds."""
        td = timedelta(seconds=45)
        result = strfdelta(td, '$S')
        assert result == '45'

    def test_strfdelta_only_minutes(self):
        """Test formatting timedelta with only minutes."""
        td = timedelta(minutes=30)
        result = strfdelta(td, '$M')
        assert result == '30'

    def test_strfdelta_only_hours(self):
        """Test formatting timedelta with only hours."""
        td = timedelta(hours=5)
        result = strfdelta(td, '$H')
        assert result == '5'

    def test_strfdelta_only_days(self):
        """Test formatting timedelta with only days."""
        td = timedelta(days=10)
        result = strfdelta(td, '$D')
        assert result == '10'

    def test_strfdelta_hours_minutes_seconds(self):
        """Test formatting timedelta without days."""
        td = timedelta(hours=2, minutes=15, seconds=30)
        result = strfdelta(td, '$H:$M:$S')
        assert result == '2:15:30'

    def test_strfdelta_minutes_seconds(self):
        """Test formatting timedelta with minutes and seconds."""
        td = timedelta(minutes=45, seconds=20)
        result = strfdelta(td, '$M:$S')
        assert result == '45:20'

    def test_strfdelta_custom_format(self):
        """Test formatting with custom text and separators."""
        td = timedelta(days=1, hours=6, minutes=30, seconds=15)
        result = strfdelta(td, 'D=$D H=$H M=$M S=$S')
        assert result == 'D=1 H=6 M=30 S=15'

    def test_strfdelta_no_component_markers(self):
        """Test format string without component markers."""
        td = timedelta(hours=2, minutes=30)
        result = strfdelta(td, 'Time: ')
        assert result == 'Time: '

    def test_strfdelta_repeated_components(self):
        """Test format string with repeated component markers."""
        td = timedelta(hours=5, minutes=10)
        result = strfdelta(td, '$H h $H h $M m')
        assert result == '5 h 5 h 10 m'

    def test_strfdelta_large_values(self):
        """Test with large timedelta values."""
        td = timedelta(days=365, hours=23, minutes=59, seconds=59)
        result = strfdelta(td, '$D-$H-$M-$S')
        assert result == '365-23-59-59'

    def test_strfdelta_compound_format(self):
        """Test compound format with multiple separators."""
        td = timedelta(days=2, hours=4, minutes=30, seconds=45)
        result = strfdelta(td, '$Dd $Hh $Mm $Ss')
        assert result == '2d 4h 30m 45s'

    def test_strfdelta_hms_format(self):
        """Test common HH:MM:SS format (hours less than 24)."""
        td = timedelta(hours=23, minutes=59, seconds=59)
        result = strfdelta(td, '$H:$M:$S')
        assert result == '23:59:59'

    def test_strfdelta_one_second(self):
        """Test with one second."""
        td = timedelta(seconds=1)
        result = strfdelta(td, '$S seconds')
        assert result == '1 seconds'

    def test_strfdelta_one_minute(self):
        """Test with one minute."""
        td = timedelta(minutes=1)
        result = strfdelta(td, '$M minutes')
        assert result == '1 minutes'

    def test_strfdelta_one_hour(self):
        """Test with one hour."""
        td = timedelta(hours=1)
        result = strfdelta(td, '$H hours')
        assert result == '1 hours'

    def test_strfdelta_one_day(self):
        """Test with one day."""
        td = timedelta(days=1)
        result = strfdelta(td, '$D days')
        assert result == '1 days'

    def test_strfdelta_60_seconds_equals_1_minute(self):
        """Test that 60 seconds converts correctly."""
        td = timedelta(seconds=60)
        result = strfdelta(td, '$M:$S')
        assert result == '1:0'

    def test_strfdelta_60_minutes_equals_1_hour(self):
        """Test that 60 minutes converts correctly."""
        td = timedelta(minutes=60)
        result = strfdelta(td, '$H:$M')
        assert result == '1:0'

    def test_strfdelta_24_hours_equals_1_day(self):
        """Test that 24 hours converts correctly."""
        td = timedelta(hours=24)
        result = strfdelta(td, '$D:$H')
        assert result == '1:0'

    def test_strfdelta_all_components_format(self):
        """Test format with all components present."""
        td = timedelta(days=7, hours=12, minutes=30, seconds=45)
        result = strfdelta(td, 'Total: $D days, $H hours, $M mins, $S secs')
        assert result == 'Total: 7 days, 12 hours, 30 mins, 45 secs'

    def test_strfdelta_microseconds_ignored(self):
        """Test that microseconds don't affect the result."""
        td1 = timedelta(hours=1, minutes=30, seconds=45)
        td2 = timedelta(hours=1, minutes=30, seconds=45, microseconds=999999)
        result1 = strfdelta(td1, '$H:$M:$S')
        result2 = strfdelta(td2, '$H:$M:$S')
        assert result1 == result2 == '1:30:45'

    def test_strfdelta_leading_zeros_not_applied(self):
        """Test that values are not zero-padded by default."""
        td = timedelta(hours=5, minutes=5, seconds=5)
        result = strfdelta(td, '$H:$M:$S')
        assert result == '5:5:5'

    def test_strfdelta_single_digit_values(self):
        """Test with single digit values."""
        td = timedelta(days=1, hours=2, minutes=3, seconds=4)
        result = strfdelta(td, '$D $H $M $S')
        assert result == '1 2 3 4'

    def test_strfdelta_double_digit_values(self):
        """Test with double digit values."""
        td = timedelta(days=10, hours=11, minutes=12, seconds=13)
        result = strfdelta(td, '$D $H $M $S')
        assert result == '10 11 12 13'

    def test_strfdelta_mixed_digit_values(self):
        """Test with mixed single and double digit values."""
        td = timedelta(days=5, hours=10, minutes=3, seconds=45)
        result = strfdelta(td, '$D $H $M $S')
        assert result == '5 10 3 45'
