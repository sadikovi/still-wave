from types import DictType
import config
import local.scripts.requests as req
import local.scripts.misc as misc
import local.scripts.db as database

class Manager(object):
    def __init__(self):
        self.db = database.DB(database.r)

    def searchAlbum(self, query):
        if len(query) == 0:
            return {"status": "success", "code": 200, "data": []}
        else:
            res = req.searchAlbum(query)
            if res["status"] == "success":
                data = res["data"]["results"]
                # create albums and jsonobj
                albums = data["albummatches"]["album"] if "album" in data["albummatches"] else []
                albums = [albums] if type(albums) is DictType else albums
                jsonobj = []
                for _i, album in enumerate(albums):
                    images = album["image"]
                    arturl = images[-1]["#text"] if len(images) > 0 else config.DEFAULT_ALBUM
                    obj = {
                        "id": album["id"],
                        "name": album["name"],
                        "artist": album["artist"],
                        "arturl": arturl
                    }
                    jsonobj.append(obj)
                res["data"] = jsonobj
            return res

    def exists(self, userid, artist, album):
        # result
        res = {"status": "", "code": -1, "data": {}}
        try:
            # look up album id in database
            albumid = self.db.lookupAlbumId(album, artist)
            if albumid is None:
                print "Loading from Pandora: %s - %s" %(album, artist)
                raw = req.loadAlbumInfo(artist, album)
                if raw["status"] == "success":
                    if len(raw["data"]) == 0:
                        raise StandardError("Album not found")
                    explorer = raw["data"]["albumExplorer"]
                    # remove weird last Data_track from album
                    tracks = [x for x in explorer["tracks"] if x["@songTitle"] != "Data_track"]
                    # extract album id
                    albumid = misc.getSharUrlId(explorer["@shareUrl"])
                    info = {
                        "id": albumid,
                        "artist": explorer["@artistName"],
                        "album": explorer["@albumTitle"],
                        "arturl": explorer["@albumArtUrl"],
                        "tracks": len(tracks)
                    }
                    # store info in database
                    self.db.addAlbumInfo(albumid, info)
                    self.db.setAlbumLookup(albumid, album, artist)
                    for song in tracks:
                        songid = misc.getSharUrlId(song["@shareUrl"])
                        self.db.addSongToAlbum(albumid, songid)
                    # consolidate data and return
                    like = self.db.userLikesAlbum(userid, albumid)
                    raw["data"] = {"albumid": albumid, "exists": True, "likedByUser": like}
                # reassign updated raw to res
                res = raw
            else:
                print "Loading from Redis: %s - %s" %(album, artist)
                like = self.db.userLikesAlbum(userid, albumid)
                [res["status"], res["code"]] = ["success", 200]
                res["data"] = {"albumid": albumid, "exists": True, "likedByUser": like}
        except ValueError as e:
            # TODO: log error
            [res["status"], res["code"], res["msg"]] = ["error", 400, str(e)]
        finally:
            return res

    def like(self, userid, albumid):
        # like album
        res = {"status": "", "code": -1, "data": {}}
        try:
            self.db.likeAlbum(userid, albumid)
            [res["status"], res["code"], res["data"]] = ["success", 200, True]
        except BaseException as e:
            # TODO: log error
            [res["status"], res["code"], res["msg"]] = ["error", 400, str(e)]
        finally:
            return res

    def dislike(self, userid, albumid):
        # dislike album
        # like album
        res = {"status": "", "code": -1, "data": {}}
        try:
            self.db.dislikeAlbum(userid, albumid)
            [res["status"], res["code"], res["data"]] = ["success", 200, True]
        except BaseException as e:
            # TODO: log error
            [res["status"], res["code"], res["msg"]] = ["error", 400, str(e)]
        finally:
            return res
