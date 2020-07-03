import pickle
import spotipy
import spotipy.util as util
import pathlib
import sys


def get_toptracks(sp, tracklimit):
    toptracks = []
    offset = 0
    result = None
    while not result or len(result['items']) == tracklimit:
        result = sp.current_user_top_tracks(offset=offset, limit=tracklimit, time_range='long_term')
        toptracks.extend(result['items'])
        print('Got top tracks', offset+1, '-', offset+len(result['items']))
        offset += len(result['items'])
    return toptracks


def get_savedtracks(sp, tracklimit):
    savedtracks = []
    offset = 0
    result = None
    while not result or len(result['items']) == tracklimit:
        result = sp.current_user_saved_tracks(offset=offset, limit=tracklimit)
        for item in result['items']:
            if 'track' in item:
                savedtracks.append(item['track'])
            else:
                savedtracks.append(item)
        print('Got saved tracks', offset+1, '-', offset+len(result['items']))
        offset += len(result['items'])
    return savedtracks


def order_savedtracks(savedtracks, toptracks):
    savedtracks = {track['id']: track for track in savedtracks}
    tracks = []
    for track in toptracks:
        id = track['id']
        if id in savedtracks:
            tracks.append(track)
            del savedtracks[id]
    tracks.extend(savedtracks.values())
    return tracks


def get_albumids(tracks):
    return list({track['album']['id'] for track in tracks})


def get_albums(sp, albumids, albumlimit):
    albums = []
    offset = 0
    result = None
    while not result or len(albums) < len(albumids):
        result = sp.albums(albumids[offset:offset+albumlimit])
        albums.extend(result['albums'])
        print('Got albums', offset+1, '-', offset+len(result['albums']))
        offset += albumlimit
    return albums


def get_artistids(tracks, albums):
    artistids = set()
    for track in tracks:
        artistids.update([artist['id'] for artist in track['artists']])
    for album in albums:
        artistids.update([artist['id'] for artist in album['artists']])
    return list(artistids)


def get_artists(sp, artistids, artistlimit):
    artists = []
    offset = 0
    result = None
    while not result or len(artists) < len(artistids):
        result = sp.artists(artistids[offset:offset+artistlimit])
        artists.extend(result['artists'])
        print('Got artists', offset+1, '-', offset+len(result['artists']))
        offset += artistlimit
    return artists


def fillin_features(sp, tracks):
    for track in tracks:
        id = track['id']
        track['features'] = sp.audio_features(id)
        print('Got features for track', track['name'])


def download_analyses(sp, tracks, trackinfo_dir):
    trackinfo_dir = pathlib.Path(trackinfo_dir)
    if not trackinfo_dir.exists():
        trackinfo_dir.mkdir()
    for track in tracks:
        id = track['id']
        path = trackinfo_dir / pathlib.Path(id)
        if not path.exists():
            with path.open('wb') as outfile:
                pickle.dump(sp.audio_analysis(id), outfile)
            print('Got analysis for track', track['name'])


def get_profile(client_id, client_secret, username, trackinfo_dir=None):
    scope = 'user-library-read playlist-read-private user-follow-read user-top-read'
    redirect_uri = 'http://localhost:8888/callback/'
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    if token:
        sp = spotipy.Spotify(auth=token)
        toptracks = get_toptracks(sp, 50)
        savedtracks = get_savedtracks(sp, 50)
        tracks = order_savedtracks(savedtracks, toptracks)
        albumids = get_albumids(tracks)
        albums = get_albums(sp, albumids, 20)
        artistids = get_artistids(tracks, albums)
        artists = get_artists(sp, artistids, 50)
        fillin_features(sp, tracks)
        if trackinfo_dir:
            download_analyses(sp, tracks, trackinfo_dir)
        return (artists, albums, tracks)
    return None


CONFIG_FILENAME = '.analyzify'


if __name__ == '__main__':
    try:
        with open(CONFIG_FILENAME, 'r') as config:
            client_id = config.readline().strip()
            client_secret = config.readline().strip()
    except:
        print('Create a file in the current working directory named', CONFIG_FILENAME, 'with the following format:')
        print('<YOUR_SPOTIFY_API_CLIENT_ID>')
        print('<YOUR_SPOTIFY_API_CLIENT_SECRET>')
        exit(1)
    if len(sys.argv) < 3:
        print('usage:', sys.argv[0], 'USERNAME OUTFILE [TRACKINFO_DIR]')
        exit(1)
    if len(sys.argv) >= 4:
        trackinfo_dir = sys.argv[3]
    else:
        trackinfo_dir = None
    username = sys.argv[1]
    outfilename = sys.argv[2]
    profile = get_profile(client_id, client_secret, username, trackinfo_dir)
    with open(outfilename, 'wb') as outfile:
        pickle.dump(profile, outfile)
