class HashKey(object):
    def __init__(self, value):
        self._key = value

    def key(self):
        return self._key

class LikeKey(HashKey):
    def __init__(self, value):
        hashvalue = "%s:liked" % str(value)
        super(LikeKey, self).__init__(hashvalue)

class DislikeKey(HashKey):
    def __init__(self, value):
        hashvalue = "%s:disliked" % str(value)
        super(DislikeKey, self).__init__(hashvalue)

class SongsForAlbumKey(HashKey):
    def __init__(self, value):
        hashvalue = "%s:songs" % str(value)
        super(SongsForAlbumKey, self).__init__(hashvalue)

class AlbumForSongKey(HashKey):
    def __init__(self, value):
        hashvalue = "%s:albumforsong" % str(value)
        super(AlbumForSongKey, self).__init__(hashvalue)

class SimilarKey(HashKey):
    def __init__(self, value):
        hashvalue = "%s:similar" % str(value)
        super(SimilarKey, self).__init__(hashvalue)

class LookupKey(HashKey):
    def __init__(self, *args):
        value = "###".join([str(x).lower() for x in args])
        hashvalue = "%s:lookup" % str(value)
        super(LookupKey, self).__init__(hashvalue)

class AlbumInfoKey(HashKey):
    def __init__(self, value):
        hashvalue = "%s:albuminfo" % str(value)
        super(AlbumInfoKey, self).__init__(hashvalue)
