#!/usr/bin/env python

# import libs
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import json
# import local
import projectpaths
import config
import local.scripts.requests as req
import local.scripts.misc as misc
import local.scripts.db as db


class SearchApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            jsonobj = {"status": "error", "msg": "Not authenticated", "code": 401}
            self.response.set_status(401)
            self.response.out.write(json.dumps(jsonobj))
        else:
            query = misc.unquoteParam(self.request.get("q"))
            if not query:
                jsonobj = {"status": "error", "msg": "Query is empty or undefined", "code": 400}
                self.response.set_status(400)
                self.response.out.write(json.dumps(jsonobj))
            else:
                res = req.searchAlbum(query)
                if res["status"] == "success":
                    data = res["data"]["results"]
                    albums = data["albummatches"]["album"]
                    jsonobj = []
                    for _i, album in enumerate(albums):
                        images = album["image"]
                        arturl = images[-1]["#text"] if images else config.DEFAULT_ALBUM
                        obj = {
                            "id": album["id"],
                            "name": album["name"],
                            "artist": album["artist"],
                            "arturl": arturl
                        }
                        jsonobj.append(obj)
                    # send json object
                    self.response.set_status(200)
                    self.response.out.write(json.dumps({"status": "success", "code": 200, "data": jsonobj}))
                else:
                    self.response.set_status(res["code"])
                    self.response.out.write(json.dumps(res))

class ExistsApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            jsonobj = {"status": "error", "msg": "Not authenticated", "code": 401}
            self.response.set_status(401)
            self.response.out.write(json.dumps(jsonobj))
        else:
            artist = misc.unquoteParam(self.request.get("artist"))
            album = misc.unquoteParam(self.request.get("album"))
            # check against our database
            try:
                albumid = db.lookupAlbumId(album, artist)
            except BaseException as e:
                self.response.set_status(400)
                self.response.out.write(json.dumps({"status": "error", "msg": str(e), "code": 400}))
            else:
                try:
                    if albumid is None:
                        print "Load from Pandora"
                        raw = req.loadAlbumInfo(artist, album)
                        if raw["status"] == "error":
                            self.response.set_status(400)
                            self.response.out.write(json.dumps({"status": "error", "code": 400, "data": None}))
                        else:
                            explorer = raw["data"]["albumExplorer"]
                            # extract album id
                            albumid = misc.getSharUrlId(explorer["@shareUrl"])
                            info = {
                                "id": albumid,
                                "artist": explorer["@artistName"],
                                "album": explorer["@albumTitle"],
                                "arturl": explorer["@albumArtUrl"]
                            }
                            # add to our database
                            db.setAlbumLookup(albumid, album, artist)
                            db.addAlbumInfo(albumid, info)
                            # add all songs to song-album store
                            for song in explorer["tracks"]:
                                songid = misc.getSharUrlId(song["@shareUrl"])
                                db.setAlbumForSong(songid, albumid)
                            # return 200 response
                            self.response.set_status(200)
                            self.response.out.write(json.dumps({"status": "success", "code": 200, "data": info}))
                    else:
                        print "load from redis"
                        info = db.getAlbumInfo(albumid)
                        self.response.set_status(200)
                        self.response.out.write(json.dumps({"status": "success", "code": 200, "data": info}))
                except BaseException as be:
                    self.response.set_status(400)
                    self.response.out.write(json.dumps({"status": "error", "code": 400, "data": str(be)}))

class LikeApi(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Like")

class DislikeApi(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Dislike")

class WrongApi(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Wrong API call")


application = webapp2.WSGIApplication([
    ('/api/search', SearchApi),
    ('/api/exists', ExistsApi),
    ('/api/like', LikeApi),
    ('/api/dislike', DislikeApi),
    ('/api/.*', WrongApi)
], debug=True)
