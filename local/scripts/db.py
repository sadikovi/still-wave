#!/usr/bin/env python

# import global
import redis
# import local
import config
from local.scripts.music import Album, Song
import local.scripts.misc as misc
from local.scripts.hashkeylib import LikeKey, DislikeKey, SongsForAlbumKey, AlbumForSongKey, SimilarKey, LookupKey, AlbumInfoKey

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


    ############################################################
    # Like, dislike and reset albumid
    ############################################################

    def actionByAlbum(self, _userid_, albumid, action):
        pipe = self._redis.pipeline()
        likedKey, dislikedKey = LikeKey(_userid_).key(), DislikeKey(_userid_).key()
        if action == "like":
            pipe.srem(dislikedKey, albumid).sadd(likedKey, albumid)
        elif action == "dislike":
            pipe.srem(likedKey, albumid).sadd(dislikedKey, albumid)
        else:
            pipe.srem(likedKey, albumid).srem(dislikedKey, albumid)
        pipe.execute()

    # like album
    def likeAlbum(self, _userid_, albumid):
        self.actionByAlbum(_userid_, albumid, "like")

    # dislike album
    def dislikeAlbum(self, _userid_, albumid):
        self.actionByAlbum(_userid_, albumid, "dislike")

    # reset album, so it is not in liked, nor disliked
    def resetAlbum(self, _userid_, albumid):
        self.actionByAlbum(_userid_, albumid, "reset")

    def getLikedAlbumIds(self, _userid_):
        likedKey = LikeKey(_userid_).key()
        return self._redis.smembers(likedKey)

    def getDislikedAlbumIds(self, _userid_):
        dislikedKey = DislikeKey(_userid_).key()
        return self._redis.smembers(dislikedKey)

    # check if user likes album
    def userLikesAlbum(self, _userid_, albumid):
        # create hashkeys
        likedKey, dislikedKey = LikeKey(_userid_).key(), DislikeKey(_userid_).key()
        like = self._redis.sismember(likedKey, albumid)
        dislike = self._redis.sismember(dislikedKey, albumid)
        # user likes or dislikes, if album is not in the sets, returns None
        if like:
            return True
        elif dislike:
            return False
        else:
            return None

    # adds userid to albumid
    def actionUserByAlbum(self, albumid, _userid_, action):
        pipe = self._redis.pipeline()
        # using the same keys, but instead of userid, we pass albumid
        likedKey, dislikedKey = LikeKey(albumid).key(), DislikeKey(albumid).key()
        if action == "like":
            pipe.srem(dislikedKey, _userid_).sadd(likedKey, _userid_)
        elif action == "dislike":
            pipe.srem(likedKey, _userid_).sadd(dislikedKey, _userid_)
        else:
            pipe.srem(likedKey, _userid_).srem(dislikedKey, _userid_)
        pipe.execute()

    def likeUserByAlbum(self, albumid, _userid_):
        self.actionUserByAlbum(albumid, _userid_, "like")

    def dislikeUserByAlbum(self, albumid, _userid_):
        self.actionUserByAlbum(albumid, _userid_, "dislike")

    def resetUserByAlbum(self, albumid, _userid_):
        self.actionUserByAlbum(albumid, _userid_, "reset")

    def usersLikingAlbum(self, albumid):
        likedKey = LikeKey(albumid).key()
        return self._redis.smembers(likedKey)

    def usersDislikingAlbum(self, albumid):
        dislikedKey = DislikeKey(albumid).key()
        return self._redis.smembers(dislikedKey)


    ############################################################
    # Lookup, adding and getting album
    ############################################################

    def lookupAlbum(self, name, artist):
        lookupKey = LookupKey(name, artist).key()
        return self._redis.get(lookupKey)

    def addLookup(self, albumid, name, artist):
        lookupKey = LookupKey(name, artist).key()
        pipe = self._redis.pipeline()
        pipe.set(lookupKey, albumid).execute()

    # get album as Album instance
    def getAlbum(self, albumid):
        album = None
        key = AlbumInfoKey(albumid).key()
        if albumid and self._redis.exists(key):
            info = self._redis.hgetall(key)
            album = Album(
                info["id"],
                info["name"],
                info["artist"],
                info["arturl"],
                int(info["trackscnt"]),
                liked=None,
                ispandora=misc.toBool(info["ispandora"])
            )
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
        key = AlbumInfoKey(album.id()).key()
        pipe = self._redis.pipeline()
        pipe.hmset(key, info).execute()
        # add songs
        for song in album.songs():
            self.addSongToAlbum(album.id(), song.id())


    ############################################################
    # Adding and getting songs for album
    ############################################################

    # add song to album
    def addSongToAlbum(self, albumid, songid):
        albumKey = SongsForAlbumKey(albumid).key()
        songKey = AlbumForSongKey(songid).key()
        pipe = self._redis.pipeline()
        pipe.sadd(albumKey, songid).set(songKey, albumid).execute()

    def getSongsForAlbum(self, albumid):
        albumKey = SongsForAlbumKey(albumid).key()
        return self._redis.smembers(albumKey)

    def getAlbumForSong(self, songid):
        songKey = AlbumForSongKey(songid).key()
        return self._redis.get(songKey)

    # add list of similar songs
    def addSimilarSongs(self, songid, similarSongs):
        # add list of similar songs
        similarKey = SimilarKey(songid).key()
        # prepare pipeline
        pipe = self._redis.pipeline()
        pipe.sadd(similarKey, "")
        for similar in similarSongs:
            pipe.sadd(similarKey, similar) if similar else None
        pipe.execute()

    def getSimilarSongs(self, songid):
        similarKey = SimilarKey(songid).key()
        if self._redis.exists(similarKey):
            return self._redis.smembers(similarKey)
        return None
