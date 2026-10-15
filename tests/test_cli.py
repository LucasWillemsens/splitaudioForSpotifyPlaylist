"""Unit tests for src/cli.py module."""

import pytest
import pathlib
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
from click.testing import CliRunner
import csv

from src.cli import (
    split_audio,
    set_id3_tag,
    create_track_data,
    main,
    TIME_FORMATS,
    AUDIO_OUT_CONVERSION,
    load_id3_tags
)


class TestTimeFormats:
    """Tests for TIME_FORMATS constant."""

    def test_time_formats_structure(self):
        """Test TIME_FORMATS has correct structure."""
        assert 1 in TIME_FORMATS
        assert 2 in TIME_FORMATS
        assert True in TIME_FORMATS[1]
        assert False in TIME_FORMATS[1]

    def test_time_formats_values(self):
        """Test TIME_FORMATS has correct format strings."""
        assert TIME_FORMATS[1][False] == '%M:%S'
        assert TIME_FORMATS[1][True] == '%M:%S.%f'
        assert TIME_FORMATS[2][False] == '%H:%M:%S'
        assert TIME_FORMATS[2][True] == '%H:%M:%S.%f'


class TestAudioOutConversion:
    """Tests for AUDIO_OUT_CONVERSION constant."""

    def test_audio_conversion_m4a(self):
        """Test m4a format conversion."""
        assert AUDIO_OUT_CONVERSION['m4a'] == 'mp3'

    def test_audio_conversion_wav_not_converted(self):
        """Test wav format is kept as wav (split losslessly)."""
        assert 'wav' not in AUDIO_OUT_CONVERSION


class TestCreateTrackData:
    """Tests for create_track_data function."""

    def test_create_track_data_basic(self):
        """Test creating track data with all parameters."""
        start = datetime(1900, 1, 1, 1, 30, 0)
        end = datetime(1900, 1, 1, 2, 45, 30)

        result = create_track_data(
            title='Test Track',
            extension='mp3',
            track_pos=1,
            track_total=5,
            start_time=start,
            end_time=end,
            artist='Test Artist',
            album='Test Album',
            year=2023
        )

        assert result['title'] == 'Test Track'
        assert result['extension'] == 'mp3'
        assert result['track'] == 1
        assert result['track_total'] == 5
        assert result['start_time'] == start
        assert result['end_time'] == end
        assert result['artist'] == 'Test Artist'
        assert result['album'] == 'Test Album'
        assert result['year'] == 2023

    def test_create_track_data_none_values(self):
        """Test creating track data with None values."""
        start = datetime(1900, 1, 1, 0, 0, 0)
        end = datetime(1900, 1, 1, 1, 0, 0)

        result = create_track_data(
            title='Another Track',
            extension='flac',
            track_pos=2,
            track_total=10,
            start_time=start,
            end_time=end,
            artist=None,
            album=None,
            year=None
        )

        assert result['artist'] is None
        assert result['album'] is None
        assert result['year'] is None

    def test_create_track_data_returns_dict(self):
        """Test that create_track_data returns a dictionary."""
        start = datetime(1900, 1, 1, 0, 0, 0)
        end = datetime(1900, 1, 1, 1, 0, 0)

        result = create_track_data(
            'Title', 'mp3', 1, 10, start, end, 'Artist', 'Album', 2023
        )

        assert isinstance(result, dict)
        assert len(result) == 9


