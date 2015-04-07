class Song(object):
    def __init__(self, _id, _albumid):
        self.id = _id
        self.albumid = _albumid
        self.similar = set()
