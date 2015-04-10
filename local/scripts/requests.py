#!/usr/bin/env python

import urllib2
import urllib
import local.scripts.misc as misc
from local.scripts.result import Error, Success

def sendGet(url, params):
    url = url+"?"+urllib.urlencode(params.items(), True) if params else url
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

def loadAlbumInfo(album, artist):
    # TODO: escape artist and album
    artist, album = urllib2.quote(artist), urllib2.quote(album)
    pandoraUrl = "http://pandora.com/json/music/album/"+artist+"/"+album
    params = {"explicit": "false"}
    res = sendGet(pandoraUrl, params)
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

def loadSongById(songid):
    pandoraUrl = "http://pandora.com/json/music/song/"+songid
    params = {"explicit": "false"}
    res = sendGet(pandoraUrl, params)
    if type(res) is Success:
        res.setData(misc.toJson(res.data()))
    return res
