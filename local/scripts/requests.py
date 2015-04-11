#!/usr/bin/env python

import urllib2
import urllib
import local.scripts.misc as misc
from local.scripts.result import Error, Success

def sendGet(url, params):
    url = url+"?"+urllib.urlencode(params.items()) if params else url
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as httperror:
        return Error(httperror.code, httperror.reason)
    except urllib2.URLError as urlerror:
        return Error(500, urlerror.reason)
    except BaseException as e:
        return Error(500, "Fatal: %s" %(str(e)))
    else:
        return Success(response.read())

def searchAlbum(query, page, limit):
    lastfmUrl = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "album.search",
        "album": query,
        "page": page,
        "api_key": "c6023aeb55b72d170f999dd3461369e4",
        "format": "json",
        "limit": limit
    }
    res = sendGet(lastfmUrl, params)
    if type(res) is Success:
        res.setData(misc.toJson(res.data()))
    return res

def loadAlbumInfo(album, artist, ispandora=True):
    albumurl, params = None, None
    if ispandora:
        albumurl = "http://pandora.com/json/music/album/"+urllib2.quote(artist)+"/"+urllib2.quote(album)
        params = {"explicit": "false"}
    else:
        albumurl = "http://ws.audioscrobbler.com/2.0/"
        params = {
            "method": "album.getinfo",
            "api_key": "c6023aeb55b72d170f999dd3461369e4",
            "artist": artist,
            "album": album,
            "format": "json"
        }
    res = sendGet(albumurl, params)
    if type(res) is Success:
        res.setData(misc.toJson(res.data()))
    return res

def loadAlbumById(albumid):
    pandoraUrl = "http://pandora.com/json/music/album/"+albumid
    params = {"explicit": "false"}
    res = sendGet(pandoraUrl, params)
    if type(res) is Success:
        res.setData(misc.toJson(res.data()))
    return res

def loadSongById(songid, ispandora=True):
    songurl, params = None, None
    if ispandora:
        songurl = "http://pandora.com/json/music/song/"+songid
        params = {"explicit": "false"}
    else:
        songurl = "http://ws.audioscrobbler.com/2.0/"
        params = {
            "method": "track.getsimilar",
            "mbid": songid,
            "api_key": "c6023aeb55b72d170f999dd3461369e4",
            "format": "json"
        }
    res = sendGet(songurl, params)
    if type(res) is Success:
        res.setData(misc.toJson(res.data()))
    return res
