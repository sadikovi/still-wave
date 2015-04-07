class User(object):
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name
        # empty sets of songs
        self.liked = set()
        self.disliked = set()
