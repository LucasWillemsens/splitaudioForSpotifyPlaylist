#!/usr/bin/env python3
import pathlib
import click
from datetime import datetime, timedelta
import csv
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3

try:
    # When imported as part of a package (preferred)
    from .common import TIME_FORMATS, AUDIO_OUT_CONVERSION
except ImportError:
    # When run/imported as a flat module (e.g. `import cli`)
    from common import TIME_FORMATS, AUDIO_OUT_CONVERSION


def split_audio(input_data: dict = [],
                audio_file: AudioSegment = None,
                output_path: str = None,
                dry_run: bool = False):
    track_title = input_data['title']
    track_pos = input_data['track']
    track_total = input_data['track_total']
    track_album = input_data['album'] if 'album' in input_data else None
    track_artist = input_data['artist'] if 'artist' in input_data else None
    track_year = input_data['year'] if 'year' in input_data else None
    track_start_time = input_data['start_time']
    track_end_time = input_data['end_time']
    track_extension = input_data['extension']
    # file_path = input_data['file_path']

    print('Title:', track_title)
    print('  Start:', datetime.strftime(track_start_time, '%H:%M:%S'))
    print('  End:', datetime.strftime(track_end_time, '%H:%M:%S'))

    duration = (track_end_time - track_start_time)
    print('  Duration:', str(duration))

    output_file = "{0}/{1:02d}. {2}.{3}".format(output_path,
                                           track_pos,
                                           track_title,
                                           track_extension)
    print("  Output: {0}".format(output_file))

    if dry_run:
        print("Simulation: Extracting audio part from time position '{0}' "
              "for the duration of '{1}' into file '{2}.{3}'"
              .format(datetime.strftime(track_start_time, '%H:%M:%S'),
                      str(duration),
                      track_title,
                      track_extension))
    else:
        start_delta = timedelta(hours=track_start_time.hour,
                                minutes=track_start_time.minute,
                                seconds=track_start_time.second,
                                microseconds=track_start_time.microsecond)
        end_delta = timedelta(hours=track_end_time.hour,
                              minutes=track_end_time.minute,
                              seconds=track_end_time.second,
                              microseconds=track_end_time.microsecond)

        start_ms = (start_delta.seconds * 1000)
        end_ms = (end_delta.seconds * 1000)

        if start_ms > 0:
            audio_track = audio_file[int(start_ms):]
        else:
            audio_track = audio_file

        audio_track_final = audio_track[:(end_ms-start_ms)]

        track_tags = {
            'title': track_title,
            'tracknumber': str(track_pos),
            'discnumber': '1'
        }
        if track_album:
            track_tags['album'] = track_album
        if track_artist:
            track_tags['artist'] = track_artist
            track_tags['albumartist'] = track_artist
        if track_year:
            track_tags['date'] = str(track_year)

        audio_track_final.export(out_f=output_file,
                                 format=track_extension,
                                 tags=track_tags)

        set_id3_tag(
            file_path=output_file,
            artist=track_artist,
            album=track_album,
            year=track_year,
            title=track_title,
            disc_num=1,
            total_disc_num=1,
            track_num=track_pos,
            total_track_num=track_total
        )


def set_id3_tag(file_path, title=None, artist=None,
                album=None, genre=None,
                year=None,
                track_num=None, total_track_num=None,
                disc_num=None, total_disc_num=None):
    """
    Sets and save the ID3 Tags of a media file.

    Complete list of available tags entries:

    * album
    * bpm
    * compilation
    * composer
    * copyright
    * encodedby
    * lyricist
    * length
    * media
    * mood
    * title
    * version
    * artist
    * albumartist
    * conductor
    * arranger
    * discnumber
    * organization
    * tracknumber
    * author
    * albumartistsort
    * albumsort
    * composersort
    * artistsort
    * titlesort
    * isrc
    * discsubtitle
    * language
    * genre
    * date
    * originaldate
    * performer:*
    * musicbrainz_trackid
    * website
    * replaygain_*_gain
    * replaygain_*_peak
    * musicbrainz_artistid
    * musicbrainz_albumid
    * musicbrainz_albumartistid
    * musicbrainz_trmid
    * musicip_puid
    * musicip_fingerprint
    * musicbrainz_albumstatus
    * musicbrainz_albumtype
    * releasecountry
    * musicbrainz_discid
    * asin
    * performer
    * barcode
    * catalognumber
    * musicbrainz_releasetrackid
    * musicbrainz_releasegroupid
    * musicbrainz_workid
    * acoustid_fingerprint
    * acoustid_id

    :param file_path: location of media file
    :param title: The `title` to apply
    :param artist: The `artist` to apply
    :param album: The `album` to apply
    :param genre: The `genre` to apply
    :param year: The year to apply to the `date`
    :param track_num: The track number
    :param total_track_num: The total number of tracks
    :param disc_num: The disc number
    :param total_disc_num: The total number discs
    """
    tags = EasyID3(file_path)

    if title:
        tags['title'] = title
    if artist:
        tags['artist'] = artist
        tags['albumartist'] = artist
    if album:
        tags['album'] = album
    if genre:
        tags['genre'] = genre
    if year:
        tags['date'] = str(year)
    if total_track_num:
        if track_num:
            tags['tracknumber'] = '{}/{}'.format(track_num, total_track_num)
        else:
            tags['tracknumber'] = '/{}'.format(total_track_num)
    else:
        if track_num:
            tags['tracknumber'] = '{}'.format(track_num)
    if total_disc_num:
        if disc_num:
            tags['discnumber'] = '{}/{}'.format(disc_num, total_disc_num)
        else:
            tags['discnumber'] = '/{}'.format(total_disc_num)
    else:
        if disc_num:
            tags['discnumber'] = '{}'.format(disc_num)

    tags.save()