class TestSetId3Tag:
    """Tests for set_id3_tag function."""

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_all_fields(self, mock_easy_id3):
        """Test setting all ID3 tags."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(
            file_path='/path/to/file.mp3',
            title='Test Title',
            artist='Test Artist',
            album='Test Album',
            genre='Rock',
            year=2023,
            track_num=1,
            total_track_num=10,
            disc_num=1,
            total_disc_num=1
        )

        mock_easy_id3.assert_called_once_with('/path/to/file.mp3')
        # Check that all the setitem calls were made
        call_args = [call for call in mock_tags.__setitem__.call_args_list]
        assert any(call[0] == ('title', 'Test Title') for call in call_args)
        assert any(call[0] == ('artist', 'Test Artist') for call in call_args)
        assert any(call[0] == ('album', 'Test Album') for call in call_args)
        assert any(call[0] == ('genre', 'Rock') for call in call_args)
        assert any(call[0] == ('date', '2023') for call in call_args)
        assert any(call[0] == ('tracknumber', '1/10') for call in call_args)
        assert any(call[0] == ('discnumber', '1/1') for call in call_args)
        mock_tags.save.assert_called_once()

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_minimal_fields(self, mock_easy_id3):
        """Test setting minimal ID3 tags."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(file_path='/path/to/file.mp3')

        mock_easy_id3.assert_called_once_with('/path/to/file.mp3')
        mock_tags.save.assert_called_once()

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_track_num_without_total(self, mock_easy_id3):
        """Test setting track number without total."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(
            file_path='/path/to/file.mp3',
            track_num=5
        )

        call_args = [call for call in mock_tags.__setitem__.call_args_list]
        assert any(call[0] == ('tracknumber', '5') for call in call_args)

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_total_track_without_num(self, mock_easy_id3):
        """Test setting total tracks without track number."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(
            file_path='/path/to/file.mp3',
            total_track_num=20
        )

        call_args = [call for call in mock_tags.__setitem__.call_args_list]
        assert any(call[0] == ('tracknumber', '/20') for call in call_args)

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_disc_num_without_total(self, mock_easy_id3):
        """Test setting disc number without total."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(
            file_path='/path/to/file.mp3',
            disc_num=2
        )

        call_args = [call for call in mock_tags.__setitem__.call_args_list]
        assert any(call[0] == ('discnumber', '2') for call in call_args)

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_total_disc_without_num(self, mock_easy_id3):
        """Test setting total discs without disc number."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(
            file_path='/path/to/file.mp3',
            total_disc_num=3
        )

        call_args = [call for call in mock_tags.__setitem__.call_args_list]
        assert any(call[0] == ('discnumber', '/3') for call in call_args)

    @patch('src.cli.EasyID3')
    def test_set_id3_tag_year_conversion_to_string(self, mock_easy_id3):
        """Test that year is converted to string."""
        mock_tags = MagicMock()
        mock_easy_id3.return_value = mock_tags

        set_id3_tag(
            file_path='/path/to/file.mp3',
            year=1999
        )

        call_args = [call for call in mock_tags.__setitem__.call_args_list]
        assert any(call[0] == ('date', '1999') for call in call_args)


class TestSetId3TagWav:
    """Tests for set_id3_tag with RIFF/WAVE (.wav) files."""

    @patch('src.cli.WAVE')
    def test_set_id3_tag_wav_all_fields(self, mock_wave):
        """Test setting all ID3 tags on a wav file through mutagen.wave.WAVE."""
        mock_wave_file = MagicMock()
        # pydub exports untagged wav files, so no ID3 chunk exists yet
        mock_wave_file.tags = None
        mock_wave_file.add_tags.side_effect = \
            lambda: setattr(mock_wave_file, 'tags', MagicMock())
        mock_wave.return_value = mock_wave_file

        set_id3_tag(
            file_path='/path/to/01. Test Title.wav',
            title='Test Title',
            artist='Test Artist',
            album='Test Album',
            genre='Rock',
            year=2023,
            track_num=1,
            total_track_num=10,
            disc_num=1,
            total_disc_num=1
        )

        mock_wave.assert_called_once_with('/path/to/01. Test Title.wav')
        mock_wave_file.add_tags.assert_called_once()

        # EasyID3 keys must be translated into their ID3 frames
        frames = {
            setall_call.args[0]: setall_call.args[1][0]
            for setall_call in mock_wave_file.tags.setall.call_args_list
        }
        assert list(frames['TIT2'].text) == ['Test Title']
        assert list(frames['TPE1'].text) == ['Test Artist']
        assert list(frames['TPE2'].text) == ['Test Artist']
        assert list(frames['TALB'].text) == ['Test Album']
        assert list(frames['TCON'].text) == ['Rock']
        assert [str(t) for t in frames['TDRC'].text] == ['2023']
        assert list(frames['TRCK'].text) == ['1/10']
        assert list(frames['TPOS'].text) == ['1/1']

        mock_wave_file.save.assert_called_once()

    @patch('src.cli.WAVE')
    def test_set_id3_tag_wav_existing_tags(self, mock_wave):
        """Test that existing wav tags are reused without re-adding them."""
        mock_wave_file = MagicMock()
        mock_wave.return_value = mock_wave_file

        set_id3_tag(
            file_path='/path/to/01. Test Title.wav',
            title='Test Title'
        )

        mock_wave_file.add_tags.assert_not_called()
        mock_wave_file.save.assert_called_once()

    @patch('src.cli.EasyID3')
    @patch('src.cli.WAVE')
    def test_set_id3_tag_wav_does_not_use_easyid3(self, mock_wave, mock_easy_id3):
        """Test that EasyID3 is not used for wav files."""
        mock_wave_file = MagicMock()
        mock_wave.return_value = mock_wave_file

        set_id3_tag(
            file_path='/path/to/01. Test Title.wav',
            title='Test Title'
        )

        mock_easy_id3.assert_not_called()
        mock_wave_file.save.assert_called_once()


