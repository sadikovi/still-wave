#!/usr/bin/env python

# import global
import redis
# import local
import config

pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DATABASE)
r = redis.Redis(connection_pool=pool)
# test connection, it will raise error, if connection is refused
r.ping()

def likeSong(userid, songid):
    # remove song (if exists) from disliked and add it to liked
    # create hashkeys
    [dislikedKey, likedKey] = ["%s:disliked" %(userid), "%s:liked" %(userid)]
    # prepare pipeline
    pipe = r.pipeline()
    pipe.srem(dislikedKey, songid).sadd(likedKey, songid).execute()

def dislikeSong(useid, songid):
    # remove song (if exists) from liked and add it to dislked
    # create hashkeys
    [dislikedKey, likedKey] = ["%s:disliked" %(useid), "%s:liked" %(useid)]
    # prepare pipeline
    pipe = r.pipeline()
    pipe.srem(likedKey, songid).sadd(dislikedKey, songid).execute()

def setAlbumForSong(songid, albumid):
    # add (or override) songid - albumid pair
    songAlbumKey = "%s:album" %(songid)
    pipe = r.pipeline()
    pipe.set(songAlbumKey, albumid).execute()

def addSimilarSongs(songid, similarSongs):
    # add list of similar songs
    similarSongKey = "%s:similar" %(songid)
    # prepare pipeline
    pipe = r.pipeline()
    for similar in similarSongs:
        pipe.sadd(similarSongKey, similar)
    pipe.execute()

# ALBUM INFO
def addAlbumInfo(albumid, info):
    # adds album info
    albuminfoKey = "%s:albuminfo" %(albumid)
    pipe = r.pipeline()
    pipe.hmset(albuminfoKey, info).execute()

def getAlbumInfo(albumid):
    albuminfoKey = "%s:albuminfo" %(albumid)
    return r.hgetall(albuminfoKey)

# ALBUM LOOKUP
def setAlbumLookup(albumid, album, artist):
    hashKey = "%s###%s:lookup" %(album.lower(), artist.lower())
    pipe = r.pipeline()
    pipe.set(hashKey, albumid).execute()

def lookupAlbumId(album, artist):
    hashKey = "%s###%s:lookup" %(album.lower(), artist.lower())
    return r.get(hashKey)
