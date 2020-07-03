import pickle
import pathlib
import sys


class Artist:
    def __init__(self, artist):
        self.name = artist['name']
        self.genres = artist['genres']
        self.popularity = artist['popularity']
        self.followers = artist['followers']['total']
        self.albums = []
        self.tracks = []


class Album:
    def __init__(self, album):
        self.type = album['album_type']
        self.genres = album['genres']
        self.name = album['name']
        self.popularity = album['popularity']
        self.release_date = album['release_date']
        self.total_tracks = album['total_tracks']
        self.artists = [artist['id'] for artist in album['artists']]
        self.tracks = []

    def fillin_artists(self, artists):
        self.artists = [artists[artist_id] for artist_id in self.artists]
        for artist in self.artists:
            artist.albums.append(self)


class Bar:
    def __init__(self, bar):
        self.start = bar['start']
        self.duration = bar['duration']
        self.confidence = bar['confidence']


class Beat:
    def __init__(self, beat):
        self.start = beat['start']
        self.duration = beat['duration']
        self.confidence = beat['confidence']


class Tatum:
    def __init__(self, tatum):
        self.start = tatum['start']
        self.duration = tatum['duration']
        self.confidence = tatum['confidence']


class Section:
    def __init__(self, section):
        self.start = section['start']
        self.duration = section['duration']
        self.confidence = section['confidence']
        self.loudness = section['loudness']
        self.tempo = section['tempo']
        self.tempo_confidence = section['tempo_confidence']
        self.key = section['key']
        self.key_confidence = section['key_confidence']
        self.mode = section['mode']
        self.mode_confidence = section['mode_confidence']
        self.time_signature = section['time_signature']
        self.time_signature_confidence = section['time_signature_confidence']


class Segment:
    def __init__(self, segment):
        self.start = segment['start']
        self.duration = segment['duration']
        self.confidence = segment['confidence']
        self.loudness_start = segment['loudness_start']
        self.loudness_max_time = segment['loudness_max_time']
        self.loudness_max = segment['loudness_max']
        self.pitches = segment['pitches']
        self.timbre = segment['timbre']


class CodeString:
    def __init__(self, value, version):
        self.value = value
        self.version = version


class EchoPrintString:
    def __init__(self, value, version):
        self.value = value
        self.version = version


class SynchString:
    def __init__(self, value, version):
        self.value = value
        self.version = version


class RhythmString:
    def __init__(self, value, version):
        self.value = value
        self.version = version


class Analysis:
    def __init__(self, analysis):
        self.num_samples = analysis['track']['num_samples']
        self.duration = analysis['track']['duration']
        self.offset_seconds = analysis['track']['offset_seconds']
        self.window_seconds = analysis['track']['window_seconds']
        self.analysis_sample_rate = analysis['track']['analysis_sample_rate']
        self.analysis_channels = analysis['track']['analysis_channels']
        self.end_of_fade_in = analysis['track']['end_of_fade_in']
        self.start_of_fade_out = analysis['track']['start_of_fade_out']
        self.loudness = analysis['track']['loudness']
        self.tempo = analysis['track']['tempo']
        self.tempo_confidence = analysis['track']['tempo_confidence']
        self.time_signature = analysis['track']['time_signature']
        self.time_signature_confidence = analysis['track']['time_signature_confidence']
        self.key = analysis['track']['key']
        self.key_confidence = analysis['track']['key_confidence']
        self.mode = analysis['track']['mode']
        self.mode_confidence = analysis['track']['mode_confidence']
        self.codestring = CodeString(analysis['track']['codestring'], analysis['track']['code_version'])
        self.echoprintstring = EchoPrintString(analysis['track']['echoprintstring'], analysis['track']['echoprint_version'])
        self.samples = SynchString(analysis['track']['synchstring'], analysis['track']['synch_version'])
        self.samples = RhythmString(analysis['track']['rhythmstring'], analysis['track']['rhythm_version'])
        self.bars = [Bar(bar) for bar in analysis['bars']]
        self.beats = [Beat(beat) for beat in analysis['beats']]
        self.tatums = [Tatum(tatum) for tatum in analysis['tatums']]
        self.sections = [Section(section) for section in analysis['sections']]
        self.segments = [Segment(segment) for segment in analysis['segments']]


class Track:
    def __init__(self, track):
        self.name = track['name']
        self.duration = track['duration_ms']
        self.popularity = track['popularity']
        self.artists = [artist['id'] for artist in track['artists']]
        self.album = track['album']['id']
        self.explicit = track['explicit']
        self.number = track['track_number']
        self.danceability = track['features'][0]['danceability']
        self.energy = track['features'][0]['energy']
        self.key = track['features'][0]['key']
        self.loudness = track['features'][0]['loudness']
        self.mode = track['features'][0]['mode']
        self.speechiness = track['features'][0]['speechiness']
        self.acousticness = track['features'][0]['acousticness']
        self.instrumentalness = track['features'][0]['instrumentalness']
        self.liveness = track['features'][0]['liveness']
        self.valence = track['features'][0]['valence']
        self.tempo = track['features'][0]['tempo']
        self.time_signature = track['features'][0]['time_signature']
        self.analysis = track['id']

    def fillin_artists(self, artists):
        self.artists = [artists[artist_id] for artist_id in self.artists]
        for artist in self.artists:
            artist.tracks.append(self)

    def fillin_album(self, albums):
        self.album = albums[self.album]
        self.album.tracks.append(self)

    def fillin_analysis(self, trackinfo_dir):
        path = pathlib.Path(trackinfo_dir) / pathlib.Path(self.analysis)
        with path.open('rb') as infile:
            self.analysis = pickle.load(infile)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage:', sys.argv[0], 'INPUT_FILE OUTPUT_FILE [TRACKINFO_DIR]')
        exit(1)
    infilepath = sys.argv[1]
    outfilepath = sys.argv[2]
    with open(infilepath, 'rb') as infile:
        profile = pickle.load(infile)
    artists = {artist['id']: artist for artist in profile[0]}
    albums = {album['id']: album for album in profile[1]}
    tracks = {track['id']: track for track in profile[2]}
    artists = {id: Artist(artist) for id, artist in artists.items()}
    albums = {id: Album(album) for id, album in albums.items()}
    tracks = {id: Track(track) for id, track in tracks.items()}
    for album in albums.values():
        album.fillin_artists(artists)
    for track in tracks.values():
        track.fillin_artists(artists)
        track.fillin_album(albums)
    if len(sys.argv) >= 4:
        trackinfo_dir = sys.argv[3]
        for track in tracks.values():
            track.fillin_analysis(trackinfo_dir)
    artists = list(artists.values())
    albums = list(albums.values())
    tracks = [tracks[track['id']] for track in profile[2]]
    profile = None
    with open(outfilepath, 'wb') as outfile:
        pickle.dump((artists, albums, tracks), outfile)
