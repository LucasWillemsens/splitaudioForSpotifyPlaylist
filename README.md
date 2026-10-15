# splitaudio
Split a single audio file into separate tracks using a CSV cue list.

This repository provides a small CLI (and optional Tkinter GUI) that
parses a CSV of track start positions and titles, extracts each track from
the source audio file, exports each track to a numbered file, and writes
basic ID3 tags using `mutagen`.

**Key behaviours**
- Input audio type is detected from the input file suffix (e.g. `.mp3`, `.m4a`).
- `m4a` inputs are exported as `mp3` by default (see `AUDIO_OUT_CONVERSION`).
- Default output directory is the input file's parent directory.
- Paths beginning with `~` are expanded.
- Output files are named using the pattern: `01. Title.ext` (two-digit track
  number, a period, a space, then the track title and extension).
- Basic ID3 tags are written (title, track number, disc number, artist,
  album and date when provided).

## Dependencies
- Python 3.12+
- `pydub` (for audio slicing)
- `mutagen` (for ID3 tag writing; the app uses `mutagen.easyid3.EasyID3`)
- `click` (CLI)
- System requirement: `ffmpeg` or `libav` for reading/writing non-WAV formats
  (required by `pydub`).
- Optional (GUI): Tkinter (typically bundled with Python, but not always)

Dependencies are managed with Poetry. Python 3.12 or newer is required.

### Recommended: install as a CLI tool (usable from any shell)

With [uv](https://docs.astral.sh/uv/), the commands are installed in an
isolated environment and placed on `PATH`:

```bash
uv tool install .
```

(If the default interpreter is older than 3.12, select one explicitly, e.g.
`uv tool install --python 3.12 .` — uv downloads a managed Python if needed.)

This installs both the `splitaudio` and `splitaudio-gui` executables into
`~/.local/bin`. After changing the source code, refresh the installed tool
by re-running the same command with `--force`.

### With Poetry (development)

```bash
poetry install
```

This creates an isolated virtualenv; the CLI is *not* placed on `PATH`
by itself. Run it through Poetry:

```bash
poetry run splitaudio --help
```

or activate the environment first (`poetry shell`) and then run
`splitaudio` directly.

### With pip

Requires Python 3.12+ (check with `python3 --version`):

```bash
pip install -e .
```

If the default `pip` belongs to an older Python, use
`python3.12 -m pip install -e .` (or newer) instead.

Install `ffmpeg` on Debian/Ubuntu:

```bash
sudo apt-get install ffmpeg
```

## CSV format

The CSV may use any delimiter; the app auto-detects the CSV dialect.
It expects a header row. Required and optional columns:

- `title` (required): Track title to apply to the split file.
- `position` (required): The start time for that track in the source file.
  Time formats supported:
  - `MM:SS` or `MM:SS.fff` (minutes:seconds, optional milliseconds)
  - `HH:MM:SS` or `HH:MM:SS.fff` (hours:minutes:seconds, optional
    milliseconds)

Optional columns (per-row values override CLI args when present):
- `artist` — track artist
- `album`  — track album
- `year`   — track year (applied to ID3 `date` tag)

Example CSV (minimal):

```csv
title,position
Intro,0:00
First Track,3:12
Second Track,7:41
```

Example CSV (with optional fields):

```csv
title,position,artist,album,year
Intro,0:00,My Artist,My Album,2021
First Track,3:12,My Artist,My Album,2021
```

> If there are for example comma's (,) contained within a song title, try using
> a pipe (|) as the separator.

## Command-line usage

After installing (e.g. with `uv tool install .`, or inside an activated
Poetry environment), the CLI is available as `splitaudio`:

```bash
splitaudio -i /path/to/source.mp3 -c /path/to/tracks.csv [-o /out/dir] [-r ARTIST] [-a ALBUM] [-y YEAR] [-d]
```

Options summary:
- `-i, --input` : Path to the source audio file.
- `-c, --csv`   : Path to the CSV file containing `title` and `position`.
- `-o, --output`: Output directory (defaults to the input file's parent).
- `-r, --artist`: Album artist to apply when per-row `artist` is not present.
- `-a, --album` : Album title to apply when per-row `album` is not present.
- `-y, --year`  : Album year to apply when per-row `year` is not present.
- `-d, --dryrun`: Perform a simulation without writing files.

## GUI usage (Tkinter)

Launch the GUI with:

```bash
splitaudio-gui
```

If Tkinter is not available, the GUI launcher falls back to a CLI mode that
accepts the same arguments (note the `--dry-run` flag spelling in this mode):

```bash
splitaudio-gui --input album.m4a --csv tracks.csv --output ./out --artist "Artist" --album "Album" --year 2020 --dry-run
```

## What the app does
- Loads the source audio via `pydub.AudioSegment.from_file` using the input's
  file suffix to select the format.
- Reads the entire CSV, counts non-empty lines to determine total tracks
  (used for `tracknumber` ID3 tag formatting).
- Iterates rows: for each row, parses `position` into a `datetime` using one
  of the supported time formats (handles optional milliseconds). Each row's
  `position` becomes the start time of the track; the next row's position
  becomes the end time. The final track's end time is the audio file
  duration.
- Slices audio in milliseconds and exports each track to a file named
  `NN. Title.ext` where `ext` is the audio output type (converted for
  certain inputs, e.g. `m4a` -> `mp3`).
- Exports include basic tags (`title`, `tracknumber`, `discnumber`, and
  `artist`/`album`/`date` if provided). After export the app calls
  `mutagen.easyid3.EasyID3` to ensure ID3 tags are written correctly.

### Examples

Dry-run (simulate extraction, print what would be done):

```bash
splitaudio -i album.m4a -c tracks.csv -d
```

Split with output directory and album metadata:

```bash
splitaudio -i album.mp3 -c tracks.csv -o ./out -r "Artist Name" -a "Album Title" -y 2020
```

## Notes & gotchas
- The CSV header must include `title` and `position` (case-sensitive).
- Time parsing depends on the number of `:` in the `position` value:
  one colon -> treated as `MM:SS[.fff]`, two colons -> `HH:MM:SS[.fff]`.
- The app uses whole seconds and milliseconds computed from the parsed
  times; extremely large durations or unusual timestamp formats may fail.
- `ffmpeg` must be installed and available in `PATH` for `pydub` to handle
  non-WAV formats such as MP3 or M4A.
