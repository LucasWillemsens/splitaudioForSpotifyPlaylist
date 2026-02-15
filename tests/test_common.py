"""Unit tests for src/common.py module."""

from src.common import AUDIO_OUT_CONVERSION, TIME_FORMATS


class TestAudioOutConversion:
    """Tests for AUDIO_OUT_CONVERSION constant."""

    def test_audio_out_conversion_has_expected_mapping(self):
        assert AUDIO_OUT_CONVERSION["m4a"] == "mp3"

    def test_audio_out_conversion_keys_and_values_are_strings(self):
        assert all(isinstance(k, str) for k in AUDIO_OUT_CONVERSION.keys())
        assert all(isinstance(v, str) for v in AUDIO_OUT_CONVERSION.values())


class TestTimeFormats:
    """Tests for TIME_FORMATS constant."""

    def test_time_formats_has_expected_top_level_keys(self):
        assert set(TIME_FORMATS.keys()) == {1, 2}

    def test_time_formats_has_true_false_subkeys(self):
        assert set(TIME_FORMATS[1].keys()) == {True, False}
        assert set(TIME_FORMATS[2].keys()) == {True, False}

    def test_time_formats_values(self):
        assert TIME_FORMATS[1][False] == "%M:%S"
        assert TIME_FORMATS[1][True] == "%M:%S.%f"
        assert TIME_FORMATS[2][False] == "%H:%M:%S"
        assert TIME_FORMATS[2][True] == "%H:%M:%S.%f"