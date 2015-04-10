import config

# Song
class Song(object):
    def __init__(self, id):
        self._id = id

    def id(self):
        return self._id

# Album
class Album(object):
    def __init__(self, id, name, artist, arturl=config.DEFAULT_ALBUM, trackscnt=0, liked=None, ispandora=True):
        # main parameters
        self._id, self._name, self._artist = id, name, artist
        # additional parameters
        self._arturl, self._trackscnt, self._liked = arturl, trackscnt, liked
        # if album is pandora
        self._ispandora = ispandora
        # songs
        self._songs = []

    def id(self):
        return self._id

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def artist(self):
        return self._artist

    def setArtist(self, artist):
        self._artist = artist

    def arturl(self):
        return self._arturl

    def trackscnt(self):
        return self._trackscnt

    def liked(self):
        return self._liked

    def update(self, id, arturl, trackscnt, liked, ispandora=True):
        self._id = id
        self._arturl = self._arturl if arturl is None else arturl
        self._trackscnt, self._liked = trackscnt, liked
        # set is pandora flag
        self._ispandora = ispandora

    def setLiked(self, liked):
        self._liked = liked

    def setId(self, id):
        self._id = id

    def addSong(self, song):
        self._songs.append(song)

    def setSongs(self, songs):
        self._songs = songs

    def songs(self):
        return self._songs

    def ispandora(self):
        return self._ispandora

    def json(self):
        return {
            "id": self.id(),
            "name": self.name(),
            "artist": self.artist(),
            "arturl": self.arturl(),
            "liked": self.liked(),
            "trackscnt": self.trackscnt(),
            "ispandora": self.ispandora()
        }