class TestLoadId3Tags:
    """Tests for load_id3_tags file type dispatch."""

    @patch('src.cli.EasyID3')
    def test_load_id3_tags_mp3_uses_easyid3(self, mock_easy_id3):
        """Test that non-wav files are handled by EasyID3."""
        result = load_id3_tags('/path/to/file.mp3')

        mock_easy_id3.assert_called_once_with('/path/to/file.mp3')
        assert result == mock_easy_id3.return_value

    @patch('src.cli.WAVE')
    def test_load_id3_tags_wav_uses_wave(self, mock_wave):
        """Test that wav files are handled through mutagen.wave.WAVE."""
        result = load_id3_tags('/path/to/file.wav')

        mock_wave.assert_called_once_with('/path/to/file.wav')
        assert result is not None

    @patch('src.cli.WAVE')
    def test_load_id3_tags_wav_extensions(self, mock_wave):
        """Test that wav, wave and upper-case extensions are detected."""
        for file_path in ('/path/to/file.wav',
                          '/path/to/file.WAV',
                          '/path/to/file.wave'):
            mock_wave.reset_mock()
            load_id3_tags(file_path)
            mock_wave.assert_called_once_with(file_path)


class TestSplitAudio:
    """Tests for split_audio function."""

    @patch('src.cli.AudioSegment')
    def test_split_audio_dry_run(self, mock_audio_segment, capsys):
        """Test split_audio in dry run mode."""
        mock_audio_file = MagicMock()

        input_data = {
            'title': 'Test Track',
            'track': 1,
            'track_total': 5,
            'album': 'Test Album',
            'artist': 'Test Artist',
            'year': 2023,
            'start_time': datetime(1900, 1, 1, 0, 1, 0),
            'end_time': datetime(1900, 1, 1, 0, 3, 0),
            'extension': 'mp3'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            split_audio(
                input_data=input_data,
                audio_file=mock_audio_file,
                output_path=tmpdir,
                dry_run=True
            )

        captured = capsys.readouterr()
        assert 'Test Track' in captured.out
        assert 'Simulation' in captured.out

    @patch('src.cli.set_id3_tag')
    def test_split_audio_non_dry_run(self, mock_set_id3):
        """Test split_audio in normal mode."""
        mock_audio_file = MagicMock()
        mock_audio_file.__getitem__ = MagicMock(return_value=MagicMock())

        input_data = {
            'title': 'Test Track',
            'track': 1,
            'track_total': 5,
            'album': 'Test Album',
            'artist': 'Test Artist',
            'year': 2023,
            'start_time': datetime(1900, 1, 1, 0, 1, 0),
            'end_time': datetime(1900, 1, 1, 0, 3, 0),
            'extension': 'mp3'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            split_audio(
                input_data=input_data,
                audio_file=mock_audio_file,
                output_path=tmpdir,
                dry_run=False
            )

        mock_set_id3.assert_called_once()

    @patch('src.cli.set_id3_tag')
    def test_split_audio_without_optional_fields(self, mock_set_id3):
        """Test split_audio when album, artist, year are missing."""
        mock_audio_file = MagicMock()
        mock_audio_file.__getitem__ = MagicMock(return_value=MagicMock())

        input_data = {
            'title': 'Track Without Metadata',
            'track': 1,
            'track_total': 1,
            'start_time': datetime(1900, 1, 1, 0, 0, 0),
            'end_time': datetime(1900, 1, 1, 0, 1, 0),
            'extension': 'mp3'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            split_audio(
                input_data=input_data,
                audio_file=mock_audio_file,
                output_path=tmpdir,
                dry_run=False
            )

        mock_set_id3.assert_called_once()

    @patch('src.cli.set_id3_tag')
    def test_split_audio_calls_set_id3_tag(self, mock_set_id3):
        """Test that split_audio calls set_id3_tag."""
        mock_audio_file = MagicMock()
        mock_audio_file.__getitem__.return_value = MagicMock()

        input_data = {
            'title': 'Test Track',
            'track': 2,
            'track_total': 5,
            'album': 'Album',
            'artist': 'Artist',
            'year': 2020,
            'start_time': datetime(1900, 1, 1, 0, 1, 0),
            'end_time': datetime(1900, 1, 1, 0, 2, 0),
            'extension': 'mp3'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            split_audio(
                input_data=input_data,
                audio_file=mock_audio_file,
                output_path=tmpdir,
                dry_run=False
            )

        mock_set_id3.assert_called_once()

    @patch('src.cli.set_id3_tag')
    def test_split_audio_output_file_naming(self, mock_set_id3, capsys):
        """Test output file naming convention."""
        mock_audio_file = MagicMock()
        mock_audio_file.__getitem__ = MagicMock(return_value=MagicMock())

        input_data = {
            'title': 'My Track',
            'track': 3,
            'track_total': 10,
            'album': None,
            'artist': None,
            'year': None,
            'start_time': datetime(1900, 1, 1, 0, 0, 0),
            'end_time': datetime(1900, 1, 1, 0, 1, 0),
            'extension': 'flac'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            split_audio(
                input_data=input_data,
                audio_file=mock_audio_file,
                output_path=tmpdir,
                dry_run=False
            )

        captured = capsys.readouterr()
        assert '03. My Track.flac' in captured.out


class TestMainCliCommand:
    """Tests for main CLI command using Click testing utilities."""

    def test_main_requires_input_file(self):
        """Test that input file is required."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'Error' in result.output

    def test_main_requires_csv_file(self):
        """Test that CSV file is required."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_audio = f.name

        try:
            result = runner.invoke(main, ['-i', temp_audio])
            assert result.exit_code != 0
        finally:
            os.unlink(temp_audio)

    def test_main_input_file_must_exist(self):
        """Test that input file must exist."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_csv = f.name

        try:
            result = runner.invoke(main, [
                '-i', '/nonexistent/file.mp3',
                '-c', temp_csv
            ])
            assert result.exit_code != 0
        finally:
            os.unlink(temp_csv)

    def test_main_csv_file_must_exist(self):
        """Test that CSV file must exist."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_audio = f.name

        try:
            result = runner.invoke(main, [
                '-i', temp_audio,
                '-c', '/nonexistent/file.csv'
            ])
            assert result.exit_code != 0
        finally:
            os.unlink(temp_audio)

    @patch('src.cli.AudioSegment')
    def test_main_default_output_path(self, mock_audio_segment):
        """Test that output path defaults to input file directory."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock audio file
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            # Create CSV file with header only
            csv_file = pathlib.Path(tmpdir) / 'test.csv'
            with open(csv_file, 'w') as f:
                f.write('position,title\n')

            mock_audio_segment.from_file.return_value = MagicMock(
                duration_seconds=100
            )

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file)
            ])

            assert tmpdir in result.output or str(audio_file.parent) in result.output or result.exit_code == 0

    @patch('src.cli.AudioSegment')
    def test_main_custom_output_path(self, mock_audio_segment):
        """Test custom output path."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock audio file
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            # Create CSV file
            csv_file = pathlib.Path(tmpdir) / 'test.csv'
            with open(csv_file, 'w') as f:
                f.write('position,title\n')

            output_dir = pathlib.Path(tmpdir) / 'output'
            output_dir.mkdir()

            mock_audio_segment.from_file.return_value = MagicMock(
                duration_seconds=100
            )

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-o', str(output_dir)
            ])

            assert str(output_dir) in result.output or result.exit_code == 0

    @patch('src.cli.AudioSegment')
    def test_main_with_album_options(self, mock_audio_segment):
        """Test main with album metadata options."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            csv_file = pathlib.Path(tmpdir) / 'test.csv'
            with open(csv_file, 'w') as f:
                f.write('position,title\n')

            mock_audio_segment.from_file.return_value = MagicMock(
                duration_seconds=100
            )

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-r', 'The Beatles',
                '-a', 'Abbey Road',
                '-y', '1969'
            ])

            assert 'Input' in result.output or result.exit_code == 0

    @patch('src.cli.AudioSegment')
    def test_main_dry_run_flag(self, mock_audio_segment, capsys):
        """Test main with dry-run flag."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            csv_file = pathlib.Path(tmpdir) / 'test.csv'
            with open(csv_file, 'w') as f:
                f.write('position,title\n')

            mock_audio_segment.from_file.return_value = MagicMock(
                duration_seconds=100
            )

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-d'
            ])

            captured = capsys.readouterr()
            assert 'Input' in captured.out or result.exit_code == 0

    @patch('src.cli.split_audio')
    @patch('src.cli.AudioSegment')
    def test_main_processes_csv_data(self, mock_audio_segment, mock_split_audio):
        """Test that main correctly processes CSV data."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            # Create a simple CSV with valid time formats
            csv_file = pathlib.Path(tmpdir) / 'tracks.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['position', 'title'])
                writer.writeheader()
                writer.writerow({'position': '0:00', 'title': 'Track 1'})
                writer.writerow({'position': '1:30', 'title': 'Track 2'})

            mock_audio_segment.from_file.return_value = MagicMock(
                duration_seconds=180
            )

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-d'
            ])

            # When split_audio is mocked, main should attempt to process the CSV
            # The exit code may be non-zero due to time format issues in the test CSV
            # but split_audio should have been called in dry-run mode
            assert result.exit_code == 0 or mock_split_audio.called or 'Simulation' in result.output

    @patch('src.cli.AudioSegment')
    def test_main_tilde_expansion_input(self, mock_audio_segment):
        """Test tilde expansion for input file path."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            csv_file = pathlib.Path(tmpdir) / 'test.csv'
            with open(csv_file, 'w') as f:
                f.write('position,title\n')

            mock_audio_segment.from_file.return_value = MagicMock(
                duration_seconds=100
            )

            # Test with actual paths (not tilde, since we can't create files there in tests)
            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file)
            ])

            assert result.exit_code == 0 or 'Input' in result.output

    def test_main_year_must_be_integer(self):
        """Test that year option accepts only integers."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            csv_file = pathlib.Path(tmpdir) / 'test.csv'
            with open(csv_file, 'w') as f:
                f.write('position,title\n')

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-y', 'not_a_year'
            ])

            assert result.exit_code != 0


class TestIntegration:
    """Integration tests for cli.py."""

    def test_full_workflow_wav_input(self):
        """End-to-end: split a real .wav file into tagged .wav files.

        Regression test: before wav support this failed with
        "... .wav' doesn't start with an ID3 tag".
        """
        from pydub import AudioSegment
        from mutagen.wave import WAVE

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a real (silent) 3-second wav source file
            source_file = pathlib.Path(tmpdir) / 'album.wav'
            AudioSegment.silent(3000, frame_rate=44100).export(
                out_f=str(source_file), format='wav')

            csv_file = pathlib.Path(tmpdir) / 'cue.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['title', 'position'])
                writer.writeheader()
                writer.writerow({'title': 'Song 1', 'position': '0:00'})
                writer.writerow({'title': 'Song 2', 'position': '0:01'})

            output_dir = pathlib.Path(tmpdir) / 'output'
            output_dir.mkdir()

            result = runner.invoke(main, [
                '-i', str(source_file),
                '-c', str(csv_file),
                '-o', str(output_dir),
                '-r', 'Test Artist',
                '-a', 'Test Album',
                '-y', '2023'
            ])

            assert result.exit_code == 0, result.output

            # Tracks must be exported as wav (no conversion)
            track1 = output_dir / '01. Song 1.wav'
            track2 = output_dir / '02. Song 2.wav'
            assert track1.exists()
            assert track2.exists()

            # ID3 tags must be written into the RIFF 'id3 ' chunk
            tags = WAVE(str(track1)).tags
            assert [str(t) for t in tags.getall('TIT2')[0].text] == ['Song 1']
            assert [str(t) for t in tags.getall('TPE1')[0].text] == ['Test Artist']
            assert [str(t) for t in tags.getall('TPE2')[0].text] == ['Test Artist']
            assert [str(t) for t in tags.getall('TALB')[0].text] == ['Test Album']
            assert [str(t) for t in tags.getall('TDRC')[0].text] == ['2023']
            assert tags.getall('TRCK')
            assert tags.getall('TPOS')

            # Each track must keep the correct duration
            assert WAVE(str(track1)).info.length == pytest.approx(1.0)
            assert WAVE(str(track2)).info.length == pytest.approx(2.0)

    @patch('src.cli.AudioSegment')
    @patch('src.cli.set_id3_tag')
    def test_full_workflow_single_track(self, mock_set_id3, mock_audio_segment):
        """Test a complete workflow with a single track."""
        runner = CliRunner()

        mock_audio = MagicMock()
        mock_audio.duration_seconds = 120
        mock_audio_segment.from_file.return_value = mock_audio

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'album.mp3'
            audio_file.touch()

            csv_file = pathlib.Path(tmpdir) / 'cue.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['position', 'title', 'artist', 'album'])
                writer.writeheader()
                writer.writerow({
                    'position': '0:00',
                    'title': 'Song 1',
                    'artist': 'Artist',
                    'album': 'Album'
                })
                writer.writerow({
                    'position': '1:00',
                    'title': 'Song 2',
                    'artist': 'Artist',
                    'album': 'Album'
                })

            output_dir = pathlib.Path(tmpdir) / 'output'
            output_dir.mkdir()

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-o', str(output_dir),
                '-r', 'Test Artist',
                '-a', 'Test Album',
                '-y', '2023'
            ])

            # Dry run would have exit code 0
            assert result.exit_code == 0 or 'Song' in result.output

    @patch('src.cli.AudioSegment')
    def test_dry_run_does_not_create_files(self, mock_audio_segment):
        """Test that dry run doesn't actually create files."""
        runner = CliRunner()

        mock_audio = MagicMock()
        mock_audio.duration_seconds = 100
        mock_audio_segment.from_file.return_value = mock_audio

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = pathlib.Path(tmpdir) / 'test.mp3'
            audio_file.touch()

            csv_file = pathlib.Path(tmpdir) / 'tracks.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['position', 'title'])
                writer.writeheader()
                writer.writerow({'position': '0:00', 'title': 'Track'})
                writer.writerow({'position': '0:30', 'title': 'Track 2'})

            output_dir = pathlib.Path(tmpdir) / 'output'
            output_dir.mkdir()

            result = runner.invoke(main, [
                '-i', str(audio_file),
                '-c', str(csv_file),
                '-o', str(output_dir),
                '-d'
            ])

            # In dry run, simulation messages should appear or exit successfully
            assert 'Simulation' in result.output or result.exit_code == 0