def create_track_data(title, extension,
                      track_pos, track_total,
                      start_time, end_time,
                      artist, album, year):
    return {
        'title': title,
        'extension': extension,
        'track': track_pos,
        'track_total': track_total,
        'start_time': start_time,
        'end_time': end_time,
        'artist': artist,
        'album': album,
        'year': year
    }


def run_split(input_file, csv_file, output_path, album_artist, album_name, album_year, dry_run):
    # Click provides validated `pathlib.Path` objects when requested; keep
    # the rest of the original behaviour the same.
    if not isinstance(input_file, pathlib.Path):
        input_file = pathlib.Path(input_file)
    if not isinstance(csv_file, pathlib.Path):
        csv_file = pathlib.Path(csv_file)
    if output_path and not isinstance(output_path, pathlib.Path):
        output_path = pathlib.Path(output_path)

    if str(input_file).startswith('~'):
        input_file = pathlib.Path('{0}{1}'.format(input_file.home(),
                                                  str(input_file)[1:]))

    if str(csv_file).startswith('~'):
        csv_file = pathlib.Path('{0}{1}'.format(csv_file.home(),
                                                str(csv_file)[1:]))

    if not output_path:
        output_path = input_file.parent
    else:
        if str(output_path).startswith('~'):
            output_path = pathlib.Path('{0}{1}'.format(output_path.home(),
                                                       str(output_path)[1:]))

    print()
    print('- Input:   ', input_file)
    print('- CSV:     ', csv_file)
    print('- Output:  ', output_path)

    audio_type = input_file.suffix[1:].lower()
    audio_file = AudioSegment.from_file(str(input_file), audio_type)

    audio_out_type = AUDIO_OUT_CONVERSION[audio_type] \
        if audio_type in AUDIO_OUT_CONVERSION else audio_type

    seconds = audio_file.duration_seconds
    file_duration = timedelta(seconds=seconds)
    print('- Duration:', file_duration)
    print()

    start_time = ''
    total_tracks = -1

    with open(csv_file) as file:
        lines = file.readlines()
        for line in lines:
            total_tracks = (total_tracks + 1) \
                if not line.isspace() else total_tracks
        file.seek(0)

        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)

        reader = csv.DictReader(file, dialect=dialect)
        first_row = True
        track_count = 0

        for row in reader:
            track_position = row['position']

            sep_count = track_position.count(':')
            has_milliseconds = (track_position.count('.') > 0)
            time_format = TIME_FORMATS[sep_count][has_milliseconds]
            new_start_time = datetime.strptime(track_position, time_format)

            if not first_row:
                track_count += 1
                if dry_run:
                    print("Simulation: Processing row ({0}) "
                          "with track position ({1})".format(track_title,
                                                             track_position))

                end_time = new_start_time
                track_data = create_track_data(
                    track_title,
                    audio_out_type,
                    track_count,
                    total_tracks,
                    start_time,
                    end_time,
                    row['artist'] if 'artist' in row else album_artist,
                    row['album'] if 'album' in row else album_name,
                    row['year'] if 'year' in row else album_year
                )
                split_audio(track_data, audio_file, output_path, dry_run)

            track_title = row['title']
            start_time = new_start_time
            first_row = False

    if not first_row:
        if dry_run:
            print("Simulation: Processing row ({0}) "
                  "with track position ({1})".format(track_title,
                                                     track_position))
        end_time = datetime.strptime(str(file_duration), '%H:%M:%S.%f')

        track_data = create_track_data(
            track_title,
            audio_out_type,
            (track_count + 1),
            total_tracks,
            start_time,
            end_time,
            row['artist'] if 'artist' in row else album_artist,
            row['album'] if 'album' in row else album_name,
            row['year'] if 'year' in row else album_year
        )

        split_audio(track_data, audio_file, output_path, dry_run)


@click.command()
@click.option('-i', '--input', 'input_file', required=True,
              type=click.Path(exists=True, path_type=pathlib.Path),
              help='Audio file to be split into tracks')
@click.option('-c', '--csv', 'csv_file', required=True,
              type=click.Path(exists=True, path_type=pathlib.Path),
              help='CSV delimited text file containing the track names and time position in the source audio file')
@click.option('-o', '--output', 'output_path', required=False,
              type=click.Path(path_type=pathlib.Path),
              help='Output path where split tracks are to be saved')
@click.option('-r', '--artist', 'album_artist', required=False,
              help='Music artist')
@click.option('-a', '--album', 'album_name', required=False,
              help='Album title')
@click.option('-y', '--year', 'album_year', type=int, required=False,
              help='Album year of release')
@click.option('-d', '--dryrun', 'dry_run', is_flag=True, default=False,
              help='Perform a dry run without processing')
def main(input_file, csv_file, output_path, album_artist, album_name, album_year, dry_run):
    run_split(input_file, csv_file, output_path, album_artist, album_name, album_year, dry_run)


if __name__ == "__main__":
    main()
