#!/usr/bin/env python

# import global
import redis
# import local
import config
from local.scripts.music import Album, Song
import local.scripts.misc as misc

pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DATABASE)
r = redis.Redis(connection_pool=pool)

class DB(object):
    def __init__(self, _redis):
        self._redis = _redis

    def ping(self):
        # test connection, it will raise error, if connection is refused
        try:
            self._redis.ping()
        except:
            return False
        else:
            return True

    # like album
    def likeAlbum(self, _userid_, albumid):
        # remove song (if exists) from disliked and add it to liked
        dislikedKey, likedKey = _userid_+":disliked", _userid_+":liked"
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.srem(dislikedKey, albumid).sadd(likedKey, albumid).execute()

    def getLikedAlbumIds(self, _userid_):
        likedKey = _userid_+":liked"
        return self._redis.smembers(likedKey)

    def getDislikedAlbumIds(self, _userid_):
        dislikedKey = _userid_+":disliked"
        return self._redis.smembers(dislikedKey)

    # dislike album
    def dislikeAlbum(self, _userid_, albumid):
        # remove song (if exists) from liked and add it to dislked
        dislikedKey, likedKey = _userid_+":disliked", _userid_+":liked"
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.srem(likedKey, albumid).sadd(dislikedKey, albumid).execute()

    # reset album, so it is not in liked, nor disliked
    def resetAlbum(self, _userid_, albumid):
        # create hashkeys
        dislikedKey, likedKey = _userid_+":disliked", _userid_+":liked"
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.srem(likedKey, albumid).srem(dislikedKey, albumid).execute()

    # check if user likes album
    def userLikesAlbum(self, _userid_, albumid):
        # create hashkeys
        dislikedKey, likedKey = _userid_+":disliked", _userid_+":liked"
        like = self._redis.sismember(likedKey, albumid)
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
        albumKey = "%s:songs" %(albumid)
        songKey = "%s:albumforsong" %(songid)
        pipe = self._redis.pipeline()
        pipe.sadd(albumKey, songid).set(songKey, albumid).execute()

    def getSongsForAlbum(self, albumid):
        albumKey = "%s:songs" %(albumid)
        return self._redis.smembers(albumKey)

    def getAlbumForSong(self, songid):
        songKey = "%s:albumforsong" %(songid)
        return self._redis.get(songKey)

    # add list of similar songs
    def addSimilarSongs(self, songid, similarSongs):
        # add list of similar songs
        similarSongKey = songid+":similar"
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.sadd(similarSongKey, "")
        for similar in similarSongs:
            if similar:
                pipe.sadd(similarSongKey, similar)
        pipe.execute()

    def getSimilarSongs(self, songid):
        similarSongKey = songid+":similar"
        if self._redis.exists(similarSongKey):
            return self._redis.smembers(similarSongKey)
        return None

    # get album as Album instance
    def getAlbum(self, id=None, album=None):
        if not id and not album:
            return None
        albumid = id or album.id()
        if not albumid:
            # do lookup first
            lookupKey = "%s###%s:lookup" %(album.name().lower(), album.artist().lower())
            albumid = self._redis.get(lookupKey)
        # fetch album info
        key = "%s:albuminfo" %(albumid)
        info = self._redis.hgetall(key)
        if info:
            album = Album(info["id"], info["name"], info["artist"], info["arturl"],
                            int(info["trackscnt"]), liked=None,
                            ispandora=misc.toBool(info["ispandora"]))
            # get songs
            songids = list(self.getSongsForAlbum(album.id()) or [])
            for songid in songids:
                album.addSong(Song(songid))
        return album

    # add album as Album instance
    def addAlbum(self, album):
        if not album or not album.id():
            return album
        # add album to database and lookup
        info = {
            "id": album.id(),
            "name": album.name(),
            "artist": album.artist(),
            "arturl": album.arturl(),
            "trackscnt": album.trackscnt(),
            "ispandora": album.ispandora()
        }
        key = "%s:albuminfo" %(album.id())
        pipe = self._redis.pipeline()
        pipe.hmset(key, info).execute()
        # add lookup
        lookupKey = "%s###%s:lookup" %(album.name().lower(), album.artist().lower())
        pipe = self._redis.pipeline()
        pipe.set(lookupKey, album.id()).execute()
        # add songs
        for song in album.songs():
            self.addSongToAlbum(album.id(), song.id())
