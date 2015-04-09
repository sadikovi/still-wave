#!/usr/bin/env python

import urllib2
import urllib
import local.scripts.misc as misc

def sendGet(url, params):
    url = url+"?"+urllib.urlencode(params.items(), True) if params else url
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as httperror:
        return {
            "status": "error",
            "msg": httperror.reason,
            "code": httperror.code
        }
    except urllib2.URLError as urlerror:
        print urlerror
        return {
            "status": "error",
            "msg": urlerror.reason,
            "code": 500
        }
    except BaseException as e:
        return {
            "status": "error",
            "msg": "Fatal: %s" %(str(e)),
            "code": 500
        }
    else:
        return {"status": "success", "code": 200, "data": response.read()}

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
    if res["status"] == "success":
        obj = misc.toJson(res["data"])
        res["data"] = obj
    return res

def loadAlbumInfo(artist, album):
    # TODO: escape artist and album
    [artist, album] = [urllib2.quote(artist), urllib2.quote(album)]
    pandoraUrl = "http://pandora.com/json/music/album/"+artist+"/"+album
    params = {"explicit": "false"}
    res = sendGet(pandoraUrl, params)
    if res["status"] == "success":
        obj = misc.toJson(res["data"])
        res["data"] = obj
    return res

def loadAlbumById(albumid):
    pandoraUrl = "http://pandora.com/json/music/album/"+albumid
    params = {"explicit": "false"}
    res = sendGet(pandoraUrl, params)
    if res["status"] == "success":
        obj = misc.toJson(res["data"])
        res["data"] = obj
    return res

def loadSongById(songid):
    pandoraUrl = "http://pandora.com/json/music/song/"+songid
    params = {"explicit": "false"}
    res = sendGet(pandoraUrl, params)
    if res["status"] == "success":
        obj = misc.toJson(res["data"])
        res["data"] = obj
    return res
