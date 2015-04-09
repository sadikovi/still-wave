#!/usr/bin/env python

# import global
import redis
# import local
import config

pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DATABASE)
r = redis.Redis(connection_pool=pool)
# test connection, it will raise error, if connection is refused
r.ping()

class DB(object):
    def __init__(self, _redis):
        self._redis = _redis

    # like album
    def likeAlbum(self, _userid_, albumid):
        # remove song (if exists) from disliked and add it to liked
        # create hashkeys
        dislikedKey, likedKey = [_userid_+":disliked", _userid_+":liked"]
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.srem(dislikedKey, albumid).sadd(likedKey, albumid).execute()

    # dislike album
    def dislikeAlbum(self, _userid_, albumid):
        # remove song (if exists) from liked and add it to dislked
        # create hashkeys
        dislikedKey, likedKey = [_userid_+":disliked", _userid_+":liked"]
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.srem(likedKey, albumid).sadd(dislikedKey, albumid).execute()

    # reset album, so it is not in liked, nor disliked
    def resetAlbum(self, _userid_, albumid):
        # create hashkeys
        dislikedKey, likedKey = [_userid_+":disliked", _userid_+":liked"]
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.srem(likedKey, albumid).srem(dislikedKey, albumid).execute()

    # check if user likes album
    def userLikesAlbum(self, _userid_, albumid):
        # create hashkeys
        dislikedKey, likedKey = [_userid_+":disliked", _userid_+":liked"]
        like = self._redis.sismember(likedKey, albumid)
        print _userid_, albumid, like
        dislike = self._redis.sismember(dislikedKey, albumid)
        # user likes or dislikes, if album is not in the sets, returns None
        if like:
            return True
        elif dislike:
            return False
        else:
            return None

    # add song to album
    def addSongToAlbum(self, albumid, songid):
        albumKey = albumid+":songs"
        pipe = self._redis.pipeline()
        pipe.sadd(albumKey, songid).execute()

    # add list of similar songs
    def addSimilarSongs(self, songid, similarSongs):
        # add list of similar songs
        similarSongKey = songid+":similar"
        # prepare pipeline
        pipe = self._redis.pipeline()
        for similar in similarSongs:
            pipe.sadd(similarSongKey, similar)
        pipe.execute()

    # ALBUM INFO
    def addAlbumInfo(self, albumid, info):
        # adds album info
        albuminfoKey = albumid+":albuminfo"
        pipe = self._redis.pipeline()
        pipe.hmset(albuminfoKey, info).execute()

    def getAlbumInfo(self, albumid):
        albuminfoKey = albumid+":albuminfo"
        return self._redis.hgetall(albuminfoKey)

    # ALBUM LOOKUP
    def setAlbumLookup(self, albumid, album, artist):
        hashKey = "%s###%s:lookup" %(album.lower(), artist.lower())
        pipe = self._redis.pipeline()
        pipe.set(hashKey, albumid).execute()

    def lookupAlbumId(self, album, artist):
        hashKey = "%s###%s:lookup" %(album.lower(), artist.lower())
        return self._redis.get(hashKey)
