import local.scripts.misc as misc
import local.scripts.db as database
from local.scripts.music import Album, Song
import local.scripts.requests as req
from local.scripts.manager import Manager
from local.scripts.result import Error, Success


class CollaborationEngine(object):
    def __init__(self, db=database.r):
        self._maxresults = 7
        self.db = database.DB(db)
        self.manager = Manager(db)


    def similarUsers(self, _userid_):
        liked = self.db.getLikedAlbumIds(_userid_)
        users = set([userid for albumid in liked for userid in self.db.usersLikingAlbum(albumid)])
        return users

    def similarityIndex(self, firstUser, secondUser):
        # liked albums
        fl = self.db.getLikedAlbumIds(firstUser)
        sl = self.db.getLikedAlbumIds(secondUser)
        # disliked albums
        fd = self.db.getDislikedAlbumIds(firstUser)
        sd = self.db.getDislikedAlbumIds(secondUser)
        # compute similarity index
        return round((len(fl&sl) + len(fd&sd) - len(fl&sd) - len(sl&fd))*1.0 / len(fl|sl|fd|sd), 2)

    def possibleItems(self, likedItems, similarUsers, limit=-1):
        # -1 limit means unlimited selection
        limit = limit if limit > 0 else -1
        items = set()
        for user in similarUsers:
            # calculate difference between items other user likes and liked items
            diff = self.db.getLikedAlbumIds(user) - likedItems
            for x in diff:
                if limit > 0 and len(items) >= limit:
                    return items
                items.add(x)
        return items

    def possibilityToLike(self, _userid_, albumid):
        likeUsers = self.db.usersLikingAlbum(albumid)
        dislikeUsers = self.db.usersDislikingAlbum(albumid)
        likeIndex, dislikeIndex = 0, 0
        # like similarity index
        for user in likeUsers:
            likeIndex += self.similarityIndex(_userid_, user)
        # dislike similarity index
        for user in dislikeUsers:
            dislikeIndex += self.similarityIndex(_userid_, user)
        return round((likeIndex-dislikeIndex)*1.0 / (len(likeUsers)+len(dislikeUsers)), 2)

    def recommendations(self, _userid_, limit):
        similar = self.similarUsers(_userid_)
        liked = self.db.getLikedAlbumIds(_userid_)
        # get possible items with limit
        items = self.possibleItems(liked, similar, limit)
        ratings = []
        for item in items:
            s = self.possibilityToLike(_userid_, item)
            # append only positive rating
            if s > 0:
                ratings.append({"rating": s, "item": self.db.getAlbum(item).json()})
        return ratings

    def recommendationsForUser(self, _userid_):
        try:
            ratings = self.recommendations(_userid_, self._maxresults)
            return Success(ratings)
        except BaseException as e:
            print "[!] Error during recommendations filtering: %s" %(str(e))
            return Error(500, str(e))
